# -*- coding: utf-8 -*-
import os
import re
import shutil
import urllib.parse
import zlib
from datetime import datetime, timedelta

try:
    import cPickle as pickle
except ImportError:
    import pickle
from link_crawler import link_crawler


class DiskCache:
    """
    Dictionary interface that stores cached 
    values in the file system rather than in memory.
    The file path is formed from an md5 hash of the key.

    >>> cache = DiskCache()
    >>> url = 'http://example.webscraping.com'
    >>> result = {'html': '...'}
    >>> cache[url] = result
    >>> cache[url]['html'] == result['html']
    True
    >>> cache = DiskCache(expires=timedelta())
    >>> cache[url] = result
    >>> cache[url]
    Traceback (most recent call last):
     ...
    KeyError: 'http://example.webscraping.com has expired'
    >>> cache.clear()
    """

    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
        """
        cache_dir: 缓存的根文件夹
        expires: 缓存过期时间，默认30天
        compress: 是否压缩
        """
        self.cache_dir = cache_dir
        self.expires = expires
        self.compress = compress

    # 从磁盘获取URL相关数据
    def __getitem__(self, url):
        """Load data from disk for this URL
        """
        # 获取URL缓存地址
        path = self.url_to_path(url)
        # 看是否存在
        if os.path.exists(path):
            # 存在就读取
            with open(path, 'rb') as fp:
                data = fp.read()
                # 如果数据是压缩的
                if self.compress:
                    # 解压
                    data = zlib.decompress(data)
                # 获取缓存数据和缓存时间
                result, timestamp = pickle.loads(data)
                # 如果缓存已经过期
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                return result
        else:
            # 该URL地址尚未缓存，返回错误异常
            raise KeyError(url + ' does not exist')

    # 添加URL缓存
    def __setitem__(self, url, result):
        """Save data to disk for this url
        """
        # 获取正确缓存地址
        path = self.url_to_path(url)
        # 获取缓存地址的母文件夹名称
        folder = os.path.dirname(path)
        # 判定是否存在该文件夹
        if not os.path.exists(folder):
            # 不存在就创建该文件夹
            os.makedirs(folder)
        # 将缓存数据附加上时间戳
        data = pickle.dumps((result, datetime.utcnow()))
        # 确定是否需要压缩
        if self.compress:
            # 需要就压缩
            data = zlib.compress(data)
        # 将数据缓存
        with open(path, 'wb') as fp:
            fp.write(data)

    # 删除URL缓存
    def __delitem__(self, url):
        """Remove the value at this key and any empty parent sub-directories
        """
        path = self._key_path(url)
        try:
            os.remove(path)
            os.removedirs(os.path.dirname(path))
        except OSError:
            pass

    # 获取URL缓存文件地址
    def url_to_path(self, url):
        """Create file system path for this URL
        """
        components = urllib.parse.urlsplit(url)
        path = components.path
        # 限定尾缀
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        # 组合名字
        filename = components.netloc + path + components.query
        # 清除无效不规则字符
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        # 限定最大长度
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    # 检测是否过期
    def has_expired(self, timestamp):
        """Return whether this timestamp has expired
        """
        return datetime.utcnow() > timestamp + self.expires

    # 清空所有缓存
    def clear(self):
        """Remove all the cached values
        """
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/(places/default/index|places/default/view)', cache=DiskCache())
