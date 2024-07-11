#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : source.py
import re
from config import *
from .parse import Parse
from lxml import html as ht
from lxml.html import HtmlElement
from lxml import html as ht


class Source:
    def __str__(self):
        pass

    @staticmethod
    def match(select, res_content=None):
        patterns = [
            '//*[@class="source"]//text()',
            "//*[contains(text(),'来源:')]//text()",
            "//*[contains(text(),'来源：')]//text()",
            '//*[@id="source"]//text()'
        ]
        confusion = []
        for pat in patterns:
            result = select.xpath(pat)
            for sun_string in result:
                if len(sun_string) <= 60:
                    confusion.append(sun_string)
        source_like = [inner_list.strip() for inner_list in confusion]
        return Parse.source_purification(list(set(source_like)))

    @classmethod
    def source(cls, select, nm: list):
        meta_source = Parse.meta_date(select, nm)
        if not meta_source:
            meta_source = cls.match(select)
        # if not meta_source:
        #     meta_source = cls.re_soc()
        return meta_source if isinstance(meta_source, list) else [meta_source]


if __name__ == '__main__':
    import requests

    urls = [
        'http://linyi.sdchina.com/show/4815751.html'
    ]
    html = requests.get(urls[0], headers=USER_AGENT)
    if html.encoding == 'ISO-8859-1':
        html = html.text.encode('ISO-8859-1').decode('utf-8')
    else:
        html = html.text
    d = Source()
    tree = ht.fromstring(html=html)
    print(d.source(tree, ['source']))
