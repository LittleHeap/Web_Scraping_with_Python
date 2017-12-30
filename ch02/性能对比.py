# -*- coding: utf-8 -*-

import csv
import time
import urllib.request
import re
import timeit
from bs4 import BeautifulSoup
import lxml.html

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')


# 正则表达式爬虫
def regex_scraper(html):
    results = {}
    html = html.decode('utf-8')
    for field in FIELDS:
        results[field] = re.search('<tr id="places_{}__row">.*?<td class="w2p_fw">(.*?)</td>'.format(field), html).groups()[0]
    return results

# BeautifulSoup爬虫
def beautiful_soup_scraper(html):
    soup = BeautifulSoup(html, 'html.parser') 
    results = {}
    for field in FIELDS:
        results[field] = soup.find('table').find('tr', id='places_{}__row'.format(field)).find('td', class_='w2p_fw').text
    return results

# Lxml爬虫
def lxml_scraper(html):
    tree = lxml.html.fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content()
    return results


def main():
    times = {}
    html = urllib.request.urlopen('http://example.webscraping.com/places/default/view/United-Kingdom-239').read()
    # 测试次数
    NUM_ITERATIONS = 1000
    for name, scraper in ('Regular expressions', regex_scraper), ('Beautiful Soup', beautiful_soup_scraper), ('Lxml', lxml_scraper):
        times[name] = []
        # 记录开始时间
        start = time.time()
        for i in range(NUM_ITERATIONS):
            if scraper == regex_scraper:
                # 清缓存
                re.purge() 
            result = scraper(html)

            # 检查是否符合预期结果
            assert(result['area'] == '244,820 square kilometres')
            times[name].append(time.time() - start)
        # 记录结束时间
        end = time.time()
        print('{}: {:.2f} seconds'.format(name, end - start))

    writer = csv.writer(open('times.csv', 'w'))
    header = sorted(times.keys())
    writer.writerow(header)
    for row in zip(*[times[scraper] for scraper in header]):
        writer.writerow(row)


if __name__ == '__main__':
    main()
