# -*- coding: utf-8 -*-
'''
    链接爬虫，错误的相对地址
'''
import re

from common import download5


# 传入目标URL和跟踪链接的正则表达式
def link_crawler(seed_url, link_regex):
    # 初始化URL队列
    crawl_queue = [seed_url]
    # 当队列里有URL地址时
    while crawl_queue:
        # 获取第一个URL地址
        url = crawl_queue.pop()
        # 下载URL信息
        html = download5(url)
        # Python 3.X解码
        html = html.decode('utf-8')
        # 遍历返回的链接
        for link in get_links(html):
            # print(link)
            if re.match(link_regex, link):
                print(link)
                # 但这只是相对地址，下一层循环会报错
                crawl_queue.append(link)


# 返回当前页面所有链接
def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/places/default', '/(places/default/view)')
