import random
import socket
import time
import urllib.parse
import urllib.request
from datetime import datetime

DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60


class Downloader:
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES,
                 timeout=DEFAULT_TIMEOUT, opener=None, cache=None):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.opener = opener
        self.cache = cache

    # 下载前检查缓存
    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # URL不在cache中存储
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    # 服务器错误重新下载
                    result = None
        if result is None:
            # 不存在获取的URL结果所以重新下载
            # 延时等待
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            # 获取下载结果
            result = self.download(url, headers, proxy=proxy, num_retries=self.num_retries)
            # 存在cache存储情况下
            if self.cache:
                # 将cache字典中URL项赋值result，缓存
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy, num_retries, data=None):
        print('Downloading:', url)
        request = urllib.request.Request(url, data, headers or {})
        opener = self.opener or urllib.request.build_opener()
        if proxy:
            proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib.request.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except Exception as e:
            print('Download error:', str(e))
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    return self._get(url, headers, proxy, num_retries - 1, data)
            else:
                code = None
        # 返回HTTP状态码
        return {'html': html, 'code': code}


# 安全延时
class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """

    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urllib.parse.urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
