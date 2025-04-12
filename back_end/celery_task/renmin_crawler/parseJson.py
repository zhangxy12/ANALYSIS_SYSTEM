
import time                            # 处理时间戳
from bs4 import BeautifulSoup


def parseJson(jsonObj):
    """解析JSON数据并返回字典列表"""
    records = jsonObj["data"]["records"]
    parsed_data = []

    for item in records:
        # 解析每条记录
        pid = item["id"]
        author = item["author"]
        originName = item["originName"]
        belongsName = item["belongsName"]
        content = BeautifulSoup(item["content"], "html.parser").text
        displayTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["displayTime"] / 1000))
        subtitle = item["subtitle"]
        title = BeautifulSoup(item["title"], "html.parser").text
        url = item["url"]

        # 将每条记录存储为字典
        record = {
            "pid": pid,
            "title": title,
            "subtitle": subtitle,
            "author": author,
            "displayTime": displayTime,
            "originName": originName,
            "belongsName": belongsName,
            "content": content,
            "url": url
        }

        parsed_data.append(record)  # 将字典添加到列表中

    return parsed_data  # 返回字典列表
