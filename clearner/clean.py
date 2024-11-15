#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : clean.py

import re
import html as ht
from io import BytesIO
import requests
from req import Req
from PIL import Image
from lxml import html
from config import inspection, default_tag_, static_source
from loguru import logger
from collections import Counter
from bs4 import BeautifulSoup
# from extract.parse import Parse
from urllib.parse import urljoin
from config import img_size, static_img
# from parsel import Selector
from lxml.html.clean import Cleaner
from config import chinese_punc, default_tag


class RemoveUseless:
    def __init__(self):
        pass

    @classmethod
    def clean_article_html(cls, htmls):
        """Remove some common styles according to the rules"""
        htmls = cls.clean_jumbled_text(htmls)
        uncommon_tags = cls.complete_transformation(htmls)
        uncommon_tag = Counter(uncommon_tags)
        result = uncommon_tag.most_common(1)
        for _tag, count in result:
            htmls = htmls.replace(_tag, 'div')
        article_cleaner = Cleaner(style=True, javascript=True, remove_unknown_tags=True)
        article_cleaner.javascript = True
        article_cleaner.style = True
        article_cleaner.allow_tags = default_tag
        article_cleaner.remove_unknown_tags = False
        return article_cleaner.clean_html(htmls)

    @staticmethod
    def complete_transformation(htmls):
        soup = BeautifulSoup(htmls, 'html.parser')
        uncommon_tags = list()
        for tag in soup.find_all():
            if tag.name not in default_tag_:
                uncommon_tags.append(tag.name)
        return uncommon_tags

    @staticmethod
    def clean_jumbled_text(htmls):
        for txt in static_source:
            htmls = htmls.replace(txt, '')
        return htmls

    @classmethod
    def second_filter(cls, select, tag, nm, zh_char=''):
        """Only the length judgment is used here for the time being, it should be reasonable to
        calculate a score or classification model for multiple dimensions - consider the loading speed"""
        zh_char_set = list()
        for class_tag in nm:
            xpp = '//*[@{}="{}"]'.format(tag, class_tag)
            uncertainty_node = select.xpath(xpp)
            for n in uncertainty_node:
                string_node = html.tostring(n, encoding='unicode')
                zh_char_set.append({"len": len(cls.zh_hans(string_node)), "node": n, "str": string_node})
        res = sorted(zh_char_set, key=lambda x: int(x.get('len')), reverse=True) if zh_char_set else []
        ratings = [{"index_%s" % tag: index, "score": cls.score(x.get('str')), 'x': x} for index, x in enumerate(res)]
        return ratings

    @classmethod
    def duel(cls, duel_score):
        return sorted(duel_score, key=lambda x: (-x[0], x[1]))[0]

    @classmethod
    def ratings_structured_data(cls, res, index, x) -> dict:
        """xx is a good fun  It is currently deprecated"""
        diff, score = res[0]['len'] - x['len'], cls.score(x.get('str'))
        xx_dit = {"index": index, "score": score, "difference": diff, "str": x['str']}
        return xx_dit

    @classmethod
    def score(cls, node_str):
        unknown_tags = re.findall(r'</[a-z]{1,3}>', node_str, re.S)
        lss = sorted([(len(two), two[0]) for two in cls.count_and_find_tag_p(unknown_tags)], key=lambda x: x[0],
                     reverse=True)
        lss.sort(key=lambda x: x[1])
        for i in range(1, len(lss)):
            if lss[i - 1][0] < lss[i][0] * 2:
                lss[i - 1], lss[i] = lss[i], lss[i - 1]
        return lss[0] if lss else (0, 0)

    @staticmethod
    def count_and_find_tag_p(lst):
        twos = []
        for i in range(len(lst) - 1):
            if lst[i] == '</p>' and lst[i + 1] == '</p>':
                if i == 0 or lst[i - 1] != '</p>':
                    twos.append([i, i + 1])
                else:
                    twos[-1].append(i + 1)
        return twos

    @classmethod
    def id_cls(cls, text, url):
        """
        xpath('//attribute::*')  xpath('//@class | //@id')
        这里只用了score来进行决斗⚔️如果效果不理想， 还可以加入 len值
        """
        from extract.parse import Parse
        article_lst = list()
        _select = cls.tree(text)
        select = cls.img_tag(_select, url)
        gen_tag = [(select.xpath('//@class'), 'class'), (select.xpath('//@id'), 'id')]
        for tag_cls_id, tag_nm in gen_tag:
            article = cls.second_filter(select, tag_nm, tag_cls_id)
            article_lst += article
        duel = sorted(article_lst, key=lambda x: (-x['score'][0], x['score'][1]))
        duel_winner = duel[0].get('x').get('str') if duel else None
        text_end = Parse.final_quality_inspection(duel_winner)
        return text_end

    @classmethod
    def deep_cleanse(cls, text):
        _select = cls.tree(text)
        nodes = _select.xpath('//@class | //@id')
        for node in nodes:
            print(node)

    @classmethod
    def img_tag(cls, element, req_url, upload_pic=False):
        img_s = element.xpath('//img')
        for img in img_s:
            src = img.attrib.get('src')
            src = cls.verify(req_url, src)
            if any(s in src for s in static_img):
                img.attrib['src'] = ''
            else:
                if upload_pic:
                    src = cls.upload_pics(src)
                img.attrib['src'] = src
        return element

    @classmethod
    def upload_pics(cls, src):
        return src

    @staticmethod
    def zh_hans(string_node):
        return re.compile(r'[\u4e00-\u9fa5]').findall(string_node)

    @staticmethod
    def image_recognition(url, status=1):
        # Asking for a link to the image, determining the size of the image, but it's a waste of time
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        if width <= img_size and height <= img_size:
            status = 0
            logger.warning('This is a static resource image: {}'.format(url))
        return status

    @classmethod
    def verify(cls, req_url, src):
        if 'http' in src:
            return src
        return cls.url_join(req_url, src)

    @staticmethod
    def url_join(req_ur: str, link: str):
        return urljoin(req_ur, link)

    @staticmethod
    def tree(text):
        return html.fromstring(text)


if __name__ == '__main__':
    r = RemoveUseless()
