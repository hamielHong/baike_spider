#coding:utf-8
from multiprocessing.pool import Pool

from multiprocessing import Queue, Process

import url_manager,html_downloader,html_parser,html_outputer
import time, multiprocessing, os

class SpiderMain(object):
    def __init__(self, func):
        self.func = func
        self.buffer = Queue()
        self.databuffer = Queue()
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.lock = multiprocessing.Lock()

    def process_url(self):
        count = 0
        while count < 100:
            if self.urls.has_new_url():
                self.lock.acquire()
                self.buffer.put(self.urls.get_new_url())
                self.lock.release()
                count += 1

    def craw_test(self):
        try:
            new_url = self.buffer.get()

            content = self.downloader.download(new_url)
            new_urls, new_data = self.parser.parse(new_url, content)

            for url in new_urls:
                self.buffer.put(url)
                print(url)
            self.databuffer.put(new_data)




        except Exception as e:
            print('failed! : %s' % (e))

    def process_craw(self):
        count = 0
        while count < 25:
            if not self.buffer.empty():

                try:
                    new_url = self.buffer.get()

                    content = self.downloader.download(new_url)
                    new_urls, new_data = self.parser.parse(new_url, content)

                    for url in new_urls:
                        self.buffer.put(url)
                    self.databuffer.put(new_data)

                    print('(%s) craw %d : %s' % (os.getpid(), count, new_url))
                    count += 1

                except Exception as e:
                    print('failed! : %s' % (e))

        print('(%s) exit.' % (os.getpid()))

    def run_spider(self, n, root_url):
        self.buffer.put(root_url)

        # pool = []
        # for i in range(2):
        #     process = Process(target=self.process_craw)
        #     process.start()
        #     process.join()


        p = Pool(n)
        #p.map(self.process_craw, range(n))
        for i in range(n):
            p.apply_async(process_craw, args=(self,))

        p.close()
        p.join()


        while not self.databuffer.empty():
            new_data = self.databuffer.get()
            self.outputer.collect_data(new_data)

        try:
            self.outputer.output_html()
        except Exception as e:
            print(e)

        print('Main Process Exit.')

def process_craw(cls_instance):
    return cls_instance.process_craw()

if __name__ == "__main__":
    start = time.time()
    root_url = "http://baike.baidu.com/view/21087.htm"
    object_spider = SpiderMain(process_craw)
    object_spider.run_spider(2, root_url)
    end = time.time()
    print("cost all time: %s" % (end-start))