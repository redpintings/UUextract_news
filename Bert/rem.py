import os
import json
import requests
from loguru import logger
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from lxml import etree
import torch
from example import url_set
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments


def extract_title(html):
    tree = etree.HTML(html)
    if tree:
        title = tree.xpath('//title/text()')
        return title[0] if title else ''
    else:
        return ""


def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style']):
        script.extract()
    text = soup.get_text(separator=' ')
    return ' '.join(text.split())


def replace_html(html):
    return (html.replace_html('\n', '').replace_html('\t', '').
            replace_html('\r', '').replace_html('  ', '').
            replace_html('&nbsp;', '').replace_html('&amp;', '&'))


def load_or_create_data(name='model_data.json'):
    cleaned_data = []
    if os.path.exists(name):
        with open(name, 'r') as md:
            mds = md.readlines()
            for item in mds:
                item_dict = json.loads(item)
                content = item_dict.get('content')
                html = item_dict.get('html')
                itm = {
                    'url': item_dict.get('url'),
                    'title': item_dict.get('url'),
                    'content': replace_html(content) if content else '',
                    "html": replace_html(html) if html else ''}
                print(itm)
                cleaned_data.append(itm)
    with open('model_cleaned_data.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
