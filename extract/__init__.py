#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Time    : 2023/2/14 14:41
# @Author  : ysl
# @File    : __init__.py.py
import re
from extract.parse import Parse
from extract.title import Title
from date import Date
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
            article, text = self.ns.extract(url=url, html=html, **kwargs)
            node = htl.fromstring(text)
            tit = Title.summarize(node)
            media_info = Source.source(node, ['source'])
            tm = Date.extract_date(text, node)
            uu_result = {
                "title": tit,
                "date": tm,
                "source": media_info,
                "article": article
            }
            from gne import GeneralNewsExtractor
            html_ = text
            extractor = GeneralNewsExtractor()
            gen_result = extractor.extract(html_, noise_node_list=['//div[@class="comment-list"]'])
            print('uu_result', uu_result)
            print('gen_result', gen_result)
        except Exception as er:
            print(er)


if __name__ == '__main__':
    from example.links import urls
    u = UU()
    # urls = [
    #     'http://www.caheb.gov.cn/system/2023/05/04/030224852.shtml',
    #     'https://www.thepaper.cn/newsDetail_forward_22896216',
    #     'https://www.jiemian.com/article/9369085.html',
    #     'http://fjnews.fjsen.com/2023-05/14/content_31314474.htm',
    #     'http://linyi.sdchina.com/show/4815751.html',
    #     'https://wh.zibo.gov.cn/gongkai/channel_c_5f9fa491ab327f36e4c13060_n_1605682651.0101/doc_6593b42151e0885ffbe043ce.html'
    # ]

    # urls = ['https://sd.dzwww.com/sdnews/202303/t20230321_11583301.htm']
    for ul in urls:
        print('url', ul)
        u.uu(url=ul)
        print('*' * 50)
