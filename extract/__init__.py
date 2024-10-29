#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 14:41
# @Author  : ysl
# @File    : __init__.py.py
import re
from extract.parse import Parse
from extract.title import Title
from .date import Date
from extract.source import Source
from extract.news import News
from lxml import html as htl
from example import url_set


class UU:

    def __init__(self):
        self.ns = News()
        self.date = Date()
        # self.lac = LAC(model_path='../computer/my_lac_model')

    def __str__(self):
        return 'Parsing news pages!'

    def contains_chinese(self, s):
        """
        判断字符串是否包含中文字符
        """
        pattern = re.compile(r'[\u4e00-\u9fa5]')
        return bool(pattern.search(s))

    def uu(self, html='', url='', **kwargs):
        try:
            article, text, plain_text = self.ns.extract(url=url, html=html, **kwargs)
            node = htl.fromstring(text)
            tit = Title.summarize(node)
            media_info = Source.source(node, ['source'])
            tm = Date.extract_date(text, node)
            uu_result = {
                "title": tit,
                "date": tm,
                "source": media_info,
                "article": article,
                "plain_text": plain_text,
                "html": text
            }
            return uu_result
        except Exception as er:
            print(er)


