import os
import json
from pypinyin import pinyin, Style

def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def dict2json(data_dict):
    json_str = json.dumps(data_dict, ensure_ascii=False, indent=2)
    return json_str


def chinese_to_pinyin(name):
    return ''.join([item[0] for item in pinyin(name, style=Style.NORMAL)])
