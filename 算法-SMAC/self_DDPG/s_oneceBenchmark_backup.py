from self_DDPG.s_BenchmarkSql import BenchmarkSql
from self_DDPG.s_SSH_test import SSH
from self_DDPG.s_get_props_dm import getPropsdm
from self_DDPG.s_extractLogData import LogProcessor
import time


class oneBench:
    def __init__(self, hostname, port, username, password, stress_test=False):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.stress_test = stress_test

        self.ssh_no_doc = SSH(hostname, port, username, password)  # 传输文件

        if stress_test:
            self.ssh_docker = SSH(hostname, port, username, password)  # 压测
            self.benchmark = BenchmarkSql(self.ssh_docker)
            print(self.benchmark.out)
            print(self.benchmark.err)
            # Start keep-alive thread for stress test SSH connection
            import threading
            keep_alive_thread = threading.Thread(target=self.ssh_docker.keep_alive)
            keep_alive_thread.daemon = True
            keep_alive_thread.start()

    def download_file(self, file_name):
        """
        可以下载 props.dm  dm.ini  benchmark.log 三个文件
        :param file_name:
        :return:
        """
        # docker_files = {"props.dm": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/props.dm",
        #                 "dm.ini": "/opt/dmdbms/data/DAMENG/dm.ini",
        #                 "benchmark.log": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/benchmark.log"}

        server_files = {"props.dm": "/home/dmdba/benchmarksql-5.0/run/props.dm",
                        "dm.ini": "/dmdata/data/DAMENG/dm.ini",
                        "benchmark.log": "/home/dmdba/benchmarksql-5.0/run/benchmark.log"}

        local_files = {"props.dm": "self_DDPG/benchmarkData_self/props.dm",
                       "dm.ini": "self_DDPG/benchmarkData_self/dm.ini",
                       "benchmark.log": "self_DDPG/benchmarkData_self/benchmark.log"}
        time.sleep(5)
        self.ssh_no_doc.download_file(server_files[file_name], local_files[file_name])
        print("download file from docker to local done")

    def updateAndUpload(self, file_name):
        """
        更新 props.dm dm.ini 文件
        在更新之前会自动下载最新的文件
        :param file_name:
        :return:
        """
        # docker_files = {"props.dm": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/props.dm",
        #                 "dm.ini": "/opt/dmdbms/data/DAMENG/dm.ini"}

        server_files = {"props.dm": "/home/dmdba/benchmarksql-5.0/run/props.dm",
                        "dm.ini": "/dmdata/data/DAMENG/dm.ini"}

        local_files = {"props.dm": "self_DDPG/benchmarkData_self/props.dm",
                       "dm.ini": "self_DDPG/benchmarkData_self/dm.ini"}

        # 上传文件
        self.ssh_no_doc.upload_file(local_files[file_name], server_files[file_name])
        # self.ssh_no_doc.transfer_file_inServer_toDocker(server_files[file_name], docker_files[file_name], True)

    def runBenchmark(self, runmins="1", isSecond=True):

        # 重启服务器
        commands = []
        commands.append("/home/dmdba/dmdbms/bin/DmServiceDAMENG restart")  # 重启数据库服务，最多10s
        self.benchmark.init_commands(commands)
        output, error = self.benchmark.pressure_measurement(runtime_s=45)
        # print(output, error)

        status = self.benchmark.ssh.ssh_execute_command(command="/home/dmdba/dmdbms/bin/DmServiceDAMENG status", timeout=5, runningFlag=True)
        print(status)
        # commands = []
        # commands.append("/opt/dmdbms/bin/DmService status") # 判断状态，因为内存分配过大启动不了
        # self.benchmark.init_commands(commands)
        # output = []
        # output, error = self.benchmark.pressure_measurement(runtime_s=30)
        if status:
        
            # 进入目录
            self.benchmark.ssh.ssh_execute_command(command="cd /home/dmdba/benchmarksql-5.0/run", timeout=5)

            if not isSecond:
                # 建表 -- 加载 -- 创建索引
                self.benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props1.dm ../sqlCreateTable.sql", timeout=10)
                output = self.benchmark.ssh.ssh_execute_command(command="./runLoader.sh ./props.dm", timeout=7 * 60)
                print("load output: ", output)
                self.benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props.dm ../sqlCreateIndex.sql", timeout=40)
                print("Load completed")

            commands = []
            commands.append("./runBenchmark.sh ./props.dm > benchmark.log 2>&1")
            self.benchmark.init_commands(commands)
            self.benchmark.pressure_measurement(runtime_s=int(runmins) * 60 + 5)
            print("{}分钟的压力测试执行完成".format(runmins))
            return True
        return False

    def get_tpmc(self):
        """
        自动下载 benchmark.log
        返回 tpmc。 如果需要返回其他值，只需要在 return 处增加即可。
        :return:
        """
        local_log = "self_DDPG/benchmarkData_self/benchmark.log"
        local_log_save = "self_DDPG/benchmarkData_self/extracted_log_data.txt"
        
        self.download_file("benchmark.log")

        log_manager = LogProcessor()
        log_str = log_manager.read_log_data_toStr(local_log, 10)
        log_dict = log_manager.extract_log_data_toDict(log_str)
        log_manager.save_log_data_toJson(local_log_save, log_dict)
        print(log_dict["Measured_tpmC_NewOrders"])
        return log_dict["Measured_tpmC_NewOrders"]

    def benchClose(self):
        if not self.stress_test:
            self.ssh_docker.ssh_close()

        self.ssh_no_doc.ssh_close()
        print("关闭执行完成\n")


if __name__ == "__main__":

    hostname = '47.108.79.80'
    port = 22
    username = 'root'
    password = 'yjh13896545793'

    bench = oneBench(hostname, port, username, password, True)
    
