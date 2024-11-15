#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : news.py

import re
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

    def end_plain_text(self, list_html, **kwargs):
        end_text = ''.join(list_html).replace('\\n', '').replace('\\r', '').replace('\\t', '').replace(' ', '').replace(
            '\xa0', '').replace('\u3000', '').replace('\u200b', '').replace('\u200e', '').replace('\u200c', '')
        return end_text

    def match_all_sentences(self, sent):
        # re.findall(r'<[\s.]*?>.*?</.*?>', )
        pass

    def extract(self, html='', url='', **kwargs):
        if url:
            original_html = self.get_html(url, **kwargs)  # 保存原始的 HTML
            html = self.cln.clean_jumbled_text(original_html)  # 处理后的 HTML
        else:
            original_html = html  # 如果没有 URL，则原始 HTML 就是传入的 HTML
            html = self.cln.clean_jumbled_text(original_html)
        resp = self.clearn_tag(html)
        if len(resp) < inspection:
            logger.warning('解析失败！！！!!!')
            return
        res = self.parse.dom_tree(resp)
        if res is None:
            dd = Parse.extract_js_text(original_html)
            return dd, original_html, dd
        article = self.sec_clearn_tag(res, url)
        article = ht.unescape(article)
        _plain_text = self.parse.node(article).xpath("//text()").getall()
        plain_text = self.end_plain_text(_plain_text)
        return article, html, plain_text
