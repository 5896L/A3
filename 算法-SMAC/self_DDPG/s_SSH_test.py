import paramiko
import time
import re


class SSH:
    def __init__(self, host, port, username, password):
        """
        输入 参数， 自动登录， 使用时主要使用 self.shell
        :param host:
        :param port:
        :param username:
        :param password:
        """
        self.hostname = host
        self.username = username
        self.port = port
        self.password = password

        # 创建SSH客户端对象
        self.client = paramiko.SSHClient()
        self.shell = None
        self.sftp = None

        self.connect()

        self.time_start = time.time()

    def connect(self):
        while True:
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(
                    self.hostname, port=self.port, 
                    username=self.username, password=self.password
                )
                print(f"Connected to {self.hostname}")
                self.sftp = self.client.open_sftp()
                self.shell = self.client.invoke_shell()
                time.sleep(1)  # 等待Shell会话初始化
                break
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def keep_alive(self):
        while True:
            try:
                if self.client.get_transport().is_active():
                    print("Connection is active. Sending keep-alive signal...")
                    self.client.exec_command('echo keep-alive')
                else:
                    print("Connection lost. Reconnecting...")
                    self.connect()
                time.sleep(3600)  # Send keep-alive signal every 60 seconds
            except Exception as e:
                print(f"Exception in keep-alive thread: {e}")
                print("time span: ", (time.time() - self.time_start))
                self.connect()

    def close(self):
        if self.client:
            self.client.close()
            print(f"Disconnected from {self.hostname}")

    def ssh_execute_command(self, command, timeout=2, runningFlag=False, is_kill=False):
        """
        输出为 执行该指令的 output 和 error
        :param timeout:
        :param command:
        :return:
        """
        try:
            if self.shell is None:
                raise Exception("Shell not initialized")

            # 清空Shell缓冲区
            mistakes = self.get_buffer()

            if mistakes.strip():
                print(mistakes)
                print("------------------")


            # 执行指令
            self.shell.send("\n")
            while self.shell.recv_ready():
                mistakes = self.shell.recv(12288)
                print(mistakes)
                print("------------------")
            self.shell.send(command + "\n")

            # # 等待命令执行完成
            # time.sleep(timeout)  # 等待命令输出完成，可以根据实际情况调整

            # 动态等待输出
            output = ""
            end_time = time.time() + timeout
            while time.time() < end_time:
                output += self.get_buffer()
                time.sleep(0.1)  # 短暂等待防止CPU占用过高
            
            # 使之能够接受到全部的数据
            output += self.get_buffer()


            if runningFlag:
                print(output)
                if "is running" in output:
                    # 使用正则表达式搜索 PID
                    match = re.search(r"\(pid (\d+)\)", output)
                        # 检查是否找到匹配
                    if match:
                        pid = match.group(1)  # 提取第一个括号内的数字
                        print("PID:", pid)
                        kill_command = "kill -9 " + pid + "\n"
                        print(kill_command)
                        if is_kill:
                            self.shell.send(kill_command)           
                            time.sleep(1) 

                            # 读取命令执行的反馈
                            while self.shell.recv_ready():
                                response = self.shell.recv(4096).decode('utf-8')
                                print("Response from kill command:", response)
                        return True
                    else:
                        print("No PID found")
                    return False
                
            else:
                clean_output = output
                # # 去除ANSI转义序列
                if  "ls" in command:
                    clean_output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)
                # 提取命令输出部分
                output_lines = clean_output.splitlines()
                command_output = []
                command_start = False
                for line in output_lines:
                    if command in line:
                        command_start = True
                        continue
                    if command_start:
                        if "root@" in line:
                            break
                        command_output.append(line)

                return "\n".join(clean_output).strip(), " "
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, str(e)


    def download_file(self, remote_path, local_path):
        """
        下载文件
        :param remote_path: 远程文件路径
        :param local_path: 本地文件路径
        :return:
        """
        try:
            self.sftp.get(remote_path, local_path)
            print(f"Successfully downloaded {remote_path} to {local_path}")
        except Exception as e:
            print(f"Error occurred: {e}")

    def download_benchmark_log(self, remote_path = '/opt/data/tmp/benchmark.log', local_path = 'benchmarkData_self/benchmark.log'):
        """
        默认从 '/opt/data/tmp/benchmark.log' 导入到 'benchmarkData_self/benchmark.log'
        :param remote_path:
        :param local_path:
        :return:
        """
        self.download_file(remote_path, local_path)

    def upload_file(self, local_path, remote_path):
        """
        上传文件
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        :return:
        """
        try:
            self.sftp.put(local_path, remote_path)
            print(f"Successfully uploaded {local_path} to {remote_path}\n")
        except Exception as e:
            print(f"Error occurred: {e}\n")


    def transfer_file_inServer_toDocker(self, from_path, to_path, serverTodocker=True, containnerID="8b0bceb2da69"):
        """
        可以从服务器往docker传， 也可以从docker往服务器传
        :param from_path:
        :param to_path:
        :return:
        """
        if serverTodocker:
            command = "docker cp " + from_path + " " + containnerID + ":" + to_path
            # print(command)
        else:
            command = "docker cp " + containnerID + ":" + from_path + " " + to_path
            print(command)

        self.ssh_execute_command(command, 5)

    def get_buffer(self):
        res = ""
        while self.shell.recv_ready():
            res += self.shell.recv(12288).decode("utf-8")
        return res



if __name__ == '__main__':
    hostname = '47.108.79.80'
    port = 22
    username = 'root'
    password = 'yjh13896545793'

    ssh = SSH(hostname, port, username, password)

    output, error = ssh.ssh_execute_command("cd / && ls", 2)
    if output:
        print("Output:\n", output)
    if error:
        print("\nError: ", error)

    # # 下载文件
    remote_path = '/home/dmdba/benchmarksql-5.0/run/benchmark.log'
    local_path = 'self_DDPG/benchmarkData_self/benchmark.log'
    ssh.download_file(remote_path, local_path)

    # remote_path = '/opt/data/tmp/test.txt'
    # local_path = 'benchmarkData_self/test.txt'
    # ssh.upload_file(local_path, remote_path)

    ssh.ssh_close()
