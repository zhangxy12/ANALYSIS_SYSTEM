"""
:爬虫任务

"""
import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from celery_task.config import mongo_conf
from celery_task.renmin_crawler.main import fetch_renmin_data
from celery_task.tieba_crawler.main import fetch_posts
from celery_task.utils import mongo_client
from celery_task.utils.my_cloud import MyCloud


def spider(tag: str, tag_task_id: str):
    """
    tag微博数据的爬取与储存
    :param tag_task_id: 任务id
    :param tag: 话题
    :return:
    """
    result_data_list = list()
    user_set = set()
    false_count = 0  # 无效请求次数
    for i in range(1, 50, 1):
        if false_count >= 5:
            break  # 无效请求大于等于5时,认为无法得到相关数据，停止请求
        url = 'http://127.0.0.1:8000/weibo_curl/api/search_tweets?keyword={keyword}&cursor={cursor}&is_hot=1' \
            .format(keyword=tag, cursor=i)
        response = requests.get(url, verify=False)
        print(url)
        print('false_count: %s' % false_count)
        weibo_dict = json.loads(response.text)
        if weibo_dict['error_code'] == 0:
            false_count = 0
            weibo_list = weibo_dict.get('data').get('result')
            new_weibo_list = list()
            for weibo in weibo_list:
                weibo['text'] = weibo['text'] + ' '
                weibo['tid'] = weibo['weibo_id']
                weibo['text_token'] = MyCloud(weibo['text'].split(' ')).GetKeyWord()
                weibo['retweet_count'] = weibo.pop('reposts_count')
                weibo['favorite_count'] = weibo.pop('attitudes_count')
                weibo['comment_count'] = weibo.pop('comments_count')
                weibo['tweet_type'] = 'article'
                weibo['data_source'] = 'weibo'
                weibo['hot_count'] = int(weibo['retweet_count']) + int(weibo['favorite_count']) + int(
                    weibo['comment_count'])
                user_set.add(weibo['user_id'])
                new_weibo_list.append(weibo)
            result_data_list.extend(new_weibo_list)
        else:
            false_count += 1
    result_data_list.sort(key=lambda x: int(x['hot_count']), reverse=True)
    result_data_dict = dict()
    result_data_dict['data'] = result_data_list
    result_data_dict['tag'] = tag
    result_data_dict['tag_task_id'] = tag_task_id
    weibo_id_set = set()  # 热度排名前十的weibo_id
    weibo_post_list = list()
    for i in range(0, len(result_data_dict['data']), 1):
        if result_data_dict['data'][i]['weibo_id'] not in weibo_id_set:
            weibo_post_list.append(result_data_dict['data'][i])
            weibo_id_set.add(result_data_dict['data'][i]['weibo_id'])
        if len(weibo_id_set) >= 10:
            break
    mongo_client.db[mongo_conf.BLOG].insert_one(result_data_dict)
    return result_data_dict, list(weibo_post_list), list(user_set)


def timeConvert(timestamp):
    try:
        # 时间戳转为日期格式
        timestamp = int(timestamp)
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception as e:
        print(f"时间转换错误: {e}")
        return "无发布时间"


def is_valid_utf8(text):
    """检查文本是否为有效的 UTF-8 编码，如果不是则跳过该字符"""
    try:
        text.encode('utf-8')
        return text  # 返回原文本
    except UnicodeEncodeError:
        return None  # 返回 None 表示该文本包含非法字符


def search_wechat_articles(keyword, cursor):
    base_url = "https://weixin.sogou.com/weixin"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    results = []

    # 使用传入的 cursor 来指定页面
    params = {
        "type": 2,
        "query": keyword,
        "page": cursor,
    }

    print(f"正在爬取第 {cursor} 页...")

    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.txt-box')

        if not articles:
            print("未找到相关文章，停止爬取。")
            return results

        for article in articles:
            try:
                # 获取文章标题
                title = article.select_one('h3').get_text(strip=True) if article.select_one('h3') else "无标题"
                title = is_valid_utf8(title)
                if title is None:  # 跳过非法字符的标题
                    continue

                # 获取文章链接
                link = article.select_one('h3 a')['href'] if article.select_one('h3 a') else "无链接"

                # 获取文章摘要
                summary = article.select_one('.txt-info').get_text(strip=True) if article.select_one(
                    '.txt-info') else "无摘要"
                summary = is_valid_utf8(summary)
                if summary is None:  # 跳过非法字符的摘要
                    continue

                # 获取文章来源
                source = article.select_one('.s-p').get_text(strip=True) if article.select_one('.s-p') else "无来源"
                source = is_valid_utf8(source)
                if source is None:  # 跳过非法字符的来源
                    continue

                source = article.select_one('.s-p .all-time-y2').get_text(strip=True) if article.select_one(
                    '.s-p .all-time-y2') else source

                # 获取发布时间
                create_time_script = article.select_one('.s-p script')
                if create_time_script:
                    timestamp = create_time_script.string.split("'")[1]
                    create_time = timeConvert(timestamp)
                else:
                    create_time = "无发布时间"

                create_time = is_valid_utf8(create_time)
                if create_time is None:  # 跳过非法字符的时间
                    continue

                results.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "source": source,
                    "time": create_time
                })
            except Exception as e:
                print(f"解析文章时出错: {e}")
    else:
        print(f"请求失败，状态码: {response.status_code}")

    # 延迟防止过于频繁的请求
    time.sleep(2)
    return results


from cnsenti import Sentiment


def analyze_sentiment(test_text):
    senti = Sentiment()
    if not test_text:
        return "neutral"  # 空文本返回中性情感
    res = senti.sentiment_count(test_text)
    print(res)
    if res["pos"] == res["neg"]:
        return "neutral"
    elif res["pos"] > res["neg"]:
        return "positive"
    else:
        return "negative"


def spider_wx(tag: str, tag_task_id: str):
    """
    微信数据的爬取与储存
    :param tag_task_id: 任务id
    :param tag: 话题
    :return:
    """
    result_data_list = list()
    false_count = 0  # 无效请求次数
    for i in range(1, 30):
        if false_count >= 5:
            break  # 无效请求大于等于5时,认为无法得到相关数据，停止请求

        # 爬取微信文章数据
        articles = search_wechat_articles(tag, i)

        if not articles:
            false_count += 1
            print(f"未获取到相关文章，第 {i} 页爬取失败，继续爬取下一页...")
            continue
        else:
            false_count = 0

        new_article_list = list()
        for article in articles:
            # 对每篇文章的 summary 进行情感分析
            sentiment = analyze_sentiment(article.get('summary', ''))
            article['sentiment'] = sentiment  # 将情感分析结果加入到文章中
            article['data_source'] = 'wechat'
            new_article_list.append(article)

        result_data_list.extend(new_article_list)

    result_data_dict = {
        'data': result_data_list,
        'tag': tag,
        'tag_task_id': tag_task_id
    }

    # 存储结果到 MongoDB
    mongo_client.db[mongo_conf.WX_BLOG].insert_one(result_data_dict)

    return result_data_dict


def spider_rm(tag: str, tag_task_id: str):
    """
    人民网数据的爬取与储存
    :param tag_task_id: 任务id
    :param tag: 话题
    :return:
    """
    result_data_list = list()
    false_count = 0  # 无效请求次数
    for i in range(1, 30):
        print(f"正在爬取第 {i} 页...")
        if false_count >= 5:
            break  # 无效请求大于等于5时,认为无法得到相关数据，停止请求

        # 爬取人民网文章数据
        articles = fetch_renmin_data(tag, i)

        if not articles:
            false_count += 1
            print(f"未获取到相关文章，第 {i} 页爬取失败，继续爬取下一页...")
            continue
        else:
            false_count = 0

        new_article_list = list()
        for article in articles:
            # 对每篇文章的 summary 进行情感分析
            sentiment = analyze_sentiment(article.get('content', ''))
            article['sentiment'] = sentiment  # 将情感分析结果加入到文章中
            article['data_source'] = 'renminwang'
            new_article_list.append(article)

        result_data_list.extend(new_article_list)

    result_data_dict = {
        'data': result_data_list,
        'tag': tag,
        'tag_task_id': tag_task_id
    }

    # 存储结果到 MongoDB
    mongo_client.db[mongo_conf.RM_BLOG].insert_one(result_data_dict)

    return result_data_dict


def spider_tb(tag: str, tag_task_id: str):
    """
    tb数据的爬取与储存
    :param tag_task_id: 任务id
    :param tag: 话题
    :return:
    """
    result_data_list = list()
    false_count = 0  # 无效请求次数
    for i in range(1, 2):
        print(f"正在爬取第 {i} 页...")
        if false_count >= 5:
            break  # 无效请求大于等于5时,认为无法得到相关数据，停止请求

        # 爬取文章数据
        articles = []
        print("fetch_posts_before")
        articles = fetch_posts(tag, i, articles)
        print("fetch_posts_after")
        if not articles:
            false_count += 1
            print(f"未获取到相关文章，第 {i} 页爬取失败，继续爬取下一页...")
            continue
        else:
            false_count = 0

        new_article_list = list()
        for article in articles:
            # 对每篇文章的 content 进行情感分析
            sentiment = analyze_sentiment(article.get('content', ''))
            article['sentiment'] = sentiment  # 将情感分析结果加入到文章中
            article['data_source'] = 'tieba'
            new_article_list.append(article)

        result_data_list.extend(new_article_list)

    result_data_dict = {
        'data': result_data_list,
        'tag': tag,
        'tag_task_id': tag_task_id
    }
    print(result_data_dict)
    print("mongo_before")
    # 存储结果到 MongoDB
    mongo_client.db[mongo_conf.TB_BLOG].insert_one(result_data_dict)
    print("mongo_after")
    tb_id_set = set()  # 用于去重的帖子 ID 集合
    print("1")
    tb_post_list = list()
    for article in result_data_list:
        # 文章有唯一标识 'url'
        post_id = article.get('url')
        if post_id not in tb_id_set:
            tb_post_list.append(article)
            tb_id_set.add(post_id)
        if len(tb_id_set) >= 10:
            break

    return result_data_dict, tb_post_list
