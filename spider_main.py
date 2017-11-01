import time
import threading
import queue
import url_manager, html_downloader, html_parser, html_outputer


class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    def craw(self, root_url):
        self.urls.add_new_url(root_url)
        count = 1
        try:
            while self.urls.has_new_url():
                new_url = self.urls.get_new_url()
                content = self.downloader.download(new_url)
                new_urls, new_data = self.parser.parse(new_url, content)
                self.urls.add_new_urls(new_urls)
                self.outputer.collect_data(new_data)
                print(count, new_url)
                if count > 20:
                    break
                count += 1
        except Exception as e:
            print(e)
            print("download fail")
        self.outputer.output_html()

if __name__ == "__main__":
    start = time.time()

    root_url = "https://baike.baidu.com/item/Python"
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)

    end = time.time()
    print('time cost : %s' % (end - start))