# -*- coding: utf-8 -*-
import re
import urllib.parse
import urllib.robotparser

from downloader import Downloader


def link_crawler(seed_url, link_regex=None, delay=2, max_depth=1, max_urls=-1, user_agent='wswp', proxies=None,
                 num_retries=1, scrape_callback=None, cache=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # 目标爬虫URL队列
    crawl_queue = [seed_url]
    # 初始化已经遍历爬虫的URL深度字典
    seen = {seed_url: 0}
    # 记录爬了多少URL地址
    num_urls = 0
    rp = get_robots(seed_url)
    # 下载页面
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)
    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # 检查robots.txt限定，是否允许代理爬虫当前页面
        if rp.can_fetch(user_agent, url):
            # 触发__call__函数
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])

            if depth != max_depth:
                # 继续深度爬虫
                if link_regex:
                    # 正则表达式限定
                    # links.extend(link for link in get_links(html) if re.match(link_regex, link))
                    # Python 3.X解码
                    html = html.decode('utf-8')
                    # 遍历当前页面所有链接
                    for link in get_links(html):
                        if re.match(link_regex, link):
                            print(link)
                            links.extend([link])
                for link in links:
                    link = normalize(seed_url, link)
                    # 检查是否爬过当前URL
                    if link not in seen:
                        seen[link] = depth + 1
                        # 检查URL是否与种子地址属于同一源
                        if same_domain(seed_url, link):
                            # 确认成功，加入未来爬虫URL队列
                            crawl_queue.append(link)

            # 检查已爬数量是否达到最大值
            num_urls += 1
            # if num_urls == max_urls:
            #     break
        else:
            print('Blocked by robots.txt:', url)


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urllib.parse.urldefrag(link)  # remove hash to avoid duplicates
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


def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)', delay=3,
                 num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(places/default/index|places/default/view)', delay=3,
                 num_retries=1, max_depth=1, user_agent='GoodCrawler')
