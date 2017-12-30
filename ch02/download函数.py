# -*- coding: utf-8 -*-

import urllib.request


def download(url, user_agent=None):
    print('Downloading:', url)
    headers = {'User-agent': user_agent or 'wswp'}
    request = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(request).read()
    except urllib.request.URLError as e:
        print('Download error:', e.reason)
        html = None
    return html


if __name__ == '__main__':
    print(download('http://example.webscraping.com'))
