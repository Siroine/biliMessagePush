import platform
import global_vars
import bili_API
import os


def display_menu():
    """
    显示菜单
    :return:
    """
    if global_vars.check_new_message_running:
        running_display = "\033[32m运行中\033[0m"
    else:
        running_display = "\033[31m已停止\033[0m"

    if global_vars.Bark_PushKey:
        Bark_userDisplay = f"\033[32m{global_vars.Bark_PushKey}\033[0m"
    else:
        Bark_userDisplay = "\033[31m未绑定\033[0m"

    if global_vars.SC_PushKey:
        SC_userDisplay = f"\033[32m{global_vars.SC_PushKey}\033[0m"
    else:
        SC_userDisplay = "\033[31m未绑定\033[0m"

    if global_vars.bili_userCookies:
        bili_username, bili_userUID = bili_API.getLoginUserName(global_vars.bili_userCookies)
        if bili_username and bili_userUID:
            bili_userDisplay = f"\033[32m{bili_username}({bili_userUID})\033[0m"
        else:
            bili_userDisplay = "\033[31m登录状态已失效\033[0m"
    else:
        bili_userDisplay = "\033[31m未登录\033[0m"


    print("\n======= bili私信推送 =======")
    print(f"== Made by {bili_API.getBiliUsername_live_byUID(8084749)} ==")
    print(f"\n当前运行状态：{running_display}")
    print(f"BarkKey: {Bark_userDisplay}")
    print(f"Server酱Key: {SC_userDisplay}")
    print(f"B站登录用户: {bili_userDisplay}")
    print("\n请选择操作:")
    print("1. 启用/停用推送服务")
    print("2. 登录B站账号")
    print("3. 配置Bark推送Key")
    print("4. 配置Server酱推送Key")
    print("5. 消息推送测试")
    print("6. 退出")
    print("\n请输入操作指令 (1-6): ")

def clear_screen():
    """
    清屏函数，兼容 Windows、Unix 系统，以及 PyCharm 调试环境
    """
    system_name = platform.system()
    try:
        if system_name == 'Windows':
            os.system('cls')  # Windows 清屏命令
        elif system_name in ['Linux', 'Darwin']:
            if os.getenv("TERM"):  # 检查是否有正确的 TERM 环境变量
                os.system('clear')  # Unix 清屏命令
            else:
                # 在 PyCharm 中或其他无终端环境中模拟清屏
                print("\n" * 100)
        else:
            # 非常规环境模拟清屏
            print("\n" * 100)
    except Exception as e:
        print(f"清屏时出错: {e}")
        print("\n" * 100)

def press_any_key_to_continue():
    """
    等待用户按任意键继续，兼容 Windows、Unix 系统，以及 PyCharm 调试环境
    """
    print("\n按任意键返回...", end="", flush=True)
    try:
        if platform.system() == 'Windows':
            import msvcrt
            msvcrt.getch()  # 等待用户按键
        else:
            import sys
            import termios
            import tty
            fd = sys.stdin.fileno()
            if os.isatty(fd):  # 判断是否是终端
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    sys.stdin.read(1)  # 等待一个字符输入
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            else:
                # 非终端环境下（如 PyCharm 调试器），通过回车模拟
                input()  # 等待用户按下回车
    except Exception as e:
        print(f"\n出现错误: {e}")
        input("\n回车返回...")  # 回退到更简单的兼容模式
