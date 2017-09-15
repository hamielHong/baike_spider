#coding:utf-8
from baike_spider import url_manager,html_downloader,html_parser,html_outputer
import time, threading

class SpiderMain(object):
    def __init__(self):
        self.count = 1
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.lock = threading.Lock()

    def thread_craw(self):
        while self.count < 100:

            if self.urls.has_new_url():
                self.lock.acquire()
                lockb = True
                try:
                    new_url = self.urls.get_new_url()
                    self.lock.release()
                    lockb = False
                    content = self.downloader.download(new_url)
                    new_urls, new_data = self.parser.parse(new_url, content)
                    self.lock.acquire()
                    lockb = True
                    self.urls.add_new_urls(new_urls)
                    self.outputer.collect_data(new_data)
                    self.lock.release()
                    lockb = False
                    print('%s craw %d : %s' % (threading.current_thread().name, self.count, new_url))
                    self.lock.acquire()
                    lockb = True
                    self.count += 1
                    self.lock.release()
                    lockb = False
                    if self.count > 100:
                        break
                except Exception as e:
                    print('failed! : %s' % (e))

                finally:
                    if lockb:
                        self.lock.release()
                    if self.count > 100:
                        break


        print('%s exit.' % (threading.current_thread().name))

    def run_spider(self, n, root_url):
        self.urls.add_new_url(root_url)
        threads = []
        for i in range(n):
            thread = threading.Thread(target=self.thread_craw)
            thread.start()  # 线程开始处理任务
            threads.append(thread)

        for thread in threads:
            thread.join()

        try:
            self.outputer.output_html()
        except Exception as e:
            print(e)

        print('Main thread exit.')


if __name__ == "__main__":
    start = time.time()
    root_url = "http://baike.baidu.com/view/21087.htm"
    object_spider = SpiderMain()
    object_spider.run_spider(4, root_url)
    end = time.time()
    print("cost all time: %s" % (end-start))