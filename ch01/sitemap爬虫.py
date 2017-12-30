# -*- coding: utf-8 -*-
'''
    通过正则表达式从<loc>标签中抽取URL
'''
import re
from common import download1


def crawl_sitemap(url):
    # 下载sitemap文件
    sitemap = download1(url)
    # Python 3.X加入解码
    sitemap = sitemap.decode('utf-8')
    # print(sitemap)
    # 抓取全部链接
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # 遍历下载/打印全部链接
    for link in links:
        html = download1(link)


if __name__ == '__main__':
    crawl_sitemap('http://example.webscraping.com/sitemap.xml')
