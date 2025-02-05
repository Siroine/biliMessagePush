import requests
import time
import qrcode
import base64
import pickle
import tempfile
import os
import platform
'''
# 这些是窗口显示图片用的库
from PIL import Image, ImageTk
import tkinter as tk
import threading
'''
import bili_API
from public_class import Class_ConfigManager
ConfigManager = Class_ConfigManager()
from display import press_any_key_to_continue
import global_vars


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}
window_ref = None





def show_QRCode(url):
    """
    用窗口显示传递内容的二维码
    :param url:
    :return:
    """
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1 是最小值，值越大二维码越复杂
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率: L 7%, M 15%, Q 25%, H 30%
        box_size=10,  # 每个二维码单元格的像素大小
        border=4,  # 边框的单元格宽度
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 生成二维码图像
    img = qr.make_image(fill_color="black", back_color="white")

    # 保存二维码到临时文件
    temp_dir = tempfile.gettempdir()  # 获取临时文件目录
    file_path = os.path.join(temp_dir, "qrcode.png")
    img.save(file_path)

    # 检测系统类型并调用对应方法显示图片
    system_name = platform.system()
    try:
        if system_name == "Windows":
            # Windows 系统
            os.startfile(file_path)
        elif system_name == "Darwin":
            # macOS 系统
            os.system(f"open {file_path}")
        elif system_name == "Linux":
            # Linux 系统
            os.system(f"xdg-open {file_path}")
        else:
            raise NotImplementedError(f"Unsupported system: {system_name}")
    except Exception as e:
        print(f"无法显示二维码: {e}")
        print(f"请手动打开文件: {file_path}")


def destroy_QRCodeWindow():
    """
    销毁QRcode窗口
    :return:
    """
    global window_ref
    if window_ref:
        window_ref.after(0, window_ref.destroy)

def poll_qr_code_status(qrcode_key):
    """
    轮询二维码状态，返回登录后的Cookies
    :param qrcode_key:
    :return:
    """
    url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}&source=main-fe-header'
    lastResponseStatus = None

    while True:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if response_json['data']['message'] != lastResponseStatus:
            print(f"二维码状态-> \033[33m{response_json['data']['message']}\033[0m")

        lastResponseStatus = response_json['data']['message']

        if response_json['data']['code'] == 0:
            # 登录成功
            print(f" {response_json}")
            return response.cookies
        elif response_json['data']['code'] not in [86101, 86090]:
            print(f"错误的code: {response_json['data']['code']}")
            break

        time.sleep(0.5)

    return None

def readBiliCookies_fromFile():
    """
    从文件读取Cookies
    :return: 成功返回Cookies，失败返回None
    """
    cookies_base64 = ConfigManager.get('bili_message.ini','UserInfo','bili_LoginCookies')
    if not cookies_base64:
        return None
    cookies_bytes = base64.b64decode(cookies_base64)
    cookies = pickle.loads(cookies_bytes)
    return cookies

def writeBiliCookies_toFile(cookies):
    """
    将Cookies保存至文件
    :return:
    """
    cookies_bytes = pickle.dumps(cookies)
    cookies_base64 = base64.b64encode(cookies_bytes).decode('utf-8')
    ConfigManager.set('bili_message.ini','UserInfo','bili_LoginCookies',cookies_base64)




def biliAPI_Login():
    """
    唤起bilibili登录行为
    :return:
    """
    # 1. 请求二维码
    qr_code_url, qrcode_key = bili_API.getLoginQRcode()
    print(f"获取到二维码: {qr_code_url}")

    # 2. 显示二维码
    show_QRCode(qr_code_url)


    # 3. 轮询二维码扫描状态
    global_vars.bili_userCookies = poll_qr_code_status(qrcode_key)
    #destroy_QRCodeWindow()

    # 4. 显示用户信息
    if global_vars.bili_userCookies:
        user_name, user_uid = bili_API.getLoginUserName(global_vars.bili_userCookies)
        print(f'登录成功 -> \033[32m{user_name}({user_uid})\033[0m')
        writeBiliCookies_toFile(global_vars.bili_userCookies)
    else:
        print("\033[31m登录失败，请重试\033[0m")
    press_any_key_to_continue()
    return


if not global_vars.bili_userCookies:
    global_vars.bili_userCookies = readBiliCookies_fromFile()

if __name__ == '__main__':
    biliAPI_Login()
