import re
from lxml import etree
import re
from bs4 import BeautifulSoup
from config import chinese_punc, inspection
from parsel import Selector


class Parse:
    def __init__(self):
        pass

    @staticmethod
    def node(html):
        select = Selector(text=html)
        return select

    @staticmethod
    def zh_re(html):
        return re.compile(r'[\u4e00-\u9fa5]', re.S).findall(html)

    def dom_tree(self, html):
        """改进后的 DOM 树分析方法"""
        maximum_probability = list()
        n = self.node(html)
        nodes = n.xpath('//div|//article|//section').getall()
        for index, node in enumerate(nodes):
            _all_nb, punc_num_p_all = self.calculate(node)
            all_nb = list(filter(lambda x: x is not None, _all_nb))
            if (len(all_nb) and punc_num_p_all) > 0:
                p_num = all_nb.count('p')
                if p_num == 0: continue
                score = self.calculate_score(node, p_num, punc_num_p_all)
                maximum_probability.append({"score": score, "node": node})
        res = sorted(maximum_probability, key=lambda x: int(x.get('score')), reverse=True)
        top_art = res[0].get('node') if len(res) > 0 else None
        return top_art

    def calculate(self, node):
        all_nb, punc_num_p_all = list(), 0
        result = self.node(node).xpath('.//*').getall()
        for r in result:
            res = re.compile(r'<(div|p|article|section).*?>', re.S).findall(r)
            close_neighbour = res[0] if res else None
            if close_neighbour == 'p':
                result = re.findall(chinese_punc, r, re.S)
                punc_num_p_all += len(result)
            all_nb.append(close_neighbour)
        return all_nb, punc_num_p_all

    def calculate_score(self, node, p_num, punc_num_p_all):
        div_num = node.count('<div')
        article_num = node.count('<article')
        section_num = node.count('<section')
        total_div = div_num + article_num + section_num
        if total_div == 0:
            total_div = 1
        score = ((p_num / total_div) * (2 / 5) + punc_num_p_all * (2 / 5)) / (total_div / p_num) * (1 / 5)
        return score

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

    @staticmethod
    def extract_js_text(html):
        # Step 1: Use regex to find all consecutive <p> tags in the HTML
        paragraph_blocks = re.findall(r'(<p.*?>.*?/p>)', html, re.DOTALL)

        # Step 2: Initialize the main content text
        main_content = ""
        for block in paragraph_blocks:
            # Parse the block with BeautifulSoup
            soup = BeautifulSoup(block, 'html.parser')

            # Extract and clean the text from each <p> tag within the block
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

            # Concatenate paragraphs if they form a large enough block to be considered main content
            block_text = "\n\n".join(paragraphs)
            if len(block_text) > 100:  # Adjust the length threshold as needed
                main_content += block_text + "\n\n"

        # Step 3: Final clean-up to remove any remaining HTML or JS artifacts
        clean_text = re.sub(r'\s+', ' ', main_content).strip()
        return clean_text
