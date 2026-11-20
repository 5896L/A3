# -*- coding: utf-8 -*-

from smac import HyperparameterOptimizationFacade, Scenario
from smac import Callback
from smac.runhistory import TrialInfo, TrialValue
from smac.main.smbo import SMBO
from Linux_utils import *
from ConfigSpace import Configuration, ConfigurationSpace
from ConfigSpace.hyperparameters import UniformFloatHyperparameter, UniformIntegerHyperparameter, CategoricalHyperparameter
import json
import numpy as np
from smac.runhistory import RunHistory
from pathlib import Path
import os
import time

from sklearn.linear_model import Lasso

# 存数据库
from dm.models import ItemPara, PropsDM
from dm.models import (TrainingConfiguration_runMin1,
                       TrainingConfiguration_runMin2,
                       TrainingConfiguration_runMin3,
                       TrainingConfiguration_runMin4,
                       TrainingConfiguration_runMin5,
                       TrainingConfiguration_runMin6,
                       TrainingConfiguration_runMin7,
                       TrainingConfiguration_runMin8,
                       TrainingConfiguration_runMin9,
                       TrainingConfiguration_runMin10)

# 自定义序列化器
# def default_serializer(obj):
#     if isinstance(obj, np.integer):
#         return int(obj)
#     if isinstance(obj, np.floating):
#         return float(obj)
#     if isinstance(obj, np.ndarray):
#         return obj.tolist()

class StopCallback(Callback):
    def __init__(self):
        self.results = []
        self.importance_value_dict = {
            'BUFFER': 8789,
            'FAST_POOL_PAGES': 6667,
            'FAST_ROLL_PAGES': 970,
            'HAGR_BUF_GLOBAL_SIZE': 786,
            'HAGR_BUF_SIZE': 125,
            'HJ_BLK_SIZE': 29,
            'HJ_BUF_GLOBAL_SIZE': 8954,
            'HUGE_BUFFER': 487,
            'MEMORY_POOL': 1356,
            'MEMORY_TARGET': 4000,
            'MVCC_RETRY_TIMES': 9,
            'RECYCLE': 366,
            'SORT_BUF_SIZE': 40,
            'WORK_THRD_RESERVE_SIZE': 259
        }

        pass


    def on_tell_end(self, smbo: SMBO, trial_info: TrialInfo, trial_value: TrialValue, **kwargs) -> bool | None:
        """Called after the stats are updated and the trial is added to the runhistory. Optionally, returns false
        to gracefully stop the optimization.
        """

        # 获取最新的配置参数和结果
        config = trial_info.config
        config_dict = dict(config)  # 将 config 转换为字典
        # config_json = json.dumps(config_dict, default=default_serializer)  # 将字典转换为 JSON 对象
        score = trial_value.cost
        # self.results.append({"config": config, "tpmc": -score})  # score为负数，所以取负

        propsdm = PropsDM.objects.using('mysql').filter(id=1).get()
        run_mins = propsdm.runMins
        # 动态获取模型类
        training_class_name = f'TrainingConfiguration_runMin{run_mins}'
        training_class = globals()[training_class_name]

        # 存数据库
        training_class.objects.using('mysql').create(
            TPMC=-score,
            RECYCLE=config_dict['RECYCLE'],
            FAST_ROLL_PAGES = config_dict['FAST_ROLL_PAGES'],
            HAGR_BUF_SIZE = config_dict['HAGR_BUF_SIZE'],
            HJ_BLK_SIZE = config_dict['HJ_BLK_SIZE'],
            HUGE_BUFFER = config_dict['HUGE_BUFFER'],
            WORK_THRD_RESERVE_SIZE = config_dict['WORK_THRD_RESERVE_SIZE'],
            BUFFER = config_dict['BUFFER'],
            SORT_BUF_SIZE = config_dict['SORT_BUF_SIZE'],
            HJ_BUF_GLOBAL_SIZE = config_dict['HJ_BUF_GLOBAL_SIZE'],
            FAST_POOL_PAGES = config_dict['FAST_POOL_PAGES'],
            MEMORY_POOL = config_dict['MEMORY_POOL'],
            MEMORY_TARGET = config_dict['MEMORY_TARGET'],
            HAGR_BUF_GLOBAL_SIZE = config_dict['HAGR_BUF_GLOBAL_SIZE'],
            MVCC_RETRY_TIMES = config_dict['MVCC_RETRY_TIMES'],
        )

        # 加一个分析参数关联性的算法
        print("\nconfiguration:\n", config_dict)
        print("\nscore:\n", score)


        item_para = ItemPara.objects.using('mysql').filter(id=1).get()
        is_stop = item_para.IS_STOPPED
        is_pause = item_para.IS_PAUSED

        print("IS_STOPPED --------------------------------->", is_stop)
        print("IS_PAUSED--------------------------------->", is_pause)

        # 加一个分析参数关联性的算法
        self.results.append({"config": config, "tpmc": -score})  # 存储配置和得分
        if len(self.results) >= 1:
            self.run_lasso()

        if is_stop == 'T':
            return False


        while is_pause == 'T':
            print("Optimization paused... waiting to resume")
            time.sleep(5)  # 每5秒检查一次是否恢复

            item_para = ItemPara.objects.using('mysql').filter(id=1).get()
            is_pause = item_para.IS_PAUSED  # 更新is_pause
            is_stop = item_para.IS_STOPPED  # 更新is_stopped

            if is_stop == 'T':
                return False

        return None

    def run_lasso(self):
        # 准备数据
        X = np.array([list(r["config"].values()) for r in self.results])  # 配置作为特征
        y = np.array([r["tpmc"] for r in self.results])  # tpmc作为目标变量

        # 执行Lasso回归
        lasso = Lasso(alpha=0.1)
        lasso.fit(X, y)

        # 输出Lasso回归得到的权重
        print("Lasso回归得到的权重:", lasso.coef_)
        importance_value = lasso.coef_
        for idx, config_name in enumerate(self.importance_value_dict.keys()):
            self.importance_value_dict[config_name] = importance_value[idx]
        print(self.importance_value_dict)
        # print(lasso.coef_)


class SMAC_DM:
    def __init__(self, n_trials):
        self.is_train = False
        self.is_pause = False
        self.create_config_space()
        self.n_trials = n_trials
        self.INVALID_SCORE = -999999
    
    def load_history(self, current_history:RunHistory):
        """
        加载以前运行过的所有记录
        """

        father_folder = "./smac3_output/" + str(self.run_mins)
        midfix = "0"
        scenario_suffix = "scenario.json"
        history_suffix = "runhistory.json"

        # 遍历父文件夹中的所有子文件夹
        child_folders = [folder for folder in os.listdir(father_folder) if os.path.isdir(os.path.join(father_folder, folder))]
        
        for child_folder in child_folders:
            # 构造路径
            child_path = Path(father_folder) / child_folder / midfix
            scenario_path = child_path
            history_path = child_path / history_suffix

            # 加载场景
            if child_path.exists():
                added_history, added_scenario, added_configspace = RunHistory(), self.smac.scenario, None
            
                added_scenario = added_scenario.load(scenario_path)
                added_configspace = added_scenario.configspace
                added_history.load(history_path, added_configspace)

                current_history.update(added_history)
                print(f"Successfully loaded history from {history_path}")
            else:
                print(f"Scenario or history file not found in {child_path}")      

        return current_history          

    
    def train(self, config: Configuration, seed: int = 1) -> float:
        score = float(self.extractTpmc(config))
        print(f"第{self.count}次tpmc: ", score)
        self.count += 1

        return -score
    
    def SMAC(self):
        self.count = 1
        self.run_mins = extractRunMins()

        # 更新Item para
        item_para = ItemPara.objects.using('mysql').filter(id=1).get()

        # 构建属性名称字符串
        attribute_name = f'Min{self.run_mins}'

        # 获取当前属性值
        current_value = getattr(item_para, attribute_name)

        # 修改属性值
        new_value = current_value + 1
        setattr(item_para, attribute_name, new_value)

        # 保存修改后的对象
        item_para.save()

        self.scenario = Scenario(self.configspace, 
                                 deterministic=True, 
                                 n_trials=self.n_trials,
                                 output_directory="smac3_output/" + str(self.run_mins) + "/")
        # Use SMAC to find the best configuration/hyperparameters
        self.smac = HyperparameterOptimizationFacade(self.scenario, 
                                                self.train,
                                                overwrite=True,
                                                callbacks=[StopCallback()],
                                                )
        
        runhistory = self.smac.runhistory
        runhistory = self.load_history(runhistory)
        print(runhistory.finished)
        # tmp_config = runhistory.get_config(1)
        # print(tmp_config)
        # print(runhistory.get_cost(tmp_config))

        incumbent = self.smac.optimize()
        
        # print("\nincubent:\n", incumbent)

    def create_config_space(self):
        self.configspace = ConfigurationSpace()
        # 添加超参数
        self.configspace.add(UniformIntegerHyperparameter('MEMORY_POOL', 1350, 1360, default_value=1352))
        # self.configspace.add(UniformIntegerHyperparameter('MVCC_RETRY_TIMES', 5, 8, default_value=5))
        # self.configspace.add(UniformIntegerHyperparameter('MEMORY_N_POOLS', 0, 50, default_value=1))
        self.configspace.add(UniformIntegerHyperparameter('MEMORY_TARGET', 4000, 4010, default_value=4003))
        # self.configspace.add(UniformIntegerHyperparameter('MEMORY_EXTENT_SIZE', 1, 10, default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('HUGE_MEMORY_PERCENTAGE', 45, 55, default_value=50))
        self.configspace.add(UniformIntegerHyperparameter('HUGE_BUFFER', 480, 490, default_value=482))
        # self.configspace.add(UniformIntegerHyperparameter('HUGE_BUFFER_POOLS', 3, 5, default_value=4))
        self.configspace.add(UniformIntegerHyperparameter('BUFFER', 8780, 8800, default_value=8784))
        # self.configspace.add(UniformIntegerHyperparameter('BUFFER_POOLS', 3, 5, default_value=19))
        self.configspace.add(UniformIntegerHyperparameter('FAST_POOL_PAGES', 6655, 6670, default_value=6659))
        self.configspace.add(UniformIntegerHyperparameter('FAST_ROLL_PAGES', 930, 1000, default_value=938))
        # self.configspace.add(UniformIntegerHyperparameter('KEEP', 8, 500, default_value=8))
        self.configspace.add(UniformIntegerHyperparameter('RECYCLE', 360, 370, default_value=366))
        # self.configspace.add(UniformIntegerHyperparameter('RECYCLE_POOLS', 3, 5, default_value=19))
        # self.configspace.add(UniformIntegerHyperparameter('MULTI_PAGE_GET_NUM', 1, 32, default_value=1))
        # self.configspace.add(CategoricalHyperparameter('SORT_FLAG', [0, 1, 2, 3], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('SORT_ADAPTIVE_FLAG', [0, 1, 2, 3], default_value=0))
        self.configspace.add(UniformIntegerHyperparameter('SORT_BUF_SIZE', 35, 43, default_value=38))
        # self.configspace.add(UniformIntegerHyperparameter('SORT_BUF_GLOBAL_SIZE', 10000, 20000, default_value=10000))
        # self.configspace.add(UniformIntegerHyperparameter('SORT_BLK_SIZE', 20, 50, default_value=20))
        # self.configspace.add(UniformIntegerHyperparameter('HAGR_HASH_SIZE', 80000, 300000, default_value=100000))
        self.configspace.add(UniformIntegerHyperparameter('HJ_BUF_GLOBAL_SIZE', 8940, 8960, default_value=8951))
        # self.configspace.add(UniformIntegerHyperparameter('HJ_BUF_SIZE', 800, 5000, default_value=1000))
        self.configspace.add(UniformIntegerHyperparameter('HAGR_BUF_GLOBAL_SIZE', 780, 790, default_value=784))
        self.configspace.add(UniformIntegerHyperparameter('HAGR_BUF_SIZE', 110, 130, default_value=120))
        self.configspace.add(UniformIntegerHyperparameter('HJ_BLK_SIZE', 28, 35, default_value=31))
        self.configspace.add(UniformIntegerHyperparameter('MVCC_RETRY_TIMES', 6, 10, default_value=8))
        # self.configspace.add(UniformIntegerHyperparameter('HAGR_BLK_SIZE', 1, 50, default_value=2))
        # self.configspace.add(UniformIntegerHyperparameter('MTAB_MEM_SIZE', 1, 50, default_value=8))
        # self.configspace.add(UniformIntegerHyperparameter('FTAB_MEM_SIZE', 0, 100, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('MMT_SIZE', 0, 10, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('MMT_GLOBAL_SIZE', 3800, 5000, default_value=4000))
        # self.configspace.add(CategoricalHyperparameter('MMT_FLAG', [1, 2], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('DICT_BUF_SIZE', 48, 200, default_value=50))
        # self.configspace.add(UniformIntegerHyperparameter('HFS_CACHE_SIZE', 160, 500, default_value=160))
        # self.configspace.add(UniformIntegerHyperparameter('VM_STACK_SIZE', 64, 1024, default_value=256))
        # self.configspace.add(UniformIntegerHyperparameter('VM_POOL_SIZE', 32, 1024, default_value=64))
        # self.configspace.add(UniformIntegerHyperparameter('VM_POOL_TARGET', 10240, 20480, default_value=16384))
        # self.configspace.add(UniformIntegerHyperparameter('SESS_POOL_SIZE', 32, 1048576, default_value=64))
        # self.configspace.add(UniformIntegerHyperparameter('SESS_POOL_TARGET', 10240, 10485760, default_value=16384))
        # self.configspace.add(UniformIntegerHyperparameter('RT_HEAP_TARGET', 8192, 16384, default_value=8192))
        # self.configspace.add(CategoricalHyperparameter('VM_MEM_HEAP', [0, 1, 2], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('HAGR_DISTINCT_HASH_TABLE_SIZE', 10000, 20000, default_value=10000))
        # self.configspace.add(UniformIntegerHyperparameter('CNNTB_HASH_TABLE_SIZE', 100, 2000, default_value=100))
        # self.configspace.add(UniformIntegerHyperparameter('GLOBAL_RTREE_BUF_SIZE', 80, 500, default_value=100))
        # self.configspace.add(UniformIntegerHyperparameter('SINGLE_RTREE_BUF_SIZE', 0, 50, default_value=10))
        # self.configspace.add(UniformIntegerHyperparameter('SORT_OPT_SIZE', 0, 20, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('TSORT_OPT', [0, 1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('WORKER_THREADS', 1, 64, default_value=32))
        # self.configspace.add(UniformIntegerHyperparameter('TASK_THREADS', 1, 64, default_value=16))
        # self.configspace.add(CategoricalHyperparameter('FAST_RW_LOCK', [0, 1, 2], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('SPIN_TIME', 0, 4000, default_value=4000))
        # self.configspace.add(UniformIntegerHyperparameter('WORK_THRD_STACK_SIZE', 1024, 16384, default_value=8192))
        self.configspace.add(UniformIntegerHyperparameter('WORK_THRD_RESERVE_SIZE', 200, 210, default_value=200))
        # self.configspace.add(UniformIntegerHyperparameter('WORKER_CPU_PERCENT', 0, 0.4, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('RS_BDTA_FLAG',[0, 2], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('RS_BDTA_BUF_SIZE', 8, 500, default_value=32))
        # self.configspace.add(UniformIntegerHyperparameter('MAX_OPT_N_TABLES', 3, 8, default_value=6))
        # self.configspace.add(UniformIntegerHyperparameter('MAX_N_GRP_PUSH_DOWN', 1, 100, default_value=5))
        # self.configspace.add(CategoricalHyperparameter('CTE_OPT_FLAG', [0, 1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('BATCH_PARAM_OPT', [0, 1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('CLT_CONST_TO_PARAM', [0, 1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('LIKE_OPT_FLAG', 0, 127, default_value=127))
        # self.configspace.add(UniformIntegerHyperparameter('FILTER_PUSH_DOWN', 0, 15, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('UPD_DEL_OPT', [0, 2], default_value=2))
        # self.configspace.add(UniformIntegerHyperparameter('ENABLE_DIST_IN_SUBQUERY_OPT', 0, 7, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('USE_HAGR_FLAG', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('DTABLE_PULLUP_FLAG', [0, 1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('VIEW_PULLUP_FLAG', 0, 63, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('VIEW_PULLUP_MAX_TAB', 1, 16, default_value=7))
        # self.configspace.add(UniformIntegerHyperparameter('GROUP_OPT_FLAG', 0, 63, default_value=4))
        # self.configspace.add(CategoricalHyperparameter('FROM_OPT_FLAG', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('REFED_EXISTS_OPT_FLAG', [0,1,2,3], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('REFED_OPS_SUBQUERY_OPT_FLAG', 0, 7, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('MAX_PHC_BE_NUM', 512, 5000, default_value=512))
        # self.configspace.add(CategoricalHyperparameter('PARTIAL_JOIN_EVALUATION_FLAG', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('USE_FK_REMOVE_TABLES_FLAG', [0, 1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('USE_FJ_REMOVE_TABLE_FLAG', [0, 1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('USE_HTAB', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('SEL_ITEM_HTAB_FLAG', 0, 15, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OR_CVT_HTAB_FLAG', [0,1,2], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('CASE_WHEN_CVT_IFUN', 0, 15, default_value=9))
        # self.configspace.add(CategoricalHyperparameter('OR_NBEXP_CVT_CASE_WHEN_FLAG',[0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('NONCONST_OR_CVT_IN_LST_FLAG',[0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OUTER_CVT_INNER_PULL_UP_COND_FLAG', [1,2,3], default_value=3))
        # self.configspace.add(CategoricalHyperparameter('OPT_OR_FOR_HUGE_TABLE_FLAG', [0, 1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('SUBQ_CVT_SPL_FLAG', 0, 31, default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_RQ_TO_SPL', [0, 1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('MULTI_IN_CVT_EXISTS', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('PRJT_REPLACE_NPAR', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_RQ_TO_INV',[0,1,2], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('SUBQ_EXP_CVT_FLAG', 0, 255, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('USE_REFER_TAB_ONLY', [0, 1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('REFED_SUBQ_CROSS_FLAG', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('IN_LIST_AS_JOIN_KEY', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OUTER_JOIN_INDEX_OPT_FLAG', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OUTER_JOIN_FLATING_FLAG', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('TOP_ORDER_OPT_FLAG', 0,15, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('TOP_ORDER_ESTIMATE_CARD', 0, 5000, default_value=300))
        # self.configspace.add(CategoricalHyperparameter('TOP_DIS_HASH_FLAG', [0,1,2], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('ENABLE_RQ_TO_NONREF_SPL',0,7, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('ENABLE_CHOOSE_BY_ESTIMATE_FLAG', 0,7, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OPTIMIZER_MODE', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('NEW_MOTION', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('LDIS_NEW_FOLD_FUN', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('DYNAMIC_CALC_NODES', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('OPTIMIZER_MAX_PERM', 1, 20000, default_value=7200))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_INDEX_FILTER', [0,1,2], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('OPTIMIZER_DYNAMIC_SAMPLING', 0,12, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('NONREFED_SUBQUERY_AS_CONST', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('HASH_CMP_OPT_FLAG', 0,15, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('OUTER_OPT_NLO_FLAG', 0, 7, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('DISTINCT_USE_INDEX_SKIP',[0, 1, 2], default_value=2))
        # self.configspace.add(CategoricalHyperparameter('USE_INDEX_SKIP_SCAN', [0,1,2], default_value=0))
        # self.configspace.add(UniformFloatHyperparameter('INDEX_SKIP_SCAN_RATE', 0, 1, default_value=0.0025))
        # self.configspace.add(UniformIntegerHyperparameter('SPEED_SEMI_JOIN_PLAN', 0, 31, default_value=9))
        # self.configspace.add(CategoricalHyperparameter('COMPLEX_VIEW_MERGING', [0,1,2], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OP_SUBQ_CVT_IN_FLAG', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENHANCED_SUBQ_MERGING', [0,1,2,3], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('HLSM_FLAG', [1,2,3], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('DEL_HP_OPT_FLAG', 0, 31, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('OPTIMIZER_OR_NBEXP', 0, 31, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('CNNTB_OPT_FLAG', 0, 255, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('ADAPTIVE_NPLN_FLAG',[0,1,2,3], default_value=3))
        # self.configspace.add(UniformIntegerHyperparameter('NBEXP_OPT_FLAG', 0, 7, default_value=7))
        # self.configspace.add(CategoricalHyperparameter('HAGR_HASH_ALGORITHM_FLAG', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('DIST_HASH_ALGORITHM_FLAG', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('VIEW_FILTER_MERGING', 0, 511, default_value=138))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_JOIN_FACTORIZATION',[0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_PARTITION_WISE_OPT',[0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('HASH_PLL_OPT_FLAG', 0, 63, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('PLACE_GROUP_BY_FLAG', [0,1,2,3], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_NEST_LOOP_JOIN_CACHE', [0,1,2,3], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('VIEW_OPT_FLAG', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_ADJUST_NLI_COST', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_ADJUST_DIST_COST', [0,1,2], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_RLOG_SIZE', 0, 1000, default_value=128))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_DIRTY_PAGES', 0, 100, default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_INTERVAL', 0, 1000, default_value=180))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_FLUSH_RATE', 0, 100.00, default_value=5))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_FLUSH_PAGES', 1000, 5000, default_value=1000))
        # self.configspace.add(UniformIntegerHyperparameter('CKPT_WAIT_PAGES', 1, 1056, default_value=1024))
        # self.configspace.add(UniformIntegerHyperparameter('FORCE_FLUSH_PAGES', 0, 12, default_value=8))
        # self.configspace.add(CategoricalHyperparameter('DIRECT_IO', [0,1,2], default_value=0)) # Log
        # self.configspace.add(UniformIntegerHyperparameter('IO_THR_GROUPS', 1, 10, default_value=8))
        # self.configspace.add(UniformIntegerHyperparameter('HIO_THR_GROUPS', 1, 10, default_value=2))
        # self.configspace.add(UniformIntegerHyperparameter('TRX_VIEW_SIZE', 16, 16384, default_value=512))
        # # self.configspace.add(CategoricalHyperparameter('TRX_VIEW_MODE', [0,1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('TRX_CMTARR_SIZE', 3, 11, default_value=10))
        # self.configspace.add(UniformIntegerHyperparameter('BDTA_SIZE', 290, 310, default_value=300))
        # self.configspace.add(CategoricalHyperparameter('OLAP_FLAG', [0,1,2 ], default_value=2))
        # self.configspace.add(UniformIntegerHyperparameter('JOIN_HASH_SIZE', 500000, 500010, default_value=500000))
        # self.configspace.add(UniformIntegerHyperparameter('TEMP_SIZE', 10, 500, default_value=10))
        # self.configspace.add(UniformIntegerHyperparameter('CACHE_POOL_SIZE', 80, 1000, default_value=100))
        # self.configspace.add(UniformIntegerHyperparameter('PLN_DICT_HASH_THRESHOLD', 15, 100, default_value=20))
        # self.configspace.add(UniformIntegerHyperparameter('STAT_COLLECT_SIZE', 8000, 20000, default_value=10000))
        # self.configspace.add(CategoricalHyperparameter('STAT_ALL', [0,1,2,3,4], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('PHC_MODE_ENFORCE', 0, 15, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_HASH_JOIN', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_INDEX_JOIN', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_MERGE_JOIN', [0,1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('MAX_PARALLEL_DEGREE', 0, 128, default_value=1))
        # self.configspace.add(CategoricalHyperparameter('PARALLEL_POLICY', [0,1,2], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('PARALLEL_THRD_NUM', 1, 100, default_value=10))
        # self.configspace.add(UniformIntegerHyperparameter('PARALLEL_MODE_COMMON_DEGREE', 1, 100, default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('PUSH_SUBQ', 0, 7, default_value=0))
        # self.configspace.add(CategoricalHyperparameter('OPTIMIZER_AGGR_GROUPBY_ELIM', [0,1], default_value=1))
        # self.configspace.add(UniformIntegerHyperparameter('ENABLE_IN_VALUE_LIST_OPT', 0, 15, default_value=6))
        # self.configspace.add(CategoricalHyperparameter('ENHANCED_BEXP_TRANS_GEN',[0,1,2,3], default_value=3))
        # self.configspace.add(UniformIntegerHyperparameter('FIRST_ROWS', 90, 500, default_value=100))
        # self.configspace.add(CategoricalHyperparameter('HFINS_PARALLEL_FLAG', [0,1,2], default_value=0))

        # self.configspace.add(CategoricalHyperparameter('TMP_DEL_OPT', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('STAT_OPT_FLAG', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('RLOG_BUF_SIZE', [2,4,8,16,32,64,128,256,1024], default_value=1024))
        # self.configspace.add(UniformIntegerHyperparameter('RLOG_POOL_SIZE', 1, 512, default_value=256))
        # self.configspace.add(CategoricalHyperparameter('RLOG_PARALLEL_ENABLE', [0,1,2], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('FAST_RELEASE_SLOCK', [0,1], default_value=1))
        # # self.configspace.add(CategoricalHyperparameter('LOCK_TID_MODE', [0,1], default_value=1))
        # # self.configspace.add(CategoricalHyperparameter('LOCK_TID_UPGRADE', [0,1], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('NOWAIT_WHEN_UNIQUE_CONFLICT', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('UNDO_EXTENT_NUM', 3, 6, default_value=4))
        # self.configspace.add(UniformIntegerHyperparameter('UNDO_RETENTION', 0, 100, default_value=90))
        # self.configspace.add(CategoricalHyperparameter('PARALLEL_PURGE_FLAG', [0,1], default_value=0))
        # self.configspace.add(UniformIntegerHyperparameter('PURGE_WAIT_TIME', 500, 510, default_value=500))
        # self.configspace.add(CategoricalHyperparameter('PSEG_RECV', [0,1,2,3], default_value=3))
        # self.configspace.add(CategoricalHyperparameter('LOCK_DICT_OPT', [0,1,2], default_value=2))
        # # self.configspace.add(UniformIntegerHyperparameter('TRX_DICT_LOCK_NUM', 1, 1024, default_value=64))
        # # self.configspace.add(CategoricalHyperparameter('FINS_LOCK_MODE', [0,1,2], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('MSG_COMPRESS_TYPE', [0,1,2], default_value=2))
        # self.configspace.add(CategoricalHyperparameter('COMM_VALIDATE', [0,1,2], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_MONITOR', [0,1], default_value=1))
        # self.configspace.add(CategoricalHyperparameter('ENABLE_FREQROOTS', [0,1,2,3], default_value=0))
        # self.configspace.add(CategoricalHyperparameter('PURGE_DEL_OPT', [0,1,2], default_value=0))
        # self.configspace.add(UniformFloatHyperparameter('SEL_RATE_EQU', 0, 1, default_value=0))
        # self.configspace.add(UniformFloatHyperparameter('SEL_RATE_SINGLE', 0, 1, default_value=0))

    def extractTpmc(self, config):
        global flag
        updateIni(config)  # 修改并上传dm.ini文件

        print("preparation completed, Start Benchmark\n")

        flag = False
        flag, output = runBenchMark_SMAC()
        print("BenchmarkSql completed\n")

        if flag:
            tpmc = getTpmc(output)
            print("tpmc extracted\n")
            if tpmc is None:
                tpmc = self.INVALID_SCORE
                print("Failed: flag = True")
        else:
            tpmc = self.INVALID_SCORE
            print("Failed: flag = False")
        return tpmc
    

if __name__ == "__main__":
    model = SMAC_DM()

    model.SMAC()

    