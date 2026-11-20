from s_BenchmarkSql import BenchmarkSql
from s_SSH_test import SSH
from s_get_props_dm import getPropsdm
from s_extractLogData import LogProcessor


class oneBench:
    def __init__(self, hostname, port, username, password, stress_test=False):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self.ssh_no_doc = SSH(hostname, port, username, password)  # 传输文件

        if stress_test:
            self.ssh_docker = SSH(hostname, port, username, password)  # 压测
            self.benchmark = BenchmarkSql(self.ssh_docker)

        print(self.benchmark.out)
        print(self.benchmark.err)

    def download_file(self, file_name):
        docker_files = {"props.dm": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/props.dm",
                        "dm.ini": "/opt/dmdbms/data/DAMENG/dm.ini",
                        "benchmark.log": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/benchmark.log"}

        server_files = {"props.dm": "/tmp1/props.dm",
                        "dm.ini": "/tmp1/dm.ini",
                        "benchmark.log": "/tmp1/benchmark.log"}

        local_files = {"props.dm": "benchmarkData_self/props.dm",
                       "dm.ini": "benchmarkData_self/dm.ini",
                       "benchmark.log": "benchmarkData_self/benchmark.log"}

        self.ssh_no_doc.transfer_file_inServer_toDocker(docker_files[file_name], server_files[file_name], False)
        self.ssh_no_doc.download_file(server_files[file_name], local_files[file_name])
        print("download file from docker to local done")

    def updateAndUpload(self, file_name, runMins="1"):
        docker_files = {"props.dm": "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/props.dm",
                        "dm.ini": "/opt/dmdbms/data/DAMENG/dm.ini"}

        server_files = {"props.dm": "/tmp1/props.dm",
                        "dm.ini": "/tmp1/dm.ini"}

        local_files = {"props.dm": "benchmarkData_self/props.dm",
                       "dm.ini": "benchmarkData_self/dm.ini"}

        # 更新文件
        if file_name == "props.dm":
            # 修改 props.dm
            deal_propsdm = getPropsdm(local_files[file_name])
            deal_propsdm.update_config_file(local_files[file_name], deal_propsdm.propsdm_dict, "runMins", runMins)


        elif file_name == "dm.ini":
            pass

        # 上传文件
        self.ssh_no_doc.upload_file(local_files[file_name], server_files[file_name])
        self.ssh_no_doc.transfer_file_inServer_toDocker(server_files[file_name], docker_files[file_name], True)

    def runBenchmark(self, runmins="1", isFirst=True):

        # 重启服务器
        commands = []
        commands.append("/opt/dmdbms/bin/DmService restart")  # 重启数据库服务，最多10s
        self.benchmark.init_commands(commands)
        self.benchmark.pressure_measurement(runtime_s=30)

        # 进入目录
        benchmark.ssh.ssh_execute_command(command="cd /opt/dmdbms/data/tmp/benchmarksql-5.0/run", timeout=5)

        if isFirst:
            # 建表 -- 加载 -- 创建索引
            benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props1.dm ../sqlCreateTable.sql", timeout=30)
            benchmark.ssh.ssh_execute_command(command="./runLoader.sh ./props.dm", timeout=8 * 60)
            benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props.dm ../sqlCreateIndex.sql", timeout=40)

        commands = []
        commands.append("./runBenchmark.sh ./props.dm > benchmark.log 2>&1")
        benchmark.init_commands(commands)
        benchmark.pressure_measurement(runtime_s=int(runmins) * 60 + 5)

    def get_tpmc(self):
        """
        返回 tpmc。 如果需要返回其他值，只需要在 return 处增加即可。
        :return:
        """
        local_log = "benchmarkData_self/benchmark.log"
        local_log_save = "benchmarkData_self/extracted_log_data.txt"

        log_manager = LogProcessor()
        log_str = log_manager.read_log_data_toStr(local_log, 10)
        log_dict = log_manager.extract_log_data_toDict(log_str)
        log_manager.save_log_data_toJson(local_log_save, log_dict)
        print(log_dict["Measured_tpmC_NewOrders"])
        return log_dict["Measured_tpmC_NewOrders"]


if __name__ == "__main__":
    # 使用示例
    hostname = '47.108.79.80'
    port = 22
    username = 'root'
    password = 'yjh13896545793'

    ssh_docker = SSH(hostname, port, username, password)  # 压测

    ssh_no_doc = SSH(hostname, port, username, password)  # 传输文件

    # 创建 Benchmark 时自动进入 docker 环境
    benchmark = BenchmarkSql(ssh_docker)
    output = benchmark.out
    error = benchmark.err
    print(output)
    print(error)

    # output, error = ssh.ssh_execute_command("cd / && ls")
    # print(output)
    # print(error)

    # 下载 props.dm
    docker_props_dm = "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/props.dm"
    server_props_dm = "/tmp1/props.dm"
    local_props_dm = "benchmarkData_self/props.dm"
    # ssh_no_doc.transfer_file_inServer_toDocker(docker_props_dm, server_props_dm)
    # ssh_no_doc.download_file(server_props_dm, local_props_dm)

    # 修改 props.dm
    getPropsdm = getPropsdm(local_props_dm)
    runmin = "10"
    getPropsdm.update_config_file(local_props_dm, getPropsdm.propsdm_dict, "runMins", runmin)

    # 上传 props.dm
    ssh_no_doc.upload_file(local_props_dm, server_props_dm)
    ssh_no_doc.transfer_file_inServer_toDocker(server_props_dm, docker_props_dm, True)

    # 压测

    # 上传dm.ini, 修改内部参数
    docker_dmini = "/opt/dmdbms/data/DAMENG/dm.ini"
    server_dmini = "/tmp1/dm.ini"
    local_dmini = "benchmarkData_self/dm.ini"
    getPropsdm.dos2unix(local_dmini)

    ssh_no_doc.upload_file(local_dmini, server_dmini)
    ssh_no_doc.transfer_file_inServer_toDocker(server_dmini, docker_dmini, True)

    # 重启服务器
    commands = []
    commands.append("/opt/dmdbms/bin/DmService restart")  # 重启数据库服务，最多10s
    benchmark.init_commands(commands)
    benchmark.pressure_measurement(runtime_s=30)

    # # 压测一次
    # commands = []
    # commands.append("cd /opt/dmdbms/data/tmp/benchmarksql-5.0/run")

    benchmark.ssh.ssh_execute_command(command="cd /opt/dmdbms/data/tmp/benchmarksql-5.0/run", timeout=5)

    # 建表 和 加载
    benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props1.dm ../sqlCreateTable.sql", timeout=30)
    benchmark.ssh.ssh_execute_command(command="./runLoader.sh ./props.dm", timeout=8 * 60)

    commands = []
    # commands.append("./runSQL.sh ./props.dm ../sqlCreateIndex.sql")
    benchmark.ssh.ssh_execute_command(command="./runSQL.sh ./props.dm ../sqlCreateIndex.sql", timeout=40)

    commands.append("./runBenchmark.sh ./props.dm > benchmark.log 2>&1")
    benchmark.init_commands(commands)
    benchmark.pressure_measurement(runtime_s=int(runmin) * 60 + 5)

    # 读取benchmark.log
    docker_log = "/opt/dmdbms/data/tmp/benchmarksql-5.0/run/benchmark.log"
    server_log = "/tmp1/benchmark.log"
    local_log = "benchmarkData_self/benchmark.log"
    local_log_save = "benchmarkData_self/extracted_log_data.txt"

    ssh_no_doc.transfer_file_inServer_toDocker(docker_log, server_log, False)
    ssh_no_doc.download_file(server_log, local_log)

    logprocessor = LogProcessor()
    log_str = logprocessor.read_log_data_toStr(local_log, 10)
    log_dict = logprocessor.extract_log_data_toDict(log_str)
    logprocessor.save_log_data_toJson(local_log_save, log_dict)
    print(log_dict["Measured_tpmC_NewOrders"])

    ssh_docker.ssh_close()
    ssh_no_doc.ssh_close()
