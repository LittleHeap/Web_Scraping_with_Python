# -*- coding: utf-8 -*-
'''
    通过循环国家ID直接下载网页
'''

import itertools

from common import download5


def iteration():
    for page in itertools.count(1):
        # 单位时间请求次数过多会失败
        url = 'http://example.webscraping.com/places/default/view/%d' % page
        html = download5(url)
        if html is None:
            # 接收到一个错误，默认遍历结束全部网页
            break
        else:
            # 成功获取到网页
            pass


if __name__ == '__main__':
    iteration()
