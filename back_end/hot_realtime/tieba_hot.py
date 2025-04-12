import requests
from bs4 import BeautifulSoup
import json
from cnsenti import Emotion, Sentiment
# from bert_class.predict import TextClassifier

def analyze_sentiment(test_text: str) -> float:
    senti = Sentiment()
    if not test_text:
        return 0.5  # 空文本返回中性情感
    res = senti.sentiment_count(test_text)
    if res["pos"] == res["neg"]:
        return 0.5
    elif res["pos"] > res["neg"]:
        return 1
    else:
        return 0

def fetch_tieba_hot():
    # 目标 URL 和请求头
    url = 'http://tieba.baidu.com/hottopic/browse/topicList?res_type=1&red_tag=n0379530944'
    headers = {'user-agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    html = r.text

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 提取标题、热度和链接
    titles = []
    hotness = []
    links = []

    # 假设标题和链接在 <a> 标签中，热度在 <span> 标签中
    for item in soup.find_all('a', class_='topic-text'):
        title = item.get_text(strip=True)
        link = item['href']
        titles.append(title)
        links.append(link)

    for item in soup.find_all('span', class_='topic-num'):
        hotness.append(item.get_text(strip=True))

    # 创建结果列表
    result = []
    for i in range(len(titles)):
        rank = i + 1
        title = titles[i]
        hot = hotness[i]
        link = links[i]
        sentiment = analyze_sentiment(title)
        # 创建分类器实例
        # classifier = TextClassifier()
        # classifier_result = classifier.classify_text(title)
        result.append({'seq': rank, 'title': title, 'hot': hot, 'url': link, 'sentiment': sentiment})

    # 返回 JSON 数据格式
    return result

# 调用函数并返回 JSON 数据
# json_data = fetch_tieba_hot()
# print(json_data)  # 如果需要，可以去掉这行以便不打印，而是返回数据

