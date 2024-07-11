#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/31 10:14
# @Author  : ysl
# @File    : news.py
import re
# @Software: PyCharm
import html as ht
from req import *
from loguru import logger
from clearner.clean import RemoveUseless
from extract.parse import *


class News:
    def __init__(self):
        self.parse = Parse()
        self.cln = RemoveUseless
        self.req = Req()

    def clearn_tag(self, html):

        new_html = self.cln.clean_article_html(html)
        return new_html

    def sec_clearn_tag(self, html, url):
        """Remove unwanted tags from articles"""
        new_html = self.cln.id_cls(html, url)
        final = self.parse.final_quality_inspection(new_html)
        return final

    def get_html(self, url, **kwargs):
        response = self.req.req(url, **kwargs)
        return response

    def match_all_sentences(self, sent):
        # re.findall(r'<[\s.]*?>.*?</.*?>', )
        pass

    def extract(self, html='', url='', **kwargs):
        if url:
            html = self.get_html(url, **kwargs)
        html = self.cln.clean_jumbled_text(html)
        resp = self.clearn_tag(html)
        if len(resp) < inspection:
            logger.warning('解析失败！！！')
            return
        res = self.parse.dom_tree(resp)
        article = self.sec_clearn_tag(res, url)
        return ht.unescape(article), html