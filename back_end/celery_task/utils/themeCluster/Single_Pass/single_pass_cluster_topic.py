# -*- coding: UTF-8 -*-

import os
import sys
import jieba
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from celery_task.utils.my_cloud import MyCloud
from celery_task.config import mongo_conf
from celery_task.utils import mongo_client


class SinglePassCluster():
    def __init__(self, blog_data: list, topic: str, user_list: list,stopWords_path="D:\\dasanshang\\NLP\\1\\Topic_and_user_profile_analysis_system\\code\\back_end\\dict\\哈工大停用词表.txt", my_stopwords=None,
                 max_df=0.5, max_features=1000,
                 simi_threshold=0.5, res_save_path="./cluster_res.json"):
        self.origin_data_list = blog_data
        self.topic = topic
        self.user_list = user_list
        self.stopwords = self.load_stopwords(stopWords_path)
        if isinstance(my_stopwords, list):
            self.stopwords += my_stopwords
        self.tfidf = TfidfVectorizer(stop_words=self.stopwords, max_df=max_df, max_features=max_features)
        self.simi_thr = simi_threshold
        self.cluster_center_vec = []  # [cluster_center_vec, ]
        self.idx_2_text = {}  # {文本id: text, }
        self.cluster_2_idx = {}  # {cluster_id: [text_id, ]}
        self.res_path = res_save_path  # save self.cluster_2_idx
        self.tags = list()

    def load_stopwords(self, path):
        stopwords = []
        with open(path, 'r', encoding="utf-8") as f:
            for line in f:
                stopwords.append(line.strip())
        return stopwords

    def cut_sentences(self):
        texts = list()
        for data in self.origin_data_list:
            texts.append(data['text'])
        texts_cut = [" ".join(jieba.lcut(t)) for t in texts]
        self.idx_2_text = {idx: text for idx, text in enumerate(texts)}
        return texts_cut

    def get_tfidf(self, texts_cut):
        tfidf = self.tfidf.fit_transform(texts_cut)
        return tfidf.todense().tolist()

    def cosion_simi(self, vec):
        simi = cosine_similarity(np.array([vec]), np.array(self.cluster_center_vec))
        max_idx = np.argmax(simi, axis=1)[0]
        max_val = simi[0][max_idx]
        return max_val, max_idx

    def single_pass(self):
        texts_cut = self.cut_sentences()
        tfidf = self.get_tfidf(texts_cut)
        # print(len(tfidf), len(tfidf[0]))

        # 开始遍历
        for idx, vec in enumerate(tfidf):
            # 初始化，没有中心生成
            if not self.cluster_center_vec:
                self.cluster_center_vec.append(vec)
                self.cluster_2_idx[0] = [idx]
            # 存在簇
            else:
                max_simi, max_idx = self.cosion_simi(vec)
                if max_simi >= self.simi_thr:
                    self.cluster_2_idx[max_idx].append(idx)
                else:
                    self.cluster_center_vec.append(vec)
                    self.cluster_2_idx[len(self.cluster_2_idx)] = [idx]
        for key in self.cluster_2_idx.keys():
            index = self.cluster_2_idx[key]
            cluster_text = [self.origin_data_list[i].get('text') for i in index]
            user_id_list = [self.origin_data_list[i].get('user_id') for i in index]
            tags = MyCloud(cluster_text).GetWordCloud()
            hit = 0
            for user_index in range(len(self.user_list)):
                if self.user_list[user_index].get('user_id') in user_id_list:
                    self.user_list[user_index]['marks'] = tags[0:10] if len(tags) > 10 else tags
                    self.user_list[user_index]['category'] = key
                    hit += 1
                if hit >= len(user_id_list):
                    break
        update = {
            'data': self.user_list,
            'categories': len(self.cluster_2_idx)
        }
        print(self.topic)
        print(f"要更新的数据: {update}")
        try:
            result = mongo_client.db[mongo_conf.TOPIC_USER].update_one({'topic': self.topic}, {
                '$set': update
            }, upsert=True)
            print(f"匹配到的文档数量: {result.matched_count}")
            print(f"实际修改的文档数量: {result.modified_count}")
        except Exception as e:
            print(f"更新数据库时出错: {e}")
        return update



