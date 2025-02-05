import re
import base64
import pickle
import requests


from public_class import Class_ConfigManager
ConfigManager = Class_ConfigManager()
import global_vars

from display import press_any_key_to_continue


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def readBarkKey_fromFile():
    """
    从文件读取Bark的推送Key
    :return: 成功返回Key，失败返回None
    """
    PushKey_base64 = ConfigManager.get('bili_message.ini','UserInfo','Bark_PushKey')
    if not PushKey_base64:
        return None
    PushKey_bytes = base64.b64decode(PushKey_base64)
    PushKey = pickle.loads(PushKey_bytes)
    return PushKey

def writeBarkKey_toFile(PushKey):
    """
    将Key保存至文件
    :return: 成功返回Key，失败返回None
    """
    PushKey_bytes = pickle.dumps(PushKey)
    PushKey_base64 = base64.b64encode(PushKey_bytes).decode('utf-8')
    ConfigManager.set('bili_message.ini', 'UserInfo', 'Bark_PushKey', PushKey_base64)

def Bark_savePushKey(input_str):
    """
    保存Bark的PushKey
    :param input_str: 支持URL或Key
    :return: 成功返回True 失败返回False
    """
    if input_str.startswith("https://"):
        match = re.search(r"https://api\.day\.app/([a-zA-Z0-9]+)", input_str)
        if match:
            global_vars.Bark_PushKey = match.group(1)
    else:
        match = re.fullmatch(r"[a-zA-Z0-9]{16,32}", input_str)  # 限制长度为 16-32 位
        if match:
            global_vars.Bark_PushKey = match.group(0)
        else:
            return False

    if global_vars.Bark_PushKey:
        writeBarkKey_toFile(global_vars.Bark_PushKey)
        return True

    return False

def Bark_configurePushURL():
    BarkKey_Input = input("[若需删除已保存的KEY，请直接回车]\n请输入Bark软件中的推送KEY(支持链接格式):\n")
    if BarkKey_Input:
        if Bark_savePushKey(BarkKey_Input):
            print("\033[32m保存成功\033[0m")
            press_any_key_to_continue()
            return
        else:
            print("\033[31m保存失败，请重试\033[0m")
    else:
        global_vars.Bark_PushKey = None
        writeBarkKey_toFile(None)
        print("\033[32m删除成功\033[0m")
    press_any_key_to_continue()
    return

def Bark_PushMSG(title, body, url=None, icon=None, group=None, isArchive=0):
    #title=猫屋敷梨梨Official：黑神话初见day2！&body=你的关注正在直播，快去看看吧，立即前往>>&url=https://live.bilibili.com/4494478/&isArchive=0&icon=https://i1.hdslb.com/bfs/face/588991fa450feaab711d3a82c5e5f22fd6086ce0.jpg&group=直播提醒
    if not global_vars.Bark_PushKey:
        return False
    api_url = f'https://api.day.app/{global_vars.Bark_PushKey}/'
    post_data = {
        "title": title,
        "body": body,
        "url": url,
        "icon": icon,
        "group": group,
        "isArchive": isArchive,
    }

    # 删除值为 None 的键，避免发送空数据
    post_data = {k: v for k, v in post_data.items() if v is not None}

    # 发送 POST 请求
    try:
        response = requests.post(api_url, data=post_data)

        # 检查响应状态
        if response.status_code == 200:
            response_json = response.json()
            if response_json['code'] == 200:
                return True
            return False
        else:
            return False
    except requests.RequestException as e:
        return False




if not global_vars.Bark_PushKey:
    global_vars.Bark_PushKey = readBarkKey_fromFile()

