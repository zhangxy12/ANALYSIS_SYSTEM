import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


class KmeansClustering():
    def __init__(self, stopwords_path=None):
        self.stopwords = self.load_stopwords(stopwords_path)
        self.vectorizer = TfidfVectorizer(stop_words=self.stopwords)

    def load_stopwords(self, stopwords=None):
        """
        加载停用词
        :param stopwords:
        :return:
        """
        if stopwords:
            with open(stopwords, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        else:
            return []

    def preprocess_data(self, corpus_path):
        """
        文本预处理，每行一个文本
        :param corpus_path:
        :return:
        """
        corpus = []
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 使用jieba分词并去掉停用词
                corpus.append(' '.join([word for word in jieba.lcut(line.strip()) if word not in self.stopwords]))
        return corpus

    def get_top_keywords(self, corpus, result, n_top_words=5):
        """
        提取每个簇的关键词，并生成主题标签
        :param corpus:
        :param result: 每个簇的文本索引
        :param n_top_words: 提取的关键词数
        :return: 每个簇的主题标签
        """
        # 计算TF-IDF矩阵
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        feature_names = self.vectorizer.get_feature_names_out()

        top_keywords = {}
        for label, text_indices in result.items():
            # 强制转换索引为整数类型
            text_indices = [int(idx) for idx in text_indices['text_ids']]  # 确保索引是整数
            cluster_texts = [corpus[idx] for idx in text_indices]
            cluster_tfidf_matrix = self.vectorizer.transform(cluster_texts)
            tfidf_scores = cluster_tfidf_matrix.sum(axis=0).A1
            sorted_indices = tfidf_scores.argsort()[::-1]
            top_words = [feature_names[i] for i in sorted_indices[:n_top_words]]

            # 自动生成主题标签
            top_keywords[label] = self.generate_theme_label(top_words)
            print(f"Cluster {label} top keywords: {', '.join(top_words)}")
            print(f"Cluster {label} theme: {top_keywords[label]}")

        return top_keywords

    def generate_theme_label(self, top_words):
        """
        根据聚类的关键词生成主题标签
        :param top_words: 聚类的top关键词
        :return: 聚类的主题标签
        """
        theme_mapping = {
            '娱乐': ['娱乐', '电影', '明星', '综艺', '电视剧', '男团', '女团', '微博之夜'],
            '新闻': ['新闻', '事件', '报道', '记者', '社会', '总理'],
            '体育': ['足球', '篮球', '比赛', '运动员', '体育'],
            '科技': ['科技', '技术', '创新', '人工智能', '机器人'],
            '财经': ['经济', '股票', '市场', '投资', '财务']
        }

        # 基于关键词来判断主题
        for theme, keywords in theme_mapping.items():
            if any(keyword in top_words for keyword in keywords):
                return theme
        return '其他'  # 默认主题标签

    def kmeans(self, corpus_path, n_clusters=5):
        """
        KMeans文本聚类
        :param corpus_path: 语料路径（每行一篇）,文章id从0开始
        :param n_clusters: 聚类类别数目
        :return: {cluster_id1: {'text_ids': [text_id1, text_id2], 'theme': '主题名称'}}
        """
        corpus = self.preprocess_data(corpus_path)
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        clf = KMeans(n_clusters=n_clusters, n_init=10, max_iter=300)
        y = clf.fit_predict(tfidf_matrix)

        result = {}
        for text_idx, label_idx in enumerate(y):
            if label_idx not in result:
                result[label_idx] = {'text_ids': [text_idx], 'theme': ''}
            else:
                result[label_idx]['text_ids'].append(text_idx)

        # 获取每个簇的主题
        top_keywords = self.get_top_keywords(corpus, result)

        # 将主题标签添加到结果中
        for label in result:
            result[label]['theme'] = top_keywords[label]

        return result


if __name__ == '__main__':
    kmeans = KmeansClustering(stopwords_path='../data/stop_words.txt')
    result = kmeans.kmeans('../data/test_data.txt', n_clusters=3)

    # 打印聚类结果和主题
    for cluster_id, cluster_info in result.items():
        print(
            f"Cluster {cluster_id} contains text IDs: {cluster_info['text_ids']} and has the theme: {cluster_info['theme']}")
