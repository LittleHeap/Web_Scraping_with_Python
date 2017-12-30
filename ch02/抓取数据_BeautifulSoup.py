# -*- coding: utf-8 -*-

import urllib.request

from bs4 import BeautifulSoup


def scrape(html):
    soup = BeautifulSoup(html)
    tr = soup.find(attrs={'id': 'places_area__row'})
    td = tr.find(attrs={'class': 'w2p_fw'})
    area = td.text
    return area


if __name__ == '__main__':
    html = urllib.request.urlopen('http://example.webscraping.com/places/default/view/United-Kingdom-239').read()
    print(scrape(html))
