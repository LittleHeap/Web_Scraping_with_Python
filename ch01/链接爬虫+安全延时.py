# -*- coding: utf-8 -*-
'''
    链接爬虫，可限制深度
'''
import queue
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime


def link_crawler(seed_url, link_regex=None, delay=2, max_depth=2, headers=None, user_agent='wswp',
                 proxy=None, num_retries=2):
    # 爬虫队列
    crawl_queue = queue.deque([seed_url])
    # 已爬网页和其对应的深度
    seen = {seed_url: 0}
    # 计算爬取网页的数量
    num_urls = 0
    rp = get_robots(seed_url)
    # 初始化延时函数
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        # 获取队列中URL地址
        url = crawl_queue.pop()
        # 检测代理是否可以访问
        if rp.can_fetch(user_agent, url):
            # 延时
            throttle.wait(url)
            # 下载页面
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []
            depth = seen[url]
            # 检测是否达到目标深度
            if depth != max_depth:
                # 是否有跟踪链接正则表达式
                if link_regex:
                    # Python 3.X解码
                    html = html.decode('utf-8')
                    # 遍历当前页面所有链接
                    for link in get_links(html):
                        if re.match(link_regex, link):
                            print(link)
                            links.extend([link])
                print(links)
                for link in links:
                    # print(link)
                    # 连接成绝对地址
                    link = normalize(seed_url, link)
                    # 检测是否已访问
                    if link not in seen:
                        # 没访问就将其存入seen字典，并记录深度
                        seen[link] = depth + 1
                        # 判定新链接和旧链接是否来自一个主地址
                        if same_domain(seed_url, link):
                            # 确定是就加入未来访问队列
                            crawl_queue.append(link)
            # 检测是否达到目标网页数量
            num_urls += 1
            # if num_urls == max_urls:
            #     break
        else:
            print('Blocked by robots.txt:', url)


# 下载限速
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


def download(url, headers, proxy, num_retries, data=None):
    print('Downloading:', url)
    request = urllib.request.Request(url, data, headers)
    opener = urllib.request.build_opener()
    if proxy:
        proxy_params = {urllib.urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib.request.ProxyHandler(proxy_params))
    try:
        response = opener.open(request)
        html = response.read()
        code = response.code
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                return download(url, headers, proxy, num_retries - 1, data)
        else:
            code = None
    return html


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    # link, _ = urllib.parse.urldefrag(link)  # remove hash to avoid duplicates
    return urllib.parse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


# 返回网页的全部链接
def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)', user_agent='BadCrawler')
    # link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)', delay=0,
    #              num_retries=1, max_depth=1, user_agent='GoodCrawler')
