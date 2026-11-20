import numpy as np
from smac import HyperparameterOptimizationFacade, Scenario
from sklearn import datasets
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from update_config import *
from self_DDPG.s_onceBenchmark import *
from utils import *

"""
Warning: SMAC always minimizes the value returned from the target function.
"""
# count + 3
hostname = '47.108.79.80'
port = 22
username = 'root'
password = 'yjh13896545793'
source_ini = "dm_source.ini"
target_ini = "self_DDPG/benchmarkData_self/dm.ini"
scores = []
count = 671
bench = oneBench(hostname, port, username, password, True)
invalid_score = -999999

def train(config: Configuration, seed: int = 1) -> float:
    global count
    score = float(getTpmc(config, "dm_source.ini", "self_DDPG/benchmarkData_self/dm.ini"))
    print(f"第{count}次tpmc: ", score)
    scores.append(score)
    if score != invalid_score:
        save_paras_metric(config._values, score, "record.txt")
    count += 1
    if score == invalid_score and flag == False:
        return float("inf")
    return -score

def getTpmc(config, source_ini, target_ini):
    global count
    global bench
    global flag
    # if count % 5 == 0:
    #     bench = oneBench(hostname, port, username, password, True)
    update_ini(config, source_ini, target_ini)  # 修改dm.ini文件
    dos2unix(target_ini) # 转换格式
    bench.updateAndUpload("dm.ini") # 上传dm.ini文件
    print("preparation completed, Start Benchmark\n")
    print("count:", count)
    # is_second = False if count == 1 else True
    is_second = True
    print(is_second)
    flag = False
    flag = bench.runBenchmark(1, isSecond=is_second)
    print("BenchmarkSql completed\n")

    if flag:
        tpmc = bench.get_tpmc()
        print("tpmc extracted\n")
        if tpmc is None:
            tpmc =invalid_score
            print("Failed: flag = True")
    else:
        tpmc = invalid_score
        print("Failed: flag = False")
    return tpmc

configspace = create_config_space()

# Scenario object specifying the optimization environment
scenario = Scenario(configspace, deterministic=True, n_trials=10000)

# Use SMAC to find the best configuration/hyperparameters
smac = HyperparameterOptimizationFacade(scenario, train)
incumbent = smac.optimize()

# Get cost of default configuration
# default_cost = smac.validate(configspace.get_default_configuration())
# print(f"Default cost: {default_cost}")

# # Let's calculate the cost of the incumbent
# incumbent_cost = smac.validate(incumbent)
# print(f"Incumbent cost: {incumbent_cost}")
# print(incumbent)