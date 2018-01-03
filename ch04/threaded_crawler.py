import threading
import time
import urllib.parse

from downloader import Downloader

SLEEP_TIME = 1


# 多线程爬虫
def threaded_crawler(seed_url, delay=5, cache=None, scrape_callback=None, user_agent='wswp', proxies=None,
                     num_retries=1, max_threads=3, timeout=60):
    """Crawl this website in multiple threads
    """
    # 未来爬虫队列
    crawl_queue = [seed_url]
    # 已爬URL集合
    seen = set([seed_url])
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries,
                   timeout=timeout)

    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                # 未来爬虫队里已空
                break
            else:
                html = D(url)
                if scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                    except Exception as e:
                        print('Error in callback for: {}: {}'.format(url, e))
                    else:
                        for link in links:
                            link = normalize(seed_url, link)
                            # 检查是否已经爬过
                            if link not in seen:
                                seen.add(link)
                                # 加入未来爬虫队列
                                crawl_queue.append(link)

    # 等待所有下载线程结束
    threads = []
    # 爬虫仍处于激活状态
    while threads or crawl_queue:
        # 遍历线程队列
        for thread in threads:
            # 如果线程死亡
            if not thread.is_alive():
                # 移除线程
                threads.remove(thread)
        # 只要线程少于可容纳线程数量，并且有未来爬虫
        while len(threads) < max_threads and crawl_queue:
            # 可以启动更多线程
            thread = threading.Thread(target=process_queue)
            # 设置TRUE可以在ctrl-C退出线程
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        # 所有线程已经启动
        # 睡眠延时运行其他线程
        time.sleep(SLEEP_TIME)


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urllib.parse.urldefrag(link)  # remove hash to avoid duplicates
    return urllib.parse.urljoin(seed_url, link)
