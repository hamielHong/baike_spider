#coding:utf-8
from multiprocessing.pool import Pool

from multiprocessing import Queue, Process, Lock

import url_manager,html_downloader,html_parser,html_outputer
import time, multiprocessing, os


url_buffer = Queue()
data_buffer = Queue()
lock = Lock()
outputer = html_outputer.HtmlOutputer()
root_url = "http://baike.baidu.com/view/21087.htm"
url_buffer.put(root_url)

class SpiderProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()

    def run(self):
        global url_buffer, data_buffer, lock
        count = 0
        while count < 25:
            if not url_buffer.empty():
                lock.acquire()
                lockb = True
                try:
                    new_url = url_buffer.get()
                    lock.release()
                    lockb = False
                    content = self.downloader.download(new_url)
                    new_urls, new_data = self.parser.parse(new_url, content)
                    lock.acquire()
                    lockb = True
                    url_buffer.put(new_urls)
                    data_buffer.put(new_data)
                    lock.release()
                    lockb = False
                    print('Process(%s) craw %d : %s' % (os.getpid(), count, new_url))
                    count += 1


                except Exception as e:
                    print('failed! : %s' % (e))

                finally:
                    if lockb:
                        lock.release()

        print('Process(%s) exit.' % (os.getpid()))


if __name__ == "__main__":

    start = time.time()
    #root_url = "http://baike.baidu.com/view/21087.htm"
    #url_buffer.put(root_url)
    pool = []
    for i in range(2):
        process = SpiderProcess()
        process.start()
        pool.append(process)

    for process in pool:
        process.join()

    while not data_buffer.empty():
        new_data = data_buffer.get()
        outputer.collect_data(new_data)

    try:
        outputer.output_html()
    except Exception as e:
        print(e)

    print('Main Process Exit.')

    end = time.time()
    print("cost all time: %s" % (end-start))