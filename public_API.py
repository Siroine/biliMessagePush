import requests

def http_safeget(url, cookies=None, headers=None, params=None, timeout=10):
    """
    安全的 requests.get 封装，处理异常并返回 None 或响应内容。
    """
    try:
        response = requests.get(url, cookies=cookies, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()  # 如果 HTTP 状态码不是 200，抛出异常
        return response
    except requests.exceptions.Timeout:
        pass
        #print(f"请求超时：{url}")
    except requests.exceptions.ConnectionError as ce:
        pass
        #print(f"连接错误：{ce} 请求URL：{url}\n")
    except requests.exceptions.RequestException as e:
        pass
        #print(f"HTTP请求失败：{e} 请求URL：{url}")
    return None

def get_cookie_from_jar(cookie_jar, key):
    """
    从 RequestsCookieJar 中提取特定键的值。

    参数：
        cookie_jar (RequestsCookieJar): 包含 Cookies 的 RequestsCookieJar 对象。
        key (str): 要提取的 Cookie 键名。

    返回：
        str or None: 如果找到对应键名，则返回其值；否则返回 None。
    """
    try:
        # 遍历 RequestsCookieJar 查找特定键
        for cookie in cookie_jar:
            if cookie.name == key:
                return cookie.value
        return None  # 如果未找到键，返回 None
    except Exception as e:
        print(f"Error extracting cookie: {e}")
        return None