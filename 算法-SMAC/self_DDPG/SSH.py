import paramiko


class SSH:
    def __init__(self, host, port, username, password):
        """
        输入 参数， 自动登录， 使用时主要使用 self.client
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
        self.ssh_login()

    def ssh_login(self):
        """
        登录 服务器
        :param host:
        :param username:
        :param password:
        :return:   paramiko.SSHClient()
        """

        # 自动添加策略，保存服务器的主机名和密钥信息
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.hostname, self.port, self.username, self.password)

    def ssh_execute_command(self, command):
        """
        输出为 执行该指令的 output 和 error
        :param command:
        :return:
        """
        try:
            # 执行指令
            stdin, stdout, stderr = self.client.exec_command(command)

            # 读取标准输出和标准错误
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            return output, error
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, str(e)

    def ssh_close(self):
        self.client.close()


if __name__ == '__main__':
    hostname = '47.108.79.80'
    port = 22
    username = 'root'
    password = 'yjh13896545793'

    ssh = SSH(hostname, port, username, password)

    output, error = ssh.ssh_execute_command("cd / && ls")
    print(output)
    print("\nerror: " + error)

    ssh.ssh_close()
