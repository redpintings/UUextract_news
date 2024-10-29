#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : title.py

import re
import requests
from lxml import etree
from config import *
from .parse import Parse


class Title:
    def __init__(self):
        pass

    @staticmethod
    def meta_title(all_html_node):
        meta_tit = Parse.get_meta(all_html_node, 'title')
        return meta_tit[0] if meta_tit else ''

    @staticmethod
    def tag(node, nm):
        xp = f'//{nm}/text()'
        return node.xpath(xp)

    @staticmethod
    def clear(tit):
        if len(tit) <= 5:
            return tit
        lst = re.split(title_clearn_flg, tit)
        new_list = [k for k in lst if len(k) > 5 and '新闻' not in k and '网' not in k]
        return '-'.join(new_list) if new_list else tit

    @classmethod
    def h1_title(cls, all_html_node):
        for t in title:
            yield cls.tag(all_html_node, t)

    @staticmethod
    def lcs_match(tle):
        tle = [t.strip() for t in tle if t.strip()]
        if len(tle) > 1:
            lcs = Parse.find_lcs(tle[-1], tle[-2])
            return tle[-1] if len(lcs) < 5 else lcs
        else:
            return tle[0]

    @classmethod
    def summarize(cls, all_html_node):
        tle = list()

        # Extract titles from meta tags
        meta_title = cls.meta_title(all_html_node)
        if meta_title:
            tle.append(meta_title)

        # Extract titles from common header tags
        for t in cls.h1_title(all_html_node):
            if t:
                tle.insert(0, t[0])

        # Extract titles from title tag
        title_tag = cls.tag(all_html_node, 'title')
        if title_tag:
            tle.insert(0, title_tag[0])

        return cls.clear(cls.lcs_match(tle))

    def mode(self):
        pass


if __name__ == '__main__':
    urls = ['http://news.youth.cn/gn/202302/t20230227_14347287.htm']
    for url in urls:
        response = requests.get(url, headers=USER_AGENT)
        response.encoding = response.apparent_encoding  # 自动检测编码
        html = response.text
        tree = etree.HTML(html)
        tt = Title()
        print(tt.summarize(tree))
