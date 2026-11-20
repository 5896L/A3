from update_config import update_ini
from utils import load_json_to_dict
import json


source_ini = "dm_source.ini"
target_ini = "self_DDPG/benchmarkData_self/dm.ini"
SERIAL_NUMBER = "1164"

# 指定JSON文件的路径
file_path = 'smac3_output/e115652d6c44f93601f6a53332fd6f71/0/runhistory.json'

# 打开并读取JSON文件
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
config = data.get("configs").get(SERIAL_NUMBER)
update_ini(config, dict_write=True, dic=config, source_file_path=source_ini, target_file_path=target_ini)  # 修改dm.ini文件