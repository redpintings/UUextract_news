#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : config.py

import user_agent

charset_type = ['utf-8', 'utf8', 'UFT-8', 'gbk', 'gb2312', 'ISO-8859-1']
USER_AGENT = {"user-agent": user_agent.generate_user_agent()}
chinese_punc = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]'
pattern = r'\d{4}[-/]\d{2}[-/]\d{2}\s*\d{2}:\d{2}|\d{4}年\d{2}月\d{2}日|\d{4}\.\d{2}\.\d{2}|\d{4}/\d{1,2}/\d{1,2} \d{2}:\d{2}'
default_tag = ['span', 'p', 'br', 'strong', 'b', 'code', 'img', 'h1', 'h1', 'dl', 'dt', 'div']
default_tag_ = ['a', 'script', 'meta', 'link', 'li', 'i', 'html', 'body', 'input'] + default_tag
static_img = ['static', 'logo', '200.j', "300.j"]
static_source = ['图片来源']
date = ['date', 'create_at', 'published_time', 'time', 'pubtime']
meta_ = ['og:title']
title = ['h1', 'title']
title_clearn_flg = '_|-|——|――'
inspection = 20
img_size = 400
lcs_tit_len = 5
