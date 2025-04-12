# -*- coding: utf-8 -*
import jieba
import pymongo
from celery_task.utils.tfidfCluster.langconv import *
from celery_task.utils.gsdmmCluster.normalization import normalize_corpus_part
from celery_task.config import mongo_conf
from celery_task.utils import mongo_client


def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


def Sent2Word(sentence):
    """Turn a sentence into tokenized word list and remove stop-word

    Using jieba to tokenize Chinese.

    Args:
        sentence: A string.

    Returns:
        words: A tokenized word list.
    """
    global stop_words

    words = jieba.cut(sentence)
    words = [w for w in words if w not in stop_words]

    print(f"Words after segmentation: {list(words)}")

    return words


def Match(content):
    content_comment = []
    advertisement = ["王者荣耀", "券后", "售价", '¥', "￥", '下单', '转发微博', '转发', '微博']
    words = []
    for k in range(0, len(content)):
        judge = []
        print('Processing train ', k)
        content[k] = Traditional2Simplified(content[k])
        for adv in advertisement:
            if adv in content[k]:
                judge.append("True")
                break
        if re.search(r"买.*赠.*", content[k]):
            judge.append("True")
            continue
        if content[k] == "":
            judge.append("True")
            continue
        # 通过上面的两种模式判断是不是广告
        if "True" not in judge:
            # 数据清洗
            a2 = re.compile(r'#.*?#')
            content[k] = a2.sub('', content[k])
            a3 = re.compile(r'\[组图共.*张\]')
            content[k] = a3.sub('', content[k])
            a4 = re.compile(r'http:.*')
            content[k] = a4.sub('', content[k])
            a5 = re.compile(r'@.*? ')
            content[k] = a5.sub('', content[k])
            a6 = re.compile(r'\[.*?\]')
            content[k] = a6.sub('', content[k])
            words.append(Sent2Word(content[k]))

    print(f"After cleaning and before segmentation: {content[k]}")
    print(f"Tokenized words: {words}")

    return words


def getRepostSent(tag_comment_task_id):
    sent = []
    my_query = {"tag_comment_task_id": tag_comment_task_id}

    # 查询数据库
    my_doc = mongo_client.db[mongo_conf.COMMENT_TASK].find(my_query)

    for item in my_doc:
        print(item)  # 打印每个文档，确认评论数据

        # 确保有 'detail' 字段且 'comments' 字段存在
        if 'detail' in item and 'comments' in item['detail']:
            # 遍历 'comments' 数组并提取每个评论的 'content'
            for comment in item['detail']['comments']:
                if 'content' in comment:
                    sent.append(comment['content'])
                else:
                    print("Warning: 'content' field not found in comment")
        else:
            print("Warning: 'detail' or 'comments' field not found in document")

    return sent

def getRepostSent_tb(tag_comment_task_id):
    sent = []
    my_query = {"tag_comment_task_id": tag_comment_task_id}

    # 查询数据库
    my_doc = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find(my_query)

    for item in my_doc:
        print(item)  # 打印每个文档，确认评论数据

        # 确保有 'detail' 字段且 'comments' 字段存在
        if 'detail' in item and 'comments' in item['detail']:
            # 遍历 'comments' 数组并提取每个评论的 'content'
            for comment in item['detail']['comments']:
                if 'content' in comment:
                    sent.append(comment['content'])
                else:
                    print("Warning: 'content' field not found in comment")

                # 检查是否有 'replies' 字段
                if 'replies' in comment:
                    for reply in comment['replies']:
                        if 'reply_content' in reply:
                            sent.append(reply['reply_content'])
                        else:
                            print("Warning: 'reply_content' field not found in reply")
        else:
            print("Warning: 'detail' or 'comments' field not found in document")

    return sent


def countWords(sent_words):
    words_dict = dict()
    for words in sent_words:
        for word in words:
            if len(word) == 0 or word == '' or '回复' in word:  # 排除"回复"
                continue
            elif word not in words_dict.keys():
                words_dict[word] = 1
            else:
                words_dict[word] += 1
    return words_dict


# 改变形式 + 排序
def reshapeDict(words_dict):
    words_list = []
    for key in words_dict:
        item = {}
        item['name'] = key
        item['value'] = words_dict[key]
        words_list.append(item)
    words_list.sort(key=lambda i: i['value'], reverse=True)
    return words_list


def preContent(tag_comment_task_id=None, doc_id=None):
    print("回复读取")
    content = getRepostSent(tag_comment_task_id)
    print(content)
    print("分词")
    # sent_words_a = Match(content)
    sent_words_b = normalize_corpus_part(content)
    print(sent_words_b)
    print("统计")
    # words_dict_a = countWords(sent_words_a)
    words_dict_b = countWords(sent_words_b)
    print(words_dict_b)
    print("排序")
    # words_dict_a = reshapeDict(words_dict_a)
    words_dict_b = reshapeDict(words_dict_b)
    print(words_dict_b)
    if len(words_dict_b) >= 200:
        # words_dict_a = words_dict_a[0:200]
        words_dict_b = words_dict_b[0:200]

    print(words_dict_b)
    # mydb['cloud'].insert_one({"task_id": task_id, "data":words_dict_b})
    # with Mongo(mongo_conf.COMMENT_CLOUD, mongo_conf.DB_NAME) as mydb:
    mongo_client.db[mongo_conf.COMMENT_CLOUD].update_one({"tag_comment_task_id": tag_comment_task_id}, {"$set": {"data": words_dict_b}})

def preContent_tb(tag_comment_task_id=None, doc_id=None):
    print("回复读取")
    content = getRepostSent_tb(tag_comment_task_id)
    print(content)
    print("分词")
    # sent_words_a = Match(content)
    sent_words_b = normalize_corpus_part(content)
    print(sent_words_b)
    print("统计")
    # words_dict_a = countWords(sent_words_a)
    words_dict_b = countWords(sent_words_b)
    print(words_dict_b)
    print("排序")
    # words_dict_a = reshapeDict(words_dict_a)
    words_dict_b = reshapeDict(words_dict_b)
    print(words_dict_b)
    if len(words_dict_b) >= 200:
        # words_dict_a = words_dict_a[0:200]
        words_dict_b = words_dict_b[0:200]

    print(words_dict_b)
    # mydb['cloud'].insert_one({"task_id": task_id, "data":words_dict_b})
    # with Mongo(mongo_conf.COMMENT_CLOUD, mongo_conf.DB_NAME) as mydb:
    mongo_client.db[mongo_conf.TB_COMMENT_CLOUD].update_one({"tag_comment_task_id": tag_comment_task_id}, {"$set": {"data": words_dict_b}})


if __name__ == '__main__':
    preContent("1734021478OaWSd5zHH")
    # a = normalize_corpus_part(getRepostSent("1621413905Kg3sYoiGk"))
    # print(a)
