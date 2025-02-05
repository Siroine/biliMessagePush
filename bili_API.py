import requests
import json
import time
import uuid
from public_API import http_safeget, get_cookie_from_jar

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}


def getBiliAvatar_live_byUID(uid):
    """
    【live】通过直播站API获取用户头像URL（无鉴权）
    :param uid: 用户的UID
    :return: 头像的URL
    """
    url = f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={uid}"
    try:
        response = http_safeget(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            # 解析JSON
            data = response.json()
            avatar_url = data.get("data", {}).get("info", {}).get("face", "")
            return avatar_url
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return ""
    except Exception as e:
        print(f"获取头像失败: {e}")
        return ""

def getBiliUsername_live_byUID(uid):
    """
    【live】通过直播站API获取用户昵称（无鉴权）
    :param uid: 用户的UID
    :return: 用户昵称
    """
    url = f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={uid}"
    try:
        response = http_safeget(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            # 解析JSON
            data = response.json()
            username = data.get("data", {}).get("info", {}).get("uname", "")
            return username
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return ""
    except Exception as e:
        print(f"获取昵称失败: {e}")
        return ""

def getLoginQRcode():
    """
    获取bilibili网页登录用二维码
    :return: 返回二维码URL以及对应的二维码key
    """

    url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
    response = http_safeget(url, headers=headers)
    #response_text = response.content.decode('utf-8')
    #print(response_text)
    response_json = response.json()

    qr_code_url = response_json['data']['url']
    qrcode_key = response_json['data']['qrcode_key']

    return qr_code_url, qrcode_key

def checkCookies(cookies):
    # 验证登录
    if not cookies:
        # 用户没有登录B站
        return False
    bili_username, bili_userUID = getLoginUserName(cookies)
    if not bili_username or not bili_userUID:
        # 用户登录状态已失效
        return False
    return True

def getLoginUserName(cookies):
    """
    显示登录用户的用户名及UID
    :param cookies: 登录后的Cookies
    :return: 返回用户名和UID
    """
    url = 'https://api.bilibili.com/x/space/v2/myinfo'
    response = http_safeget(url, cookies=cookies, headers=headers)
    response_json = response.json()
    if 'data' in response_json:
        if response_json['data']['profile']['mid'] != "" and response_json['data']['profile']['name'] != "":
            user_name = response_json['data']['profile']['name']
            user_uid = response_json['data']['profile']['mid']
            return user_name, user_uid
    return None





if __name__ == "__main__":
    #test_uid = "8084749"
    avatar = getBiliAvatar_live_byUID(test_uid)
    username = getBiliUsername_live_byUID(test_uid)

    print(f"UID: {test_uid}")
    print(f"昵称: {username}")
    print(f"头像URL: {avatar}")
