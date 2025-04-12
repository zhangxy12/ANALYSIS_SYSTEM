"""
博文详情页请求的api
"""
import urllib

import jieba
from fastapi import APIRouter, Depends
from datetime import datetime

from jiagu.textrank import Keywords

from celery_task.config import mongo_conf
from models.dto.restful_model import RESTfulModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from dependencise import get_mongo_db
from service.comment_extract import get_tree_data, get_comment_task_id, getByTendencyId, getByCloudId, \
    getTypeByClusterId, getKeyNode, getWeiboById, getTbById, getIPById, getByCloudId_tb, get_comment_task_id_tb, \
    getByMood_tb
from collections import Counter
from collections import defaultdict
import re
import stanfordnlp
import jiagu
from fastapi import APIRouter, Depends


import pyopenie
from typing import List


comment_router = APIRouter(tags=['微博评论分析api'])


@comment_router.get('/post_detail', response_model=RESTfulModel,
                    description='获取文章详细信息',
                    summary='文章')
async def get_post_detail(tag_task_id: str, weibo_id: str, mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    return RESTfulModel(code=0, data=await getWeiboById(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo_db=mongo))


@comment_router.get('/location', response_model=RESTfulModel,
                    description='获取微博地理位置数据',
                    summary='地理位置数据')
async def get_location(tag_task_id: str, weibo_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)

    try:
        # 获取所有评论的地理位置信息
        comments = await mongo_db["comment_task"].find_one({"tag_comment_task_id": comment_task_id})
        if not comments or "detail" not in comments:
            return RESTfulModel(code=1, message="没有找到评论数据")

        comment_data = comments.get("detail", {}).get("comments", [])

        # 统计评论者的地理位置
        location_count = Counter()
        for comment in comment_data:
            location = comment.get("location", None)
            if location:
                location_count[location] += 1

        # 将统计结果转为前端可用的格式
        location_data = [{"location": loc, "count": count} for loc, count in location_count.items()]

        # 只返回地理位置数据
        return RESTfulModel(code=0, data={"location_data": location_data})

    except Exception as e:
        return RESTfulModel(code=1, data=str(e))


@comment_router.get('/cloud', response_model=RESTfulModel,
                    description='获取评论云图数据',
                    summary='云图数据')
async def get_cloud(tag_task_id: str, weibo_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)
    return RESTfulModel(code=0, data=await getByCloudId(comment_task_id, mongo_db))


# 获取情感分析统计信息
@comment_router.get('/sentiment/statistics', response_model=RESTfulModel,
                    description='获取评论情感分析统计数据',
                    summary='情感统计')
async def get_sentiment_statistics(tag_task_id: str, weibo_id: str,
                                   mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)

    # 获取所有评论的情感分析结果
    comments = await mongo_db[mongo_conf.COMMENT_TASK].find_one({'tag_comment_task_id': comment_task_id})

    sentiment_count = Counter()

    for comment in comments.get('detail', {}).get('comments', []):
        sentiment = comment.get('sentiment_analysis', {}).get('sentiment', 'neutral')
        sentiment_count[sentiment] += 1

    # 计算各情感类型的比例
    total_comments = sum(sentiment_count.values())
    sentiment_data = {
        "positive": sentiment_count.get("positive", 0) / total_comments,
        "negative": sentiment_count.get("negative", 0) / total_comments,
        "neutral": sentiment_count.get("neutral", 0) / total_comments
    }

    return RESTfulModel(code=0, data=sentiment_data)


# 贴吧
@comment_router.get('/post_detail_tb', response_model=RESTfulModel,
                    description='获取文章详细信息',
                    summary='文章')
async def get_post_detail_tb(tag_task_id: str, url: str, mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    decoded_url = urllib.parse.unquote(url)
    print(decoded_url)
    return RESTfulModel(code=0, data=await getTbById(tag_task_id=tag_task_id, url=decoded_url, mongo_db=mongo))

@comment_router.get('/cloud_tb', response_model=RESTfulModel,
                    description='获取tb评论云图数据',
                    summary='云图数据')
async def get_cloud_tb(tag_task_id: str, url: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id_tb(tag_task_id=tag_task_id, url=url, mongo=mongo_db)
    return RESTfulModel(code=0, data=await getByCloudId_tb(comment_task_id, mongo_db))

@comment_router.get('/ip', response_model=RESTfulModel,
                    description='获取tb地理位置数据',
                    summary='tb地理位置数据')
async def get_location_tb(tag_task_id: str, url: str, mongo: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    decoded_url = urllib.parse.unquote(url)

    comment_task_id = await get_comment_task_id_tb(tag_task_id=tag_task_id, url=decoded_url, mongo=mongo)

    return RESTfulModel(code=0, data=await getIPById(comment_task_id=comment_task_id, mongo_db=mongo))

@comment_router.get('/mood_tb', response_model=RESTfulModel,
                    description='获取tb评论情感分析数据',
                    summary='情感分析')
async def get_mood_tb(tag_task_id: str, url: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    decoded_url = urllib.parse.unquote(url)

    comment_task_id = await get_comment_task_id_tb(tag_task_id=tag_task_id, url=decoded_url, mongo=mongo_db)

    return RESTfulModel(code=0, data=await getByMood_tb(comment_task_id, mongo_db))

@comment_router.get('/cluster/type', response_model=RESTfulModel,
                    description='获取评论聚类数据',
                    summary='聚类')
async def get_cluster(tag_task_id: str, weibo_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)
    return RESTfulModel(code=0, data=await getTypeByClusterId(comment_task_id, mongo_db=mongo_db))

@comment_router.get('/sentiment/trend', response_model=RESTfulModel,
                    description='获取评论情感随时间变化数据',
                    summary='情感趋势')
async def get_sentiment_trend(tag_task_id: str, weibo_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)

    # 从数据库中获取评论数据
    comments = await mongo_db["comment_task"].find_one({"tag_comment_task_id": comment_task_id})
    if not comments or "detail" not in comments:
        return RESTfulModel(code=1, message="没有找到评论数据")

    # 获取评论列表
    comment_data = comments.get("detail", {}).get("comments", [])

    # 用于存储情感数据
    sentiment_trend = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})

    # 遍历所有评论并按时间统计情感
    for comment in comment_data:
        # 获取评论时间
        publish_time_str = comment.get("publish_time")
        if not publish_time_str:
            continue

        try:
            # 将时间字符串转换为日期（按天分组）
            publish_time = datetime.strptime(publish_time_str, "%Y-%m-%d %H:%M")
            date_str = publish_time.strftime("%Y-%m-%d")  # 按天统计
        except ValueError:
            continue

        # 获取情感分析结果
        sentiment = comment.get("sentiment_analysis", {}).get("sentiment", "neutral")
        if sentiment not in ["positive", "negative", "neutral"]:
            sentiment = "neutral"

        # 更新情感数据
        sentiment_trend[date_str][sentiment] += 1

    # 转换数据为前端所需的格式
    result = []
    for date, sentiment_counts in sentiment_trend.items():
        result.append({
            "publish_time": date,
            "sentiment_counts": sentiment_counts
        })

    return RESTfulModel(code=0, data=result)


@comment_router.get('/knowledge_graph', response_model=RESTfulModel,
                    description='构建博客评论知识图谱',
                    summary='博客评论知识图谱')
async def get_knowledge_graph(tag_task_id: str, weibo_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    # 获取微博数据
    comment_task_id = await get_comment_task_id(tag_task_id=tag_task_id, weibo_id=weibo_id, mongo=mongo_db)
    weibo_data = await mongo_db["comment_task"].find_one({"tag_comment_task_id": comment_task_id})

    # 提取微博内容
    blog_content = weibo_data['detail']['weibo_content']

    import re, jieba.posseg as pseg

    class ExtractEvent:
        def __init__(self):
            self.map_dict = self.load_mapdict()
            self.minlen = 2
            self.maxlen = 20
            self.keywords_num = 20
            self.limit_score = 10
            self.IP = "(([NERMQ]*P*[ABDP]*)*([ABDV]{1,})*([NERMQ]*)*([VDAB]$)?([NERMQ]*)*([VDAB]$)?)*"
            self.IP = "([NER]*([PMBQADP]*[NER]*)*([VPDA]{1,}[NEBRVMQDA]*)*)"
            self.MQ = '[DP]*M{1,}[Q]*([VN]$)?'
            self.VNP = 'V*N{1,}'
            self.NP = '[NER]{1,}'
            self.REN = 'R{2,}'
            self.VP = 'P?(V|A$|D$){1,}'
            self.PP = 'P?[NERMQ]{1,}'
            self.SPO_n = "n{1,}"
            self.SPO_v = "v{1,}"
            self.stop_tags = {'u', 'wp', 'o', 'y', 'w', 'f', 'u', 'c', 'uj', 'nd', 't', 'x'}
            self.combine_words = {"首先", "然后", "之前", "之后", "其次", "接着"}

        """构建映射字典"""

        def load_mapdict(self):
            tag_dict = {
                'B': 'b'.split(),  # 时间词
                'A': 'a d'.split(),  # 时间词
                'D': "d".split(),  # 限定词
                'N': "n j s zg en l r".split(),  # 名词
                "E": "nt nz ns an ng".split(),  # 实体词
                "R": "nr".split(),  # 人物
                'G': "g".split(),  # 语素
                'V': "vd v va i vg vn g".split(),  # 动词
                'P': "p f".split(),  # 介词
                "M": "m t".split(),  # 数词
                "Q": "q".split(),  # 量词
                "v": "V".split(),  # 动词短语
                "n": "N".split(),  # 名词介宾短语
            }
            map_dict = {}
            for flag, tags in tag_dict.items():
                for tag in tags:
                    map_dict[tag] = flag
            return map_dict

        """根据定义的标签,对词性进行标签化"""

        def transfer_tags(self, postags):
            tags = [self.map_dict.get(tag[:2], 'W') for tag in postags]
            return ''.join(tags)

        """抽取出指定长度的ngram"""

        def extract_ngram(self, pos_seq, regex):
            ss = self.transfer_tags(pos_seq)

            def gen():
                for s in range(len(ss)):
                    for n in range(self.minlen, 1 + min(self.maxlen, len(ss) - s)):
                        e = s + n
                        substr = ss[s:e]
                        if re.match(regex + "$", substr):
                            yield (s, e)

            return list(gen())

        '''抽取ngram'''

        def extract_sentgram(self, pos_seq, regex):
            ss = self.transfer_tags(pos_seq)

            def gen():
                for m in re.finditer(regex, ss):
                    yield (m.start(), m.end())

            return list(gen())

        """指示代词替换，消解处理"""

        def cite_resolution(self, words, postags, persons):
            if not persons and 'r' not in set(postags):
                return words, postags
            elif persons and 'r' in set(postags):
                cite_index = postags.index('r')
                if words[cite_index] in {"其", "他", "她", "我"}:
                    words[cite_index] = persons[-1]
                    postags[cite_index] = 'nr'
            elif 'r' in set(postags):
                cite_index = postags.index('r')
                if words[cite_index] in {"为何", "何", "如何"}:
                    postags[cite_index] = 'w'
            return words, postags

        """抽取量词性短语"""

        def extract_mqs(self, wds, postags):
            phrase_tokspans = self.extract_sentgram(postags, self.MQ)
            if not phrase_tokspans:
                return []
            phrases = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            return phrases

        '''抽取动词性短语'''

        def get_ips(self, wds, postags):
            ips = []
            phrase_tokspans = self.extract_sentgram(postags, self.IP)
            if not phrase_tokspans:
                return []
            phrases = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            phrase_postags = [''.join(postags[i[0]:i[1]]) for i in phrase_tokspans]
            for phrase, phrase_postag_ in zip(phrases, phrase_postags):
                if not phrase:
                    continue
                phrase_postags = ''.join(phrase_postag_).replace('m', '').replace('q', '').replace('a', '').replace('t',
                                                                                                                    '')
                if phrase_postags.startswith('n') or phrase_postags.startswith('j'):
                    has_subj = 1
                else:
                    has_subj = 0
                ips.append((has_subj, phrase))
            return ips

        """分短句处理"""

        def split_short_sents(self, text):
            return [i for i in re.split(r'[,，]', text) if len(i) > 2]

        """分段落"""

        def split_paras(self, text):
            return [i for i in re.split(r'[\n\r]', text) if len(i) > 4]

        """分长句处理"""

        def split_long_sents(self, text):
            return [i for i in re.split(r'[;。:； ：？?!！【】▲丨|]', text) if len(i) > 4]

        """移出噪声数据"""

        def remove_punc(self, text):
            text = text.replace('\u3000', '').replace("'", '').replace('“', '').replace('”', '').replace('▲',
                                                                                                         '').replace(
                '” ', "”")
            tmps = re.findall('[\(|（][^\(（\)）]*[\)|）]', text)
            for tmp in tmps:
                text = text.replace(tmp, '')
            return text

        """保持专有名词"""

        def zhuanming(self, text):
            books = re.findall('[<《][^《》]*[》>]', text)
            return books

        """对人物类词语进行修正"""

        def modify_nr(self, wds, postags):
            phrase_tokspans = self.extract_sentgram(postags, self.REN)
            wds_seq = ' '.join(wds)
            pos_seq = ' '.join(postags)
            if not phrase_tokspans:
                return wds, postags
            else:
                wd_phrases = [' '.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
                postag_phrases = [' '.join(postags[i[0]:i[1]]) for i in phrase_tokspans]
                for wd_phrase in wd_phrases:
                    tmp = wd_phrase.replace(' ', '')
                    wds_seq = wds_seq.replace(wd_phrase, tmp)
                for postag_phrase in postag_phrases:
                    pos_seq = pos_seq.replace(postag_phrase, 'nr')
            words = [i for i in wds_seq.split(' ') if i]
            postags = [i for i in pos_seq.split(' ') if i]
            return words, postags

        """对人物类词语进行修正"""

        def modify_duplicate(self, wds, postags, regex, tag):
            phrase_tokspans = self.extract_sentgram(postags, regex)
            wds_seq = ' '.join(wds)
            pos_seq = ' '.join(postags)
            if not phrase_tokspans:
                return wds, postags
            else:
                wd_phrases = [' '.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
                postag_phrases = [' '.join(postags[i[0]:i[1]]) for i in phrase_tokspans]
                for wd_phrase in wd_phrases:
                    tmp = wd_phrase.replace(' ', '')
                    wds_seq = wds_seq.replace(wd_phrase, tmp)
                for postag_phrase in postag_phrases:
                    pos_seq = pos_seq.replace(postag_phrase, tag)
            words = [i for i in wds_seq.split(' ') if i]
            postags = [i for i in pos_seq.split(' ') if i]
            return words, postags

        '''对句子进行分词处理'''

        def cut_wds(self, sent):

            WordList = ["一星四射队", "中科院微电子所", "小聋瞎队", "打完就解散队", "女生1队", "2021年", "5月29日",
                        "糊人不唬人队", "男子队伍", "女子队伍"]
            for UserWord in WordList:
                jieba.add_word(UserWord)
            wds = list(pseg.cut(sent))
            postags = [w.flag for w in wds]
            words = [w.word for w in wds]
            return self.modify_nr(words, postags)

        """移除噪声词语"""

        def clean_wds(self, words, postags):
            wds = []
            poss = []
            for wd, postag in zip(words, postags):
                if postag[0].lower() in self.stop_tags:
                    continue
                wds.append(wd)
                poss.append(postag[:2])
            return wds, poss

        """检测是否成立, 肯定需要包括名词"""

        def check_flag(self, postags):
            if not {"v", 'a', 'i'}.intersection(postags):
                return 0
            return 1

        """识别出人名实体"""

        def detect_person(self, words, postags):
            persons = []
            for wd, postag in zip(words, postags):
                if postag == 'nr':
                    persons.append(wd)
            return persons

        """识别出名词性短语"""

        def get_nps(self, wds, postags):
            phrase_tokspans = self.extract_sentgram(postags, self.NP)
            if not phrase_tokspans:
                return [], []
            phrases_np = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            return phrase_tokspans, phrases_np

        """识别出介宾短语"""

        def get_pps(self, wds, postags):
            phrase_tokspans = self.extract_sentgram(postags, self.PP)
            if not phrase_tokspans:
                return [], []
            phrases_pp = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            return phrase_tokspans, phrases_pp

        """识别出动词短语"""

        def get_vps(self, wds, postags):
            phrase_tokspans = self.extract_sentgram(postags, self.VP)
            if not phrase_tokspans:
                return [], []
            phrases_vp = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            return phrase_tokspans, phrases_vp

        """抽取名动词性短语"""

        def get_vnps(self, s):
            wds, postags = self.cut_wds(s)
            if not postags:
                return [], []
            if not (postags[-1].endswith("n") or postags[-1].endswith("l") or postags[-1].endswith("i")):
                return [], []
            phrase_tokspans = self.extract_sentgram(postags, self.VNP)
            if not phrase_tokspans:
                return [], []
            phrases_vnp = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans]
            phrase_tokspans2 = self.extract_sentgram(postags, self.NP)
            if not phrase_tokspans2:
                return [], []
            phrases_np = [''.join(wds[i[0]:i[1]]) for i in phrase_tokspans2]
            return phrases_vnp, phrases_np

        """提取短语"""

        def phrase_ip(self, content):
            spos = []
            events = []
            content = self.remove_punc(content)
            paras = self.split_paras(content)
            for para in paras:
                long_sents = self.split_long_sents(para)
                for long_sent in long_sents:
                    persons = []
                    short_sents = self.split_short_sents(long_sent)
                    for sent in short_sents:
                        words, postags = self.cut_wds(sent)
                        person = self.detect_person(words, postags)
                        words, postags = self.cite_resolution(words, postags, persons)
                        words, postags = self.clean_wds(words, postags)
                        # print(words,postags)
                        ips = self.get_ips(words, postags)
                        persons += person
                        for ip in ips:
                            events.append(ip[1])
                            wds_tmp = []
                            postags_tmp = []
                            words, postags = self.cut_wds(ip[1])
                            verb_tokspans, verbs = self.get_vps(words, postags)
                            pp_tokspans, pps = self.get_pps(words, postags)
                            tmp_dict = {str(verb[0]) + str(verb[1]): ['V', verbs[idx]] for idx, verb in
                                        enumerate(verb_tokspans)}
                            pp_dict = {str(pp[0]) + str(pp[1]): ['N', pps[idx]] for idx, pp in enumerate(pp_tokspans)}
                            tmp_dict.update(pp_dict)
                            sort_keys = sorted([int(i) for i in tmp_dict.keys()])
                            for i in sort_keys:
                                if i < 10:
                                    i = '0' + str(i)
                                wds_tmp.append(tmp_dict[str(i)][-1])
                                postags_tmp.append(tmp_dict[str(i)][0])
                            wds_tmp, postags_tmp = self.modify_duplicate(wds_tmp, postags_tmp, self.SPO_v, 'V')
                            wds_tmp, postags_tmp = self.modify_duplicate(wds_tmp, postags_tmp, self.SPO_n, 'N')
                            if len(postags_tmp) < 2:
                                continue
                            seg_index = []
                            i = 0
                            for wd, postag in zip(wds_tmp, postags_tmp):
                                if postag == 'V':
                                    seg_index.append(i)
                                i += 1
                            spo = []
                            for indx, seg_indx in enumerate(seg_index):
                                if indx == 0:
                                    pre_indx = 0
                                else:
                                    pre_indx = seg_index[indx - 1]
                                if pre_indx < 0:
                                    pre_indx = 0
                                if seg_indx == 0:
                                    spo.append(('', wds_tmp[seg_indx], ''.join(wds_tmp[seg_indx + 1:])))
                                elif seg_indx > 0 and indx < 1:
                                    spo.append(
                                        (''.join(wds_tmp[:seg_indx]), wds_tmp[seg_indx],
                                         ''.join(wds_tmp[seg_indx + 1:])))
                                else:
                                    spo.append((''.join(wds_tmp[pre_indx + 1:seg_indx]), wds_tmp[seg_indx],
                                                ''.join(wds_tmp[seg_indx + 1:])))
                            spos += spo

            return events, spos

    handler = ExtractEvent()
    content = blog_content
    event_triples = handler.phrase_ip(content)

    # 实体去重
    seen_subjects = set()
    unique_triples = []
    for triple in event_triples:
        subject = triple[0]
        if subject not in seen_subjects:
            seen_subjects.add(subject)
            unique_triples.append(triple)

    # 返回格式化的三元组数据
    result = [{"subject": triple[0], "predicate": triple[1], "object": triple[2]} for triple in unique_triples]
    print(result)
    return {"code": 0, "message": "Success", "data": result}

