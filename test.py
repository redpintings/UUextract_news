#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : test.py
import requests

url = "http://localhost:8000/extract_plain_text"
data = {
    "url": "https://news.cctv.com/2024/11/10/ARTI1WOIBcN6zmKU0lzbZBTz241110.shtml"
}
response = requests.post(url, json=data)
print(response.json())