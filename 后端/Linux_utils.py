# -*- coding: utf-8 -*-

import subprocess
import re
import time

NETWORK_ERROR_MSG = "网络通信异常"

def excuteLinux(command, cwd=None, is_dmdba_excute=False):
    # dmdba_prefix = 'su - dmdba -c "'
    # if is_dmdba_excute:
    #     command = dmdba_prefix + command + '"'
    # print("command:", command)
    process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        output, error = process.communicate(timeout=610)  # 设置超时时间为600秒
    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()

    print("output:", output)
    print("-------------------")
    print("error:", error)
    print("\n***********\n")
    return output, error

# 更新参数
def updateIni(config):
     excuteLinux("cp -f /dmdata/data/dm.ini.bk /dmdata/data/DAMENG/dm.ini", is_dmdba_excute=True)
     with open("/dmdata/data/DAMENG/dm.ini", "a", encoding="utf-8") as file:
         for key, value in config._values.items():
            # print((key, value))
            file.write(f"{key}={value}\n")

def extractRunMins():
    output, error = excuteLinux("cat /home/dmdba/benchmarksql-5.0/run/props.dm", is_dmdba_excute=True)
    # 使用正则表达式查找runMins后的数字
    match = re.search(r'runMins\s*=\s*(\d+)', output)
    if match:
        return int(match.group(1))  # 提取数字并转换为整数
    else:
        return None  # 如果未找到返回None


def killProcess():
    """
    训练以及普通模式，停止掉上一个达梦数据库服务的进程
    """

    def findPid(output):
        # 使用正则表达式匹配 'pid ' 后面的数字
        if "is running" in output:
            match = re.search(r'pid (\d+)', output)
            if match:
                return int(match.group(1))
        else:
            return None

    excuteLinux(command="rm -rf /home/dmdba/dmdbms/bin/pids/DmServiceDAMENG.pid", is_dmdba_excute=True)

    # 查询pid 
    output, _ = excuteLinux(command="/home/dmdba/dmdbms/bin/DmServiceDAMENG status", is_dmdba_excute=True)

    # 获取pid
    pid = findPid(output)

    if pid is not None:
        # kill pid
        excuteLinux(command="kill -9 " + str(pid))

    pid = None
    # 重启数据库
    while pid is None:
        # 重启数据库
        excuteLinux("/home/dmdba/dmdbms/bin/DmServiceDAMENG restart", is_dmdba_excute=True)

        # 查看重启成功没有
        output, _ = excuteLinux(command="/home/dmdba/dmdbms/bin/DmServiceDAMENG status", is_dmdba_excute=True)
        pid = findPid(output)
    print(pid)

    print("")
    return pid



def runBenchMark_SMAC(defaukt_run_time=10):
    
    """训练模式的压测"""
    # 重启服务器
    commands = []
    
    # 重启数据库服务 (包括杀掉原来的数据库进程，再重启)
    pid = killProcess() 
    output = None

    if pid is not None:
        output, _ = excuteLinux("cd /home/dmdba/benchmarksql-5.0/run/ && ./runBenchmark.sh ./props.dm", is_dmdba_excute=True)
        count = 1
        while NETWORK_ERROR_MSG in output:
            output, _ = excuteLinux("cd /home/dmdba/benchmarksql-5.0/run/ && ./runBenchmark.sh ./props.dm", is_dmdba_excute=True)
            count += 1
            if count >= 10: return False, output
        print("压力测试执行完成")
        return True, output
    return False, output


def getTpmc(output):
    # 使用正则表达式匹配 'Measured tpmC (NewOrders)' 后面的值
    match = re.search(r'Measured tpmC \(NewOrders\) = ([\d.]+)', output)
    if match:
        return float(match.group(1))
    else:
        return None

if __name__ == "__main__":
    _, output = runBenchMark_SMAC()

    tpmc = getTpmc(output)

    print(tpmc)