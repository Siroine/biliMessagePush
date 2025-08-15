from bili_login import biliAPI_Login
from Bark_Push import Bark_configurePushURL, Bark_PushMSG
from ServerChan_Push import SC_configurePushURL, SC_PushMSG
from bili_Message import check_new_message
from public_class import Class_ConfigManager
ConfigManager = Class_ConfigManager()
from display import display_menu, clear_screen, press_any_key_to_continue
import global_vars

import bili_API
import threading
import time

def PUSH_test():
    if global_vars.Bark_PushKey:
        print("正在尝试推送Bark...")
        if Bark_PushMSG(f"{bili_API.getBiliUsername_live_byUID(8084749)} 私信了你", "这是一条测试通知，欢迎关注我，立即前往>>", "bilibili://space/8084749",
                        "https://i1.hdslb.com/bfs/face/a5d15f14c588dc2f5711b3e9e1e8d990f184cc28.jpg", "B站提醒"):
            print("\033[32mBark已推送\033[0m")
            print(
                "如果你收到了Bark的消息推送，那么恭喜你已经成功配置推送Key。\n消息可能会延迟数秒，如果在一分钟后仍未收到提醒，请检查Bark的推送Key配置是否正确。\n")
        else:
            print("\033[31mBark推送失败\033[0m")
            print(
                "如果你收到了Bark的消息推送，那么可能是推送结果解析失败，大概不会不影响使用。\n")

    if global_vars.SC_PushKey:
        print("正在尝试推送Server酱...")
        if SC_PushMSG(f"{bili_API.getBiliUsername_live_byUID(8084749)} 私信了你",
                            "这是一条测试通知，欢迎关注我，[立即前往>>](https://space.bilibili.com/8084749) ![头像 #50px#50px](https://i1.hdslb.com/bfs/face/a5d15f14c588dc2f5711b3e9e1e8d990f184cc28.jpg)",
                            "这是一条测试通知，欢迎关注我，立即前往>>"):
            print("\033[32mServer酱已推送\033[0m")
            print(
                "如果你收到了Server酱的消息推送，那么恭喜你已经成功配置推送Key。\n消息可能会延迟数秒，如果在一分钟后仍未收到提醒，请检查Server酱的推送Key配置是否正确。")
        else:
            print("\033[31mServer酱推送失败\033[0m")
            print(
                "如果你收到了Server酱的消息推送，那么可能是推送结果解析失败，大概不会不影响使用。")
    press_any_key_to_continue()

def main():
    """主程序"""
    while True:
        clear_screen()
        display_menu()

        global_vars.auto_refresh_menu = True # 自动刷新菜单标识
        choice = input()
        global_vars.auto_refresh_menu = False # 选择菜单后暂停自动刷新

        if choice == '1':
            if global_vars.check_new_message_running:
                print("停止中..")
                ConfigManager.set('bili_message.ini', 'Set', 'Push_AutoRunning', None)
                global_vars.check_new_message_running = False
                time.sleep(1)
            else:
                print("启动中...")
                thread = threading.Thread(target=check_new_message)
                thread.daemon = True  # 设置为守护线程
                thread.start()  # 启动线程
                ConfigManager.set('bili_message.ini', 'Set', 'Push_AutoRunning', 'True')
                time.sleep(1)
        elif choice == '2':
            clear_screen()
            biliAPI_Login()
        elif choice == '3':
            clear_screen()
            Bark_configurePushURL()
        elif choice == '4':
            clear_screen()
            SC_configurePushURL()
        elif choice == '5':
            clear_screen()
            #bilibili://space/8084749
            PUSH_test()
        elif choice == '6':
            print("退出程序...")
            break
        else:
            print("无效的选择，请重新输入！")


if __name__ == '__main__':
    if ConfigManager.get('bili_message.ini', 'Set', 'Push_AutoRunning') == 'True':
        thread = threading.Thread(target=check_new_message)
        thread.daemon = True  # 设置为守护线程
        thread.start()  # 启动线程
        time.sleep(0.2)
    main()