#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/31 10:13
# @Author  : ysl
# @File    : parse.py
# @Software: PyCharm
import re
from loguru import logger
from lxml.html import etree
from config import chinese_punc, default_tag, inspection
from parsel import Selector
from lxml.html.clean import Cleaner


class Parse:
    def __init__(self):
        pass

    @staticmethod
    def node(html):
        select = Selector(text=html)
        return select

    @classmethod
    def xp_re(cls, xp, xp_re):
        """"//span[re:match(@class, '^sho')]/text()"""
        ns = {"re": "http://exslt.org/regular-expressions"}
        content = xp.xpath(xp_re, namespaces=ns)
        return content

    @staticmethod
    def zh_re(html):
        return re.compile(r'[\u4e00-\u9fa5]', re.S).findall(html)

    def dom_tree(self, html):
        """Do some permutations on the dom tree Make your goals clearer
        It still feels flawed and needs to be fixed further"""
        maximum_probability = list()
        n = self.node(html)
        nodes = n.xpath('//div[re:test(@class, "[a-z0-9-]+")]').getall()
        for index, node in enumerate(nodes):
            _all_nb, punc_num_p_all = self.calculate(node)
            all_nb = list(filter(lambda x: x is not None, _all_nb))
            if (len(all_nb) and punc_num_p_all) > 0:
                fst_layer_label = all_nb[0]
                p_num = all_nb.count('p')
                div_num = all_nb.count('div')
                if p_num == 0: continue
                if div_num == 0: div_num = 1
                score = ((p_num / len(all_nb)) * (2 / 5) + punc_num_p_all * (2 / 5)) / (div_num / len(all_nb)) * (1 / 5)
                maximum_probability.append({"score": score, "node": node})
        res = sorted(maximum_probability, key=lambda x: int(x.get('score')), reverse=True)
        top_art = res[0].get('node') if len(res) > 0 else None
        return top_art

    def calculate(self, node):
        all_nb, punc_num_p_all = list(), 0
        result = self.node(node).xpath('//preceding::*').getall()
        for r in result:
            res = re.compile(r'<(div|p).*?>', re.S).findall(r)
            close_neighbour = res[0] if res else None
            if close_neighbour == 'p':
                result = re.findall(chinese_punc, r, re.S)
                punc_num_p_all += len(result)
            all_nb.append(close_neighbour)
        return all_nb, punc_num_p_all

    @classmethod
    def final_quality_inspection(cls, html):
        return html if html and len(cls.zh_re(html)) > inspection else ''

    @staticmethod
    def get_meta(select, nm):
        meta_tags = select.xpath('//meta')
        for tag in meta_tags:
            name_xp = "@name='{}'".format(nm)
            prop_xp = "@property='{}'".format(nm)
            if tag.xpath(name_xp) or tag.xpath(prop_xp):
                return tag.xpath("@content")

    @staticmethod
    def find_lcs(s1, s2):
        # 生成0矩阵，为方便后续计算，比字符串长度多了一列
        m = [[0 for i in range(len(s2) + 1)] for j in range(len(s1) + 1)]
        mmax = 0  # 最长匹配的长度
        p = 0  # 最长匹配对应在s1中的最后一位
        for i in range(len(s1)):
            for j in range(len(s2)):
                if s1[i] == s2[j]:
                    m[i + 1][j + 1] = m[i][j] + 1
                    if m[i + 1][j + 1] > mmax:
                        mmax = m[i + 1][j + 1]
                        p = i + 1
        return s1[p - mmax:p]  # 返回最长子串

    @staticmethod
    def meta_date(select, nms: list):
        values = list()
        for nm in nms:
            name_xp = "//meta[contains(@name, '{}')]//@content".format(nm)
            prop_xp = "//meta[contains(@property, '{}')]//@content".format(nm)
            fff = [select.xpath(name) for name in [name_xp, prop_xp]]
            value = [item for sublist in fff for item in sublist if item]
            values += value
        return values

    @staticmethod
    def process_lac_source(source):
        tm, sc = [], []
        if isinstance(source, tuple):
            soc = source[0]
            if soc:
                for item in soc:
                    for hans, flg in zip(item[0], item[1]):
                        if flg == 'TIME':
                            tm.append(hans)
                        elif flg == 'ORG':
                            sc.append(hans)
        return tm[0] if tm else '', sc[0] if sc else ''

    @staticmethod
    def source_purification(source: list):
        soc = ''.join(source).replace('\u3000', '').replace('举报', '').replace('纠错', '')
        soc_cre = re.compile(r'[\u4e00-\u9fa50-9-:： /]+').findall(soc)
        return soc_cre

    def supplement(self, html, flg):
        com = re.compile(f'</h1>.*?{flg}', re.S)
        return re.findall(r'[\u4e00-\u9fa5]+', com.search(html).group())


if __name__ == '__main__':
    p = Parse()
    print(p.supplement('<div id="content">'))
    # lst = [ ([[['来源：大众报业'], ['ORG']], [['大众日报', '客户端'], ['ORG', 'n']]],),
    #         ([[['来源：胶东在线', '2023-02-25 12:03:51'], ['ORG', 'TIME']], [['-'], ['w']]], ),
    #         ([[['财讯第一看点发布厅发布厅', '第一', '看点'], ['ORG', 'm', 'n']]],),
    #         ([[['新浪新闻综合'], ['ORG']]], ),
    #         ([[['2023-02-03 15:27:28', '来源:新华社', '客户端', '北京'], ['TIME', 'ORG', 'n', 'LOC']]],),
    #         ]
    # for l in lst:
    #     t, s = p.process_lac_source(l)
    #     print(t, s)

"""
div 的第一级别子标签是什么 p  div
</div> 的数量  越少说明越精简越符合要求  （不能单一看这个指标）
<p>标签 汉语的总数   多
<p>标签 汉语标点符号的总数
<p>标签 中是否有img 如果有的话是正文的概率更大
机器学习
对class 的那么进行分类  content  article main 等
"""
