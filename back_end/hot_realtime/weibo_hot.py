import requests
from urllib.parse import quote
from datetime import datetime

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


def hot_search():
    url = 'https://weibo.com/ajax/side/hotSearch'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()['data']

def fetch_weibo_hot():
    data = hot_search()
    if not data:
        return None
    hot_search_data = []
    for i, rs in enumerate(data['realtime'][:50], 1):
        title = rs['word']
        sentiment = analyze_sentiment(title)
        # 创建分类器实例
        # classifier = TextClassifier()
        # classifier_result = classifier.classify_text(title)

        try:
            label = rs['small_icon_desc']
            if label in ['新', '热', '沸', '爆']:
                label = label
            else:
                label = ''
        except:
            label = ''
        hot_search_data.append({
            'seq': i,
            'title': title,
            'label': label,
            'url': f"https://s.weibo.com/weibo?q={quote(title)}&Refer=top",
            'sentiment': sentiment,
            # 'classifier_result':classifier_result
        })
    return hot_search_data
