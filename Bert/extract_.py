#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : extract.py


from bs4 import BeautifulSoup
import requests
import json


def fetch_webpage(url):
    try:
        response = requests.get(url, timeout=3)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(e)
        return ''


def extract_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.string if soup.title else ''

    # 提取段落和标题
    content = []
    for tag in soup.find_all(['h1', 'h2', 'p']):
        content.append(tag.get_text())

    return title, ' '.join(content)


def load_or_create_data(urls):
    data = []
    for url in urls:
        html = fetch_webpage(url)
        title, content = extract_content(html)
        data.append({'url': url, 'title': title.strip(), 'content': content.strip()})

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data


urls = ['http://www.rmzxb.com.cn/c/2023-02-27/3299508.shtml',
        'https://www.bjnews.com.cn/detail/167740918014982.html',
        'http://news.bandao.cn/a/1697882.html',
        'https://sd.dzwww.com/sdnews/202302/t20230222_11445455.htm',
        'https://www.ql1d.com/general/20855836.html',
        'https://www.163.com/news/article/HSLN5161000189FH.html?clickfrom=w_yw',
        'https://dzrb.dzng.com/articleContent/1176_1111015.html', ]
data = load_or_create_data(urls)

for item in data:
    print(f"URL: {item['url']}")
    print(f"Title: {item['title']}")
    print(f"Content: {item['content']}\n")
