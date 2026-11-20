import paramiko
from self_DDPG.s_SSH_test import SSH


class BenchmarkSql:
    def __init__(self, ssh):
        self.ssh = ssh

        self.out =[]
        self.err = []

        self.prefix = ""

        # 初始化 docker和Java
        self._benchmark_prepare()
        self.commands = None



    def init_commands(self, init_commands):
        self.commands = init_commands

    def pressure_measurement(self, runtime_s=5):
        outputs = []
        errors = []
        for idx, command in enumerate(self.commands):
            output = ""
            error = ""
            if idx == len(self.commands) - 1:
                output, error = self.ssh.ssh_execute_command(command, timeout=runtime_s)
            else:
                output, error = self.ssh.ssh_execute_command(command, timeout=5)
            outputs.append(output)
            errors.append(error)
        print("压测指令执行完成！\n")
        return outputs, errors

    def _benchmark_prepare(self):
        """
        准备压测的 docker 和 Java 环境， 只需要执行一次。
        在 Benchmark init 时自动执行一次
        """
        # commands_pre = ["docker exec -it dm8_test bash", "source /etc/profile", "ls"]
        commands_pre = ["su dmdba"]

        for command in commands_pre:
            out, err = self.ssh.ssh_execute_command(command, timeout=5)
            self.out.append(out)
            self.err.append(err)


    # def execute_single(self, instruc):
    #     """
    #     输出为 output 和 error
    #     :param instruc:
    #     :return:
    #     """
    #     try:
    #         # 执行指令
    #         stdin, stdout, stderr = self.client.exec_command(instruc)
    #
    #         # 读取标准输出和标准错误
    #         output = stdout.read().decode('utf-8')
    #         error = stderr.read().decode('utf-8')
    #
    #         return output, error
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #         return None, str(e)


if __name__ == "__main__":
    # 使用示例
    hostname = '47.108.79.80'
    port = 22
    username = 'root'
    password = 'yjh13896545793'

    ssh = SSH(hostname, port, username, password)

    output, error = ssh.ssh_execute_command("cd / && ls", 2)
    print("output:\n" + output)
    print("\nerror: " + error)

    output, error = ssh.ssh_execute_command("cd /home && ls", 2)
    print("output:\n" + output)
    print("\nerror: " + error)

    benchmark = BenchmarkSql(ssh)
    output =  benchmark.out
    error = benchmark.err
    print(output)
    print(error)

    benchmark = BenchmarkSql(ssh)

    commands = []
    # commands.append("cd / && ls")
    # commands.append("ls")

    commands.append("/opt/dmdbms/bin/DmService restart")  # 重启数据库服务，最多10s
    benchmark.init_commands(commands)
    benchmark.pressure_measurement(10)

    commands = []
    commands.append("cd /opt/dmdbms/data/tmp/benchmarksql-5.0/run")
    # commands.append("./runSQL.sh ./props1.dm ../sqlCreateTable.sql")
    # commands.append("./runSQL.sh ./props.dm ../sqlCreateIndex.sql")
    # commands.append("./runLoader.sh ./props.dm")
    commands.append("./runBenchmark.sh ./props.dm > benchmark.log 2>&1")

    benchmark.init_commands(commands)
    benchmark.pressure_measurement(1*60)



    output, error = benchmark.pressure_measurement()
    print(output)

    ssh.ssh_close()
