# -*- coding: utf-8 -*-
'''
    正则表达式抓取数据
'''
import re
import urllib.request


def scrape(html):
    html = html.decode('utf-8')
    area = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]
    area = re.findall('<td class="w2p_fw">(.*?)</td>', html)[1]
    return area


if __name__ == '__main__':
    html = urllib.request.urlopen('http://example.webscraping.com/places/default/view/United-Kingdom-239').read()
    print(scrape(html))
