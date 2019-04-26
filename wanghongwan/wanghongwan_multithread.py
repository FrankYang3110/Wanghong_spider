#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import requests
from lxml import etree
from fake_useragent import UserAgent
from urllib.parse import urljoin
from threading import Thread, Lock
from queue import Queue
import os


ua = UserAgent()
headers = {'User-Agent': ua.chrome}
download_page_count = int(input('请输入需要抓取多少页：'))
wanghong_list = []
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wanghong')


def get_document_tree(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        return tree
    else:
        print('download %s failed' % url)


def get_page_count(html):
    tree = etree.HTML(html)
    page_count = int(tree.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()')[0])
    return page_count


def get_wanghong_list(url, queue):
    tree = get_document_tree(url)
    wanghong_infos = tree.xpath('//li[@class="mui-table-view-cell"]')
    for info in wanghong_infos:
        wanghong_dict = {}
        wanghong_dict.update(wanghong_name = info.xpath('./div/a/div/text()')[0].strip())
        wanghong_dict.update(wanghong_form = info.xpath('./div/a/div/p/text()')[0])
        sort_url = info.xpath('./a/@href')[0]
        wanghong_dict.update(wanghong_url = urljoin(url, sort_url))

        queue.put(wanghong_dict)
        print('put a dict')


def download_image(queue, lock):
    while queue.qsize() != 0:
        d = queue.get()
        print('get a dict')
        time.sleep(1)
        url = d.get('wanghong_url')
        tree = get_document_tree(url)
        images = tree.xpath('//div[@class="imgs"]/img/@src')
        for image in images:
            # 用网红的名字和家乡以及图片名称截取作为保存图片的名字
            path_name = d.get('wanghong_name') + '-' + d.get('wanghong_form') + image.split('/')[-1]
            print('start get %s' % image)
            content = requests.get(image).content
            os.makedirs(path) if not os.path.exists(path) else None
            lock.acquire()
            with open('%s/%s' %(path, path_name), 'wb') as file:
                file.write(content)
            lock.release()


def main():
    queue = Queue()
    lock = Lock()
    re_url = 'http://wanghongwan.com/index-{}.html'
    tree = get_document_tree(re_url.format(1))
    page_count = int(tree.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()')[0])

    if download_page_count > page_count:
        print('Total page is %s please re_try.' % page_count)
        exit()

    for i in range(1, download_page_count+1):
        url = re_url.format(i)
        get_wanghong_list(url, queue)
        thread_list = []
        for i in range(20):
            input_thread = Thread(target=download_image, args=(queue, lock))
            thread_list.append(input_thread)
        for thread in thread_list:
            thread.start()


if __name__ == '__main__':
    main()