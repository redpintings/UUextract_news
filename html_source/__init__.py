#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : __init__.py.py
import requests

cookies = {
    'tt_webid': '7342795511718299188',
    '_S_DPR': '1',
    '_S_IPAD': '0',
    'odin_tt': '0beb745c5892f98b80cab34aca4439654d179877cbad22c50366be05cc181ec1be2b6475d2ac82dab00cc0db2adbdc5a',
    's_v_web_id': 'verify_m2vbkun0_EBrOCrjD_jgiI_4B1P_9mkV_vK6o26xCMRBW',
    '_ga': 'GA1.1.2145235394.1730259076',
    'local_city_cache': '%E6%B5%8E%E5%8D%97',
    'csrftoken': 'a56b417489ace289224811d0e10869fa',
    '_S_WIN_WH': '1920_273',
    'tt_anti_token': 'gG74vaJhNN7iRVS-fda49bb53e57816eb6cf700f2989eaf3db10b34aa7ccc303aed1aab4adb468b8',
    'gfkadpd': '24,6457',
    'tt_scid': 'nFW2Pp7q5kAkBlIkTWSRPRgonZp56UvB5zYihnsEgJ9FPsV3VkuM03DA5XK-UoFS1619',
    'ttwid': '1%7CcTccC7yXOv4-oX1enlzBy_Lz1NXfsrcxuD0JluXGRFY%7C1731308342%7Cf1f42e49f4fcbeaac901d743ff2b2512770055ed8bc4c48f9df6de415bf94697',
    '_ga_QEHZPBE5HH': 'GS1.1.1731308278.7.1.1731308356.0.0.0',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh,zh-HK;q=0.9,zh-CN;q=0.8',
    'cache-control': 'max-age=0',
    # 'cookie': 'tt_webid=7342795511718299188; _S_DPR=1; _S_IPAD=0; odin_tt=0beb745c5892f98b80cab34aca4439654d179877cbad22c50366be05cc181ec1be2b6475d2ac82dab00cc0db2adbdc5a; s_v_web_id=verify_m2vbkun0_EBrOCrjD_jgiI_4B1P_9mkV_vK6o26xCMRBW; _ga=GA1.1.2145235394.1730259076; local_city_cache=%E6%B5%8E%E5%8D%97; csrftoken=a56b417489ace289224811d0e10869fa; _S_WIN_WH=1920_273; tt_anti_token=gG74vaJhNN7iRVS-fda49bb53e57816eb6cf700f2989eaf3db10b34aa7ccc303aed1aab4adb468b8; gfkadpd=24,6457; tt_scid=nFW2Pp7q5kAkBlIkTWSRPRgonZp56UvB5zYihnsEgJ9FPsV3VkuM03DA5XK-UoFS1619; ttwid=1%7CcTccC7yXOv4-oX1enlzBy_Lz1NXfsrcxuD0JluXGRFY%7C1731308342%7Cf1f42e49f4fcbeaac901d743ff2b2512770055ed8bc4c48f9df6de415bf94697; _ga_QEHZPBE5HH=GS1.1.1731308278.7.1.1731308356.0.0.0',
    'priority': 'u=0, i',
    'referer': 'https://www.toutiao.com/?channel=finance&source=tuwen_detail',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}

params = {
    'log_from': '5acf4e3735544_1731308278882',
}

response = requests.get('https://www.toutiao.com/article/7434608715729011210/', params=params, headers=headers)
print(response.text)