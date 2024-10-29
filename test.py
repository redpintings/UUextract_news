#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : test.py
import requests

url = "http://localhost:8000/extract_plain_text"
data = {
    "url": "https://www.ql1d.com/general/25003407.html"
}
response = requests.post(url, json=data)
print(response.json())