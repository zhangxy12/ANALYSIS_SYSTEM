'''
用于发起网络请求
url : Request Url
kw  : Keyword
page: Page number
'''
import requests						# 发起网络请求

import json			# 用来解析json文本

def fetchUrl(url, kw, page):
    # 请求头
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    # 请求参数
    payloads = {
        "endTime": 0,
        "hasContent": True,
        "hasTitle": True,
        "isFuzzy": True,
        "key": kw,
        "limit": 10,
        "page": page,
        "sortType": 2,
        "startTime": 0,
        "type": 0,
    }

    # 发起 post 请求
    r = requests.post(url, headers=headers, data=json.dumps(payloads))
    return r.json()
