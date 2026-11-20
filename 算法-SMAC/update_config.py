import os
import shutil
from ConfigSpace import Configuration, ConfigurationSpace
from ConfigSpace.hyperparameters import UniformFloatHyperparameter, UniformIntegerHyperparameter, CategoricalHyperparameter


config = {"MEMORY_POOL":600,
          "KEEP": 23}

# 更新参数
def update_ini(config:Configuration, source_file_path, target_file_path, dict_write=False, dic={"MEMORY_POOL":600}):
    shutil.copy(source_file_path, target_file_path)
    if not dict_write:
        with open(target_file_path, "a", encoding="utf-8") as file:
            for key, value in config._values.items():
                # print((key, value))
                file.write(f"{key}={value}\n")
    else:
        with open(target_file_path, "a", encoding="utf-8") as file:
            for key, value in dic.items():
                # print((key, value))
                file.write(f"{key}={value}\n")

def save_paras_metric(paras: dict, metric, file_path: str):
    """
    保存参数和度量到指定文件。

    :param paras: 参数字典。
    :param metric: 度量值。
    :param file_path: 文件路径。
    """
    # 将参数字典中的值转换为字符串，并用制表符连接
    values = '\t'.join(str(value) for value in paras.values())
    
    # 以追加模式打开文件，并将参数和值写入文件
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(values + "\t" + str(metric) + "\n")
    
    print("Save completed")

# 将windows文件转换为linux文件的形式
def dos2unix(file_path, new_file_path=None):
    """
    将Windows文本文件转换为Linux适用的文件。

    :param file_path: 输入文件路径
    :param new_file_path: 输出文件路径（可选），默认为覆盖原文件
    """
    if new_file_path is None:
        new_file_path = file_path

    with open(file_path, 'rb') as file:
        content = file.read()

    # 替换回车符，并确保使用换行符
    content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    with open(new_file_path, 'wb') as file:
        file.write(content)

def create_config_space():
    configspace = ConfigurationSpace()
    # 添加超参数
    configspace.add_hyperparameter(UniformIntegerHyperparameter('MEMORY_POOL', 450, 5001, default_value=500))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MEMORY_N_POOLS', 0, 50, default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('MEMORY_TARGET', 14000, 20000, default_value=15000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('MEMORY_EXTENT_SIZE', 1, 10, default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HUGE_MEMORY_PERCENTAGE', 45, 100, default_value=50))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HUGE_BUFFER', 80, 500, default_value=80))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HUGE_BUFFER_POOLS', 3, 512, default_value=4))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('BUFFER', 8192, 11001, default_value=8192))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('BUFFER_POOLS', 15, 512, default_value=19))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('FAST_POOL_PAGES', 2800, 4000, default_value=3000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('FAST_ROLL_PAGES', 800, 2000, default_value=1000))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('KEEP', 8, 500, default_value=8))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('RECYCLE', 8, 500, default_value=300))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('RECYCLE_POOLS', 15, 100, default_value=19))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MULTI_PAGE_GET_NUM', 1, 32, default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('SORT_FLAG', [0, 1, 2, 3], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('SORT_ADAPTIVE_FLAG', [0, 1, 2, 3], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('SORT_BUF_SIZE', 1000, 1500, default_value=1000))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SORT_BUF_GLOBAL_SIZE', 10000, 20000, default_value=10000))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SORT_BLK_SIZE', 20, 50, default_value=20))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('HAGR_HASH_SIZE', 80000, 300000, default_value=100000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HJ_BUF_GLOBAL_SIZE', 4800, 50000, default_value=5000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HJ_BUF_SIZE', 800, 5000, default_value=1000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HAGR_BUF_GLOBAL_SIZE', 4800, 10000, default_value=5000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HAGR_BUF_SIZE', 480, 1000, default_value=500))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HAGR_BLK_SIZE', 1, 50, default_value=2))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MTAB_MEM_SIZE', 1, 50, default_value=8))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('FTAB_MEM_SIZE', 0, 100, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MMT_SIZE', 0, 10, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MMT_GLOBAL_SIZE', 3800, 5000, default_value=4000))
    # configspace.add_hyperparameter(CategoricalHyperparameter('MMT_FLAG', [1, 2], default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('DICT_BUF_SIZE', 48, 200, default_value=50))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('HFS_CACHE_SIZE', 160, 500, default_value=160))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('VM_STACK_SIZE', 64, 1024, default_value=256))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('VM_POOL_SIZE', 32, 1024, default_value=64))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('VM_POOL_TARGET', 10240, 20480, default_value=16384))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('SESS_POOL_SIZE', 32, 1048576, default_value=64))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('SESS_POOL_TARGET', 10240, 10485760, default_value=16384))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('RT_HEAP_TARGET', 8192, 16384, default_value=8192))
    configspace.add_hyperparameter(CategoricalHyperparameter('VM_MEM_HEAP', [0, 1, 2], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('HAGR_DISTINCT_HASH_TABLE_SIZE', 10000, 20000, default_value=10000))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('CNNTB_HASH_TABLE_SIZE', 100, 2000, default_value=100))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('GLOBAL_RTREE_BUF_SIZE', 80, 500, default_value=100))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SINGLE_RTREE_BUF_SIZE', 0, 50, default_value=10))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SORT_OPT_SIZE', 0, 20, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('TSORT_OPT', [0, 1], default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('WORKER_THREADS', 1, 64, default_value=32))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TASK_THREADS', 1, 64, default_value=16))
    # configspace.add_hyperparameter(CategoricalHyperparameter('FAST_RW_LOCK', [0, 1, 2], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SPIN_TIME', 0, 4000, default_value=4000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('WORK_THRD_STACK_SIZE', 1024, 16384, default_value=8192))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('WORK_THRD_RESERVE_SIZE', 200, 300, default_value=200))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('WORKER_CPU_PERCENT', 0, 0.4, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('RS_BDTA_FLAG',[0, 2], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('RS_BDTA_BUF_SIZE', 8, 500, default_value=32))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MAX_OPT_N_TABLES', 3, 8, default_value=6))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MAX_N_GRP_PUSH_DOWN', 1, 100, default_value=5))
    # configspace.add_hyperparameter(CategoricalHyperparameter('CTE_OPT_FLAG', [0, 1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('BATCH_PARAM_OPT', [0, 1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('CLT_CONST_TO_PARAM', [0, 1], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('LIKE_OPT_FLAG', 0, 127, default_value=127))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('FILTER_PUSH_DOWN', 0, 15, default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('UPD_DEL_OPT', [0, 2], default_value=2))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('ENABLE_DIST_IN_SUBQUERY_OPT', 0, 7, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_HAGR_FLAG', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('DTABLE_PULLUP_FLAG', [0, 1], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('VIEW_PULLUP_FLAG', 0, 63, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('VIEW_PULLUP_MAX_TAB', 1, 16, default_value=7))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('GROUP_OPT_FLAG', 0, 63, default_value=4))
    # configspace.add_hyperparameter(CategoricalHyperparameter('FROM_OPT_FLAG', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('REFED_EXISTS_OPT_FLAG', [0,1,2,3], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('REFED_OPS_SUBQUERY_OPT_FLAG', 0, 7, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MAX_PHC_BE_NUM', 512, 5000, default_value=512))
    # configspace.add_hyperparameter(CategoricalHyperparameter('PARTIAL_JOIN_EVALUATION_FLAG', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_FK_REMOVE_TABLES_FLAG', [0, 1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_FJ_REMOVE_TABLE_FLAG', [0, 1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_HTAB', [0,1], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SEL_ITEM_HTAB_FLAG', 0, 15, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OR_CVT_HTAB_FLAG', [0,1,2], default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CASE_WHEN_CVT_IFUN', 0, 15, default_value=9))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OR_NBEXP_CVT_CASE_WHEN_FLAG',[0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('NONCONST_OR_CVT_IN_LST_FLAG',[0,1], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('OUTER_CVT_INNER_PULL_UP_COND_FLAG', [1,2,3], default_value=3))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OPT_OR_FOR_HUGE_TABLE_FLAG', [0, 1], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SUBQ_CVT_SPL_FLAG', 0, 31, default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_RQ_TO_SPL', [0, 1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('MULTI_IN_CVT_EXISTS', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('PRJT_REPLACE_NPAR', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_RQ_TO_INV',[0,1,2], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('SUBQ_EXP_CVT_FLAG', 0, 255, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_REFER_TAB_ONLY', [0, 1], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('REFED_SUBQ_CROSS_FLAG', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('IN_LIST_AS_JOIN_KEY', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OUTER_JOIN_INDEX_OPT_FLAG', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OUTER_JOIN_FLATING_FLAG', [0,1], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TOP_ORDER_OPT_FLAG', 0,15, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TOP_ORDER_ESTIMATE_CARD', 0, 5000, default_value=300))
    # configspace.add_hyperparameter(CategoricalHyperparameter('TOP_DIS_HASH_FLAG', [0,1,2], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('ENABLE_RQ_TO_NONREF_SPL',0,7, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('ENABLE_CHOOSE_BY_ESTIMATE_FLAG', 0,7, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OPTIMIZER_MODE', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('NEW_MOTION', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('LDIS_NEW_FOLD_FUN', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('DYNAMIC_CALC_NODES', [0,1], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('OPTIMIZER_MAX_PERM', 1, 20000, default_value=7200))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_INDEX_FILTER', [0,1,2], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('OPTIMIZER_DYNAMIC_SAMPLING', 0,12, default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('NONREFED_SUBQUERY_AS_CONST', [0,1], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('HASH_CMP_OPT_FLAG', 0,15, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('OUTER_OPT_NLO_FLAG', 0, 7, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('DISTINCT_USE_INDEX_SKIP',[0, 1, 2], default_value=2))
    # configspace.add_hyperparameter(CategoricalHyperparameter('USE_INDEX_SKIP_SCAN', [0,1,2], default_value=0))
    configspace.add_hyperparameter(UniformFloatHyperparameter('INDEX_SKIP_SCAN_RATE', 0, 1, default_value=0.0025))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('SPEED_SEMI_JOIN_PLAN', 0, 31, default_value=9))
    configspace.add_hyperparameter(CategoricalHyperparameter('COMPLEX_VIEW_MERGING', [0,1,2], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OP_SUBQ_CVT_IN_FLAG', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENHANCED_SUBQ_MERGING', [0,1,2,3], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('HLSM_FLAG', [1,2,3], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('DEL_HP_OPT_FLAG', 0, 31, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('OPTIMIZER_OR_NBEXP', 0, 31, default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('CNNTB_OPT_FLAG', 0, 255, default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('ADAPTIVE_NPLN_FLAG',[0,1,2,3], default_value=3))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('NBEXP_OPT_FLAG', 0, 7, default_value=7))
    # configspace.add_hyperparameter(CategoricalHyperparameter('HAGR_HASH_ALGORITHM_FLAG', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('DIST_HASH_ALGORITHM_FLAG', [0,1], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('VIEW_FILTER_MERGING', 0, 511, default_value=138))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_JOIN_FACTORIZATION',[0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_PARTITION_WISE_OPT',[0,1], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HASH_PLL_OPT_FLAG', 0, 63, default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('PLACE_GROUP_BY_FLAG', [0,1,2,3], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_NEST_LOOP_JOIN_CACHE', [0,1,2,3], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('VIEW_OPT_FLAG', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_ADJUST_NLI_COST', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_ADJUST_DIST_COST', [0,1,2], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_RLOG_SIZE', 0, 1000, default_value=128))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_DIRTY_PAGES', 0, 100, default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_INTERVAL', 0, 1000, default_value=180))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_FLUSH_RATE', 0, 100.00, default_value=5))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_FLUSH_PAGES', 1000, 5000, default_value=1000))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CKPT_WAIT_PAGES', 1, 10240, default_value=1024))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('FORCE_FLUSH_PAGES', 0, 1000, default_value=8))
    configspace.add_hyperparameter(CategoricalHyperparameter('DIRECT_IO', [0,1,2], default_value=0)) # Log
    configspace.add_hyperparameter(UniformIntegerHyperparameter('IO_THR_GROUPS', 1, 64, default_value=8))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('HIO_THR_GROUPS', 1, 64, default_value=2))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('TRX_VIEW_SIZE', 16, 16384, default_value=512))
    # configspace.add_hyperparameter(CategoricalHyperparameter('TRX_VIEW_MODE', [0,1], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TRX_CMTARR_SIZE', 3, 11, default_value=10))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('BDTA_SIZE', 1, 5000, default_value=300))
    # configspace.add_hyperparameter(CategoricalHyperparameter('OLAP_FLAG', [0,1,2 ], default_value=2))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('JOIN_HASH_SIZE', 450000, 5200000, default_value=500000))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TEMP_SIZE', 10, 500, default_value=10))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('CACHE_POOL_SIZE', 80, 1000, default_value=100))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('PLN_DICT_HASH_THRESHOLD', 15, 100, default_value=20))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('STAT_COLLECT_SIZE', 8000, 20000, default_value=10000))
    # configspace.add_hyperparameter(CategoricalHyperparameter('STAT_ALL', [0,1,2,3,4], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('PHC_MODE_ENFORCE', 0, 15, default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_HASH_JOIN', [0,1], default_value=1))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_INDEX_JOIN', [0,1], default_value=1))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_MERGE_JOIN', [0,1], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('MAX_PARALLEL_DEGREE', 0, 128, default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('PARALLEL_POLICY', [0,1,2], default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('PARALLEL_THRD_NUM', 1, 100, default_value=10))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('PARALLEL_MODE_COMMON_DEGREE', 1, 100, default_value=1))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('PUSH_SUBQ', 0, 7, default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('OPTIMIZER_AGGR_GROUPBY_ELIM', [0,1], default_value=1))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('ENABLE_IN_VALUE_LIST_OPT', 0, 15, default_value=6))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENHANCED_BEXP_TRANS_GEN',[0,1,2,3], default_value=3))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('FIRST_ROWS', 90, 500, default_value=100))
    # configspace.add_hyperparameter(CategoricalHyperparameter('HFINS_PARALLEL_FLAG', [0,1,2], default_value=0))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('HFINS_MAX_THRD_NUM', 4, 200, default_value=100))
    configspace.add_hyperparameter(CategoricalHyperparameter('BTR_SPLIT_MODE', [0,1], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('DECIMAL_FIX_STORAGE', [0,1], default_value=0))
    # configspace.add_hyperparameter(CategoricalHyperparameter('TMP_DEL_OPT', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('STAT_OPT_FLAG', [0,1], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('RLOG_BUF_SIZE', [2,4,8,16,32,64,128,256,1024,2048,4096,8192,16384], default_value=1024))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('RLOG_POOL_SIZE', 1, 2048, default_value=256))
    configspace.add_hyperparameter(CategoricalHyperparameter('RLOG_PARALLEL_ENABLE', [0,1,2], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('FAST_RELEASE_SLOCK', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('LOCK_TID_MODE', [0,1], default_value=1))
    # configspace.add_hyperparameter(CategoricalHyperparameter('LOCK_TID_UPGRADE', [0,1], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('NOWAIT_WHEN_UNIQUE_CONFLICT', [0,1], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('UNDO_EXTENT_NUM', 3, 1024, default_value=4))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('UNDO_RETENTION', 0, 1000, default_value=90))
    configspace.add_hyperparameter(CategoricalHyperparameter('PARALLEL_PURGE_FLAG', [0,1], default_value=0))
    configspace.add_hyperparameter(UniformIntegerHyperparameter('PURGE_WAIT_TIME', 0, 1000, default_value=500))
    configspace.add_hyperparameter(CategoricalHyperparameter('PSEG_RECV', [0,1,2,3], default_value=3))
    configspace.add_hyperparameter(CategoricalHyperparameter('LOCK_DICT_OPT', [0,1,2], default_value=2))
    # configspace.add_hyperparameter(UniformIntegerHyperparameter('TRX_DICT_LOCK_NUM', 1, 1024, default_value=64))
    # configspace.add_hyperparameter(CategoricalHyperparameter('FINS_LOCK_MODE', [0,1,2], default_value=1))
    configspace.add_hyperparameter(CategoricalHyperparameter('MSG_COMPRESS_TYPE', [0,1,2], default_value=2))
    configspace.add_hyperparameter(CategoricalHyperparameter('COMM_VALIDATE', [0,1,2], default_value=1))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_MONITOR', [0,1], default_value=1))
    configspace.add_hyperparameter(CategoricalHyperparameter('ENABLE_FREQROOTS', [0,1,2,3], default_value=0))
    configspace.add_hyperparameter(CategoricalHyperparameter('PURGE_DEL_OPT', [0,1,2], default_value=0))
    # configspace.add_hyperparameter(UniformFloatHyperparameter('SEL_RATE_EQU', 0, 1, default_value=0))
    # configspace.add_hyperparameter(UniformFloatHyperparameter('SEL_RATE_SINGLE', 0, 1, default_value=0))

    return configspace


if __name__ == "__main__":
    source_file_path = "dm_source.ini"
    target_file_path = "dm.ini"
    # 复制源文件到目标文件
    shutil.copy(source_file_path, target_file_path)

    update_ini(config, target_file_path)

    print(f"字典内容已成功追加到文件 {target_file_path}。")
{"a":1, "b":1, "c":1}