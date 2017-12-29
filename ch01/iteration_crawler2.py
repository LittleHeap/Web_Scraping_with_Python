# -*- coding: utf-8 -*-
'''
    设置访问失败限度，完善ID遍历爬虫强壮性
'''

import itertools

from common import download5


def iteration():
    # 允许最大访问失败次数
    max_errors = 5
    # 当前已有访问失败次数
    num_errors = 0
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/places/default/view/%d' % page
        html = download5(url)
        if html is None:
            # 返回下载网页失败
            num_errors += 1
            if num_errors == max_errors:
                # 达到预期失败限度，退出循环
                break
        else:
            # 否则重置当前失败次数
            num_errors = 0


if __name__ == '__main__':
    iteration()
