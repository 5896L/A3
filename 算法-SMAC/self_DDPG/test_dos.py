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


if __name__ == '__main__':
    # 输入文件路径
    file_path = 'benchmarkData_self/props.dm'

    # 调用函数进行转换
    dos2unix(file_path)

    print(f"Converted {file_path} to Unix format.")
