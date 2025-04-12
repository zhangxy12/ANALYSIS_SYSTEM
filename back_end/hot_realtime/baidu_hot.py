import requests
from bs4 import BeautifulSoup
from cnsenti import Emotion, Sentiment

# from bert_class.predict import TextClassifier


def analyze_sentiment(test_text: str) -> float:
    senti = Sentiment()
    if not test_text:
        return 0.5  # 空文本返回中性情感
    res = senti.sentiment_count(test_text)
    print(res)
    if res["pos"] == res["neg"]:
        return 0.5
    elif res["pos"] > res["neg"]:
        return 1
    else:
        return 0


def fetch_baidu_hot():
    """
    爬取百度热搜榜数据，返回 JSON 格式的结果。

    :return: 包含热搜数据的列表，每项包括标题、热度指数和链接。
    """
    url = 'http://top.baidu.com/buzz?b=1&fr=topindex'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    # 发送 HTTP GET 请求
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()  # 检查状态码是否成功
    r.encoding = r.apparent_encoding  # 自动设置编码

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(r.text, 'html.parser')

    # 查找标题列表、热度指数和链接
    title_list = soup.find_all(attrs={'class': 'c-single-text-ellipsis'})
    hot_list = soup.find_all(attrs={'class': 'hot-index_1Bl1a'})
    link_list = soup.find_all('a', class_='title_dIF3B')  # 提取 <a> 标签

    # 确保三个列表长度一致
    length = min(len(title_list), len(hot_list), len(link_list))
    result = []

    # 生成 JSON 数据
    for j in range(length):
        title = title_list[j].get_text(strip=True)  # 获取标题文本
        hot_index = hot_list[j].get_text(strip=True)  # 获取热度指数
        link = link_list[j].get('href', '')  # 提取链接，默认值为空字符串
        sentiment = analyze_sentiment(title)
        # 创建分类器实例
        # classifier = TextClassifier()
        # classifier_result = classifier.classify_text(title)
        result.append({
            "seq": j + 1,
            "title": title,
            "hot_index": hot_index,
            "url": link,
            'sentiment': sentiment,
            # "classifier_result": classifier_result
        })

    return result


if __name__ == "__main__":
    data = fetch_baidu_hot()
    import json

    print(json.dumps(data, ensure_ascii=False, indent=4))
