import time

import json
from datetime import datetime

import bili_API
from Bark_Push import Bark_PushMSG
from ServerChan_Push import SC_PushMSG
from display import display_menu
import global_vars
from public_API import http_safeget

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}



# 主程序
def check_new_message():

    # 登录状态检查
    if not global_vars.bili_userCookies:
        print("\033[31m未登录B站，启动失败..\033[0m")
        return
    if not bili_API.checkCookies(global_vars.bili_userCookies):
        print("\033[31mB站登录状态已失效，启动失败..\033[0m")
        return
    if not global_vars.Bark_PushKey:
        print("\033[31m未填写推送Key，启动失败..\033[0m")
        return

    global_vars.check_new_message_running = True

    # 初始化状态
    last_check_timestamp = int(datetime.now().timestamp())
    webpage_response = http_safeget("https://api.vc.bilibili.com/session_svr/v1/session_svr/single_unread",
                                    cookies=global_vars.bili_userCookies, headers=headers)
    json_unread = webpage_response.json()
    last_unread_count_unfollowed = json_unread['data']['unfollow_unread']
    last_unread_count_followed = json_unread['data']['follow_unread']


    while True:
        if not global_vars.check_new_message_running:
            return
        # 登录状态检查
        if not bili_API.checkCookies(global_vars.bili_userCookies):
            global_vars.check_new_message_running = False
            display_menu()
            return


        try:
            # 检查未读私信数量
            webpage_response = http_safeget('https://api.vc.bilibili.com/session_svr/v1/session_svr/single_unread',
                                            cookies=global_vars.bili_userCookies, headers=headers)

            #print(f"未读私信数量-> {webpage_response.text}")

            if not webpage_response:
                raise ValueError("获取私信信息失败，正在重试..")

            json_unread = webpage_response.json()

            if 'data' not in json_unread:
                raise KeyError(f"获取私信信息失败，正在重试..")
        except Exception as e:
            time.sleep(5)  # 延迟 5 秒后重试
            continue

        # 解析未读私信数量
        json_unread = webpage_response.json()
        current_unread_count_unfollowed = json_unread['data']['unfollow_unread']
        current_unread_count_followed = json_unread['data']['follow_unread']


        # 如果未读数量增加
        if current_unread_count_unfollowed > last_unread_count_unfollowed or current_unread_count_followed > last_unread_count_followed:
            #print(f"时间戳-> {last_check_timestamp}")

            # 获取未读私信详情
            webpage_response = http_safeget(
                f'https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions?begin_ts={last_check_timestamp}&build=0&mobi_app=web',
                cookies=global_vars.bili_userCookies, headers=headers)


            json_unread_details = webpage_response.json()
            #print(f"私信详情1-> {json_unread_details}")
            list_unread_details = json_unread_details['data']['session_list']
            #print(f"私信详情2-> {list_unread_details}")

            #print(f"会话数量-> {len(list_unread_details)}")
            # 遍历会话
            for unread_details in list_unread_details:
                if unread_details['session_type'] == 1:
                    message_fromUID = unread_details['talker_id']
                    unread_count = unread_details['unread_count']
                    #print(f"UID-> {message_fromUID}   私信数量-> {unread_count}")
                    # 获取私信内容
                    webpage_response = http_safeget(
                        f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id={message_fromUID}&session_type=1&size={unread_count}',
                        cookies=global_vars.bili_userCookies, headers=headers)
                    #print(f"对话详情-> {webpage_response.text}")

                    json_message_details = webpage_response.json()
                    messages = json_message_details["data"]["messages"]
                    #print(f"数量-> {len(messages)}")

                    if not messages:
                        continue
                    # 遍历私信记录
                    for message in messages:
                        msg_timestamp = message["timestamp"]
                        #print(f"时间戳-> {msg_timestamp} / {last_check_timestamp}")
                        if message["timestamp"] >= last_check_timestamp:
                            json_message_content = message["content"]
                            parsed_content = json.loads(json_message_content)
                            if message["msg_type"] == 1: # 文本消息
                                message_content = parsed_content["content"]
                                #msg = "title=收到B站私信&body=【昵称】：【正文】&url=&isArchive=0&icon=【头像】&group=私信提醒"
                                Bark_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                             f'{message_content}', 'bilibili://',
                                             bili_API.getBiliAvatar_live_byUID(message_fromUID), 'B站提醒')
                                SC_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                           f'{message_content}  \n[立即查看>>](http://qq.bilibilibot.com/jump_bilibili.html)',
                                           f'{message_content}')


                                #bili_API.sendBiliMessage(global_vars.bili_userCookies, message_fromUID, "感谢你的私信，我将尽快回复。[自动回复]")


                            elif message["msg_type"] == 2: # 图片
                                Bark_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                             f'[图片]', 'bilibili://', bili_API.getBiliAvatar_live_byUID(message_fromUID),
                                             'B站提醒')
                                SC_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                           f'[图片]  \n[立即查看>>](http://qq.bilibilibot.com/jump_bilibili.html)',
                                           f'[图片]')
                            elif message["msg_type"] == 7: #视频
                                message_content = parsed_content["title"]
                                Bark_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                             f'[视频]({message_content})', 'bilibili://', bili_API.getBiliAvatar_live_byUID(message_fromUID),
                                             'B站提醒')
                                SC_PushMSG(f'{bili_API.getBiliUsername_live_byUID(message_fromUID)} 私信了你',
                                           f'[视频]({message_content})。\n[立即查看>>](http://qq.bilibilibot.com/jump_bilibili.html)',
                                           f'[视频]({message_content})')




        # 更新上次检查状态
        last_unread_count_unfollowed = current_unread_count_unfollowed
        last_unread_count_followed = current_unread_count_followed
        last_check_timestamp = int(datetime.now().timestamp())

        # 程序延时
        time.sleep(2)


