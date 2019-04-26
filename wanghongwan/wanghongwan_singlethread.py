#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
from lxml import etree
from fake_useragent import UserAgent
from urllib.parse import urljoin
import os


ua = UserAgent()
headers = {'User-Agent': ua.chrome}
download_page_count = 10
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


def get_wanghong_list(url):
    global wanghong_list
    tree = get_document_tree(url)
    wanghong_infos = tree.xpath('//li[@class="mui-table-view-cell"]')
    for info in wanghong_infos:
        wanghong_dict = {}
        wanghong_dict.update(wanghong_name = info.xpath('./div/a/div/text()')[0].strip())
        wanghong_dict.update(wanghong_form = info.xpath('./div/a/div/p/text()')[0])
        sort_url = info.xpath('./a/@href')[0]
        wanghong_dict.update(wanghong_url = urljoin(url, sort_url))
        wanghong_list.append(wanghong_dict)


def download_image(list):
    for d in list:
        url = d.get('wanghong_url')
        tree = get_document_tree(url)
        images = tree.xpath('//div[@class="imgs"]/img/@src')
        for image in images:
            path_name = d.get('wanghong_name') + '-' + d.get('wanghong_form') + image.split('/')[-1]
            print('start get %s' % image)
            content = requests.get(image).content
            os.makedirs(path) if not os.path.exists(path) else None
            with open('%s/%s' %(path, path_name), 'wb') as file:
                file.write(content)


def main():
    re_url = 'http://wanghongwan.com/index-{}.html'
    tree = get_document_tree(re_url.format(1))
    page_count = int(tree.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()')[0])
    if download_page_count > page_count:
        print('Total page is %s please re_input.' % page_count)
    for i in range(1, download_page_count+1):
        url = re_url.format(i)
        get_wanghong_list(url)
        download_image(wanghong_list)


if __name__ == '__main__':
    main()