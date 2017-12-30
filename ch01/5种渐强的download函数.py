# -*- coding: utf-8 -*-
'''
    通常模式下的5种网页下载函数
'''
import urllib.request
import urllib.parse


# 下载网页
def download1(url):
    """Simple downloader"""
    return urllib.request.urlopen(url).read()


# 用异常捕获封装网页下载进程
def download2(url):
    """Download function that catches errors"""
    print('Downloading:', url)
    try:
        html = urllib.request.urlopen(url).read()
    except urllib.request.URLError as e:
        # 打印异常原因
        print('Download error:', e.reason)
        html = None
    return html


# 对异常捕获继续加入异常类别判定，500-599说明错误发生在服务器端，可以重新尝试下载
def download3(url, num_retries=2):
    """Download function that also retries 5XX errors"""
    print('Downloading:', url)
    try:
        html = urllib.request.urlopen(url).read()
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = None
        # 重复请求
        if num_retries > 0:
            # 判定异常参数是否介于500-599
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download3(url, num_retries - 1)
    return html


# 添加用户代理user_agent
def download4(url, user_agent='wswp', num_retries=2):
    """Download function that includes user agent support"""
    print('Downloading:', url)
    # 设置用户代理名称
    headers = {'User-agent': user_agent}
    # 请求同时添加用户代理
    request = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(request).read()
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                html = download4(url, user_agent, num_retries - 1)
    return html


# 设置支持代理
def download5(url, user_agent='wswp', proxy=None, num_retries=2):
    print('Downloading:', url)
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener()
    if proxy:
        proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib.request.ProxyHandler(proxy_params))
    try:
        html = opener.open(request).read()
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                html = download5(url, user_agent, proxy, num_retries - 1)
    return html


if __name__ == '__main__':
    print(download3('http://example.webscraping.com'))
