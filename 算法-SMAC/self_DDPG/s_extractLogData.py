import re
import json
from collections import deque


class LogProcessor:
    @staticmethod
    def read_log_data_toStr( file_path, num_lines):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = deque(file, maxlen=num_lines)
        return ''.join(lines)

    @staticmethod
    def extract_log_data_toDict( log_content):
        """
        返回 字典        "Measured_tpmC_NewOrders": 15000.0,
                       "Measured_tpmTOTAL": 24191.44,
                       "Session_Start": "2024-07-02 08:26:11",
                       "Session_End": "2024-07-02 08:27:11",
                       "Transaction_Count": 24286
        :param log_content:
        :return:
        """
        tpmC_match = re.search(r'Measured tpmC \(NewOrders\) = ([\d.]+)', log_content)
        tpmTOTAL_match = re.search(r'Measured tpmTOTAL = ([\d.]+)', log_content)
        session_start_match = re.search(r'Session Start\s+=\s+([\d\-: ]+)', log_content)
        session_end_match = re.search(r'Session End\s+=\s+([\d\-: ]+)', log_content)
        transaction_count_match = re.search(r'Transaction Count = (\d+)', log_content)

        log_data = {
            "Measured_tpmC_NewOrders": float(tpmC_match.group(1)) if tpmC_match else None,
            "Measured_tpmTOTAL": float(tpmTOTAL_match.group(1)) if tpmTOTAL_match else None,
            "Session_Start": session_start_match.group(1) if session_start_match else None,
            "Session_End": session_end_match.group(1) if session_end_match else None,
            "Transaction_Count": int(transaction_count_match.group(1)) if transaction_count_match else None
        }

        return log_data

    @staticmethod
    def save_log_data_toJson(file_path, log_data):
        log_data_str = json.dumps(log_data, indent=4)

        try:
            with open(file_path, 'r') as file:
                existing_content = file.read()
        except FileNotFoundError:
            existing_content = ""

        new_content = log_data_str + "\n\n" + existing_content

        with open(file_path, 'w') as txt_file:
            txt_file.write(new_content)

        print(f"数据已保存到 {file_path}")


if __name__ == "__main__":
    # 使用类的方法处理日志文件
    log_file_path = 'benchmarkData_self/benchmark.log'
    output_file_path = 'benchmarkData_self/extracted_log_data.txt'

    log_content = LogProcessor.read_log_data_toStr(log_file_path, 10)  # 字符串
    log_data = LogProcessor.extract_log_data_toDict(log_content)  # 字典
    LogProcessor.save_log_data_toJson(output_file_path, log_data)  # json格式字符串
