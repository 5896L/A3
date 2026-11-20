import re


class getPropsdm:
    def __init__(self, file_path):
        self.file_path = file_path
        self.propsdm_dict = None

        self.config_text = self.read_config_file(self.file_path)
        self.propsdm_dict = self.parse_config(self.config_text)


    # 读取配置文件
    def read_config_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            config_text = file.read()
        return config_text

    def parse_config(self, config_text):
        """
        返回对应字典 config dict
        :param config_text:
        :return:
        """
        # 移除注释行
        lines = config_text.split('\n')
        non_comment_lines = [line for line in lines if
                             not line.strip().startswith('//') and not line.strip().startswith('#')]
        non_comment_text = '\n'.join(non_comment_lines)

        # 使用正则表达式匹配配置参数
        pattern = re.compile(r"(\w+)=([^\n]+)")
        matches = pattern.findall(non_comment_text)

        # 将匹配到的参数保存到字典中
        config_dict = {key: value for key, value in matches}

        return config_dict

    def update_config_file(self, file_path, config_dict, target_key=None, target_value=None):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if target_key and target_value:
            config_dict[target_key] = target_value

        new_lines = []
        pattern = re.compile(r"(\w+)=([^\n]+)")

        for line in lines:
            if line.strip().startswith('//') or line.strip().startswith('#') or '=' not in line:
                new_lines.append(line)
                continue

            match = pattern.match(line.strip())
            if match:
                key = match.group(1)
                if key in config_dict:
                    new_lines.append(f"{key}={config_dict[key]}\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)

        self.dos2unix(file_path)

    def dos2unix(self, file_path, new_file_path=None):
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


if __name__ == '__main__':
    # 配置文件路径
    file_path = 'benchmarkData_self/props.dm'

    # 读取配置文件内容
    # config_text = read_config_file(file_path)
    #
    # # 解析配置内容
    # config_dict = parse_config(config_text)

    # # 输出解析结果
    # for key, value in config_dict.items():
    #     print(f"{key}: {value}")
    #
    # config_dict['db'] = "dameng"
    # config_dict['runMins'] = "10"

    for key, value in config_dict.items():
        print(f"{key}: {value}")
    update_config_file(file_path, config_dict)
