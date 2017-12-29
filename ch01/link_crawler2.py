# -*- coding: utf-8 -*-
'''
    链接爬虫，链接成完整的绝对地址，但是访问到一定次数也会被屏蔽，可以通过延时增加稳定性
'''
import re
import time
import urllib.parse

from datetime import datetime
from common import download5


def link_crawler(seed_url, link_regex, delay=5):
    # 设置限速
    throttle = Throttle(delay)
    crawl_queue = [seed_url]
    # 集合存储已访问网址对象
    seen = set(crawl_queue)
    while crawl_queue:
        url = crawl_queue.pop()
        # 延时等待
        throttle.wait(url)
        html = download5(url)
        # Python 3.X解码
        html = html.decode('utf-8')
        for link in get_links(html):
            if re.match(link_regex, link):
                # 如果匹配则链接成绝对地址
                link = urllib.parse.urljoin(seed_url, link)
                # print(link)
                # 判定是否已经访问过
                if link not in seen:
                    print(link)
                    # 没访问过则扔进集合
                    seen.add(link)
                    # 没访问过则扔进队列
                    crawl_queue.append(link)


# 返回网页中全部链接
def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


# 下载限速延时
class Throttle:
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        domain = urllib.parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)')
