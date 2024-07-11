#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/1 17:41
# @Author  : ysl
# @File    : date.py

from datetime import datetime
import re
import requests
from lxml import etree

# 日期格式的正则表达式模式
date_patterns = [
    r'\b\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\b',  # 2023-03-01, 2023/03/01, 2023年03月01日
    r'\b\d{1,2}[-/月]\d{1,2}日?[-/年]\d{4}\b',  # 01-03-2023, 01/03/2023, 01月03日2023年
    r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2}\b',  # 01-03-23, 01/03/23
    r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'  # 01-03-2023, 01/03/2023
]


class Date:
    """
    日期提取器, 主要从html中提取日期信息
    """

    @staticmethod
    def meta_date(select, meta_names):
        for name in meta_names:
            meta_tags = select.xpath(f"//meta[contains(@name, '{name}') or contains(@property, '{name}')]//@content")
            if meta_tags:
                return meta_tags[0]
        return None

    @staticmethod
    def find_date_in_text(text):
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    @classmethod
    def extract_date(cls, html_text, select):
        meta_names = ['date', 'pubdate', 'publishdate', 'pubDate', 'PublishDate', 'PubDate']
        date = cls.meta_date(select, meta_names)
        if not date:
            date = cls.find_date_in_text(html_text)
        return date


if __name__ == '__main__':
    urls = [
        "http://www.tibet.cn/cn/index/politics/polotocs1/202302/t20230227_7368139.html"
    ]
    for url in urls:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # 检查请求是否成功
            html_text = response.text
            tree = etree.HTML(html_text)
            extractor = Date()
            extracted_date = extractor.extract_date(html_text, tree)
            print(f"URL: {url}\nExtracted Date: {extracted_date}\n")
        except requests.RequestException as e:
            print(f"Failed to retrieve URL {url}: {e}")
