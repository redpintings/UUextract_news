#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : req.py

import chardet
import requests
from config import *


class Req:
    def __init__(self, url='', headers=USER_AGENT):
        self.url = url
        self.headers = headers
        self.charset = 'utf-8'

    def req(self, url, **kwargs):
        resp_obj = requests.get(url, headers=dict(self.headers, **kwargs), timeout=5)
        encoding = chardet.detect(resp_obj.content).get('encoding')
        resp_obj.encoding = encoding if encoding else self.charset
        return resp_obj.text

    @staticmethod
    def resp_type(response, tp=0):
        if "json" in response.headers.get("Content-Type"):
            return tp
        return tp == 1


if __name__ == '__main__':
    req = Req(url='')
    resp = req.req('https://ckxxapp.ckxx.net/pages/2024/11/08/968304f76c12473bacd71f09d6217da2.html')
    print(resp)