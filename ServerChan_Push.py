import requests
import re
from public_class import Class_ConfigManager
ConfigManager = Class_ConfigManager()
import global_vars
import base64
import pickle
from display import press_any_key_to_continue

def readSCKey_fromFile():
    """
    从文件读取Server酱的推送Key
    :return: 成功返回Key，失败返回None
    """
    PushKey_base64 = ConfigManager.get('bili_message.ini','UserInfo','SC_PushKey')
    if not PushKey_base64:
        return None
    PushKey_bytes = base64.b64decode(PushKey_base64)
    PushKey = pickle.loads(PushKey_bytes)
    return PushKey

def writeSCKey_toFile(PushKey):
    """
    将Key保存至文件
    :return: 成功返回Key，失败返回None
    """
    PushKey_bytes = pickle.dumps(PushKey)
    PushKey_base64 = base64.b64encode(PushKey_bytes).decode('utf-8')
    ConfigManager.set('bili_message.ini', 'UserInfo', 'SC_PushKey', PushKey_base64)

def SC_savePushKey(input_str):
    """
    保存Server酱的PushKey
    :param input_str: 支持URL或Key
    :return: 成功返回True 失败返回False
    """
    if input_str.startswith("https://"):
        match = re.search(r"https://\d+\.push\.ft07\.com/send/([a-zA-Z0-9]+)\.send", input_str)
        if match:
            global_vars.SC_PushKey = match.group(1)
    else:
        match = re.fullmatch(r"[a-zA-Z0-9]{16,48}", input_str)
        if match:
            global_vars.SC_PushKey = match.group(0)
        else:
            return False

    if global_vars.SC_PushKey:
        writeSCKey_toFile(global_vars.SC_PushKey)
        return True

    return False

def SC_configurePushURL():
    SCKey_Input = input("[若需删除已保存的KEY，请直接回车]\n请输入SC软件中的推送KEY(支持链接格式):\n")
    if SCKey_Input:
        if SC_savePushKey(SCKey_Input):
            print("\033[32m保存成功\033[0m")
            press_any_key_to_continue()
            return
        else:
            print("\033[31m保存失败，请重试\033[0m")
    else:
        global_vars.SC_PushKey = None
        writeSCKey_toFile(None)
        print("\033[32m删除成功\033[0m")
    press_any_key_to_continue()
    return

def SC_PushMSG(title, desp='', short='', options=None):

    if not global_vars.SC_PushKey:
        return False
    sendkey = global_vars.SC_PushKey
    if options is None:
        options = {}
    # 判断 sendkey 是否以 'sctp' 开头，并提取数字构造 URL
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
    params = {
        'title': title,
        'desp': desp,
        'short': short,
        **options
    }
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }


    # 发送 POST 请求
    try:
        response = requests.post(url, json=params, headers=headers)

        # 检查响应状态
        #print(f"response.status_code({response.status_code})")
        if response.status_code == 200:
            response_json = response.json()
            #print(f"response_json['code']({response_json['code']})")
            if response_json['code'] == 0:
                return True
            return False
        else:
            return False
    except requests.RequestException as e:
        return False

if not global_vars.SC_PushKey:
    global_vars.SC_PushKey = readSCKey_fromFile()