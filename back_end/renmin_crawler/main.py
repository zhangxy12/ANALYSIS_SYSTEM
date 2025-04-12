
from pymongo import MongoClient

from renmin_crawler.fetchUrl import fetchUrl
from renmin_crawler.parseJson import parseJson

# MongoDB配置
MONGO_URI = "mongodb://localhost:27017"  # MongoDB连接URI
DB_NAME = "test"  # 数据库名
COLLECTION_NAME = "news"  # 集合（表）名

# 连接MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def save_to_mongo(data):
    """将数据保存到MongoDB数据库中的 news 集合"""
    # 确保数据是一个列表，并且每一项都是字典
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        try:
            collection.insert_many(data)  # 使用insert_many来插入多条记录
            print(f"{len(data)}条数据已保存至MongoDB的 news 集合！")
        except Exception as e:
            print(f"保存数据到MongoDB时发生错误: {e}")
    else:
        print(f"数据格式错误，预期是一个包含字典的列表，但实际得到: {type(data)}")


def fetch_renmin_data(keyword: str, page: int):
    """
    根据关键词和页码获取人民网的数据并保存到MongoDB的news集合中
    """
    url = "http://search.people.cn/search-platform/front/search"
    html = fetchUrl(url, keyword, page)
    parsed_data = parseJson(html)

    # 将数据保存到MongoDB
    # save_to_mongo(parsed_data)

    return parsed_data

if __name__ == "__main__":
    # 起始页，终止页，关键词设置
    start = 1
    end = 3
    kw = "曼巴"

    # 保存爬取的数据
    all_data = []

    # 爬取数据
    for page in range(start, end + 1):
        url = "http://search.people.cn/search-platform/front/search"
        html = fetchUrl(url, kw, page)
        parsed_data = parseJson(html)

        # 将解析后的数据保存到MongoDB
        save_to_mongo(parsed_data)

        # 将数据累积到 all_data 中
        all_data.extend(parsed_data)

        print("第{}页爬取完成".format(page))

    # 爬虫完成提示信息
    print("爬虫执行完毕！数据已保存至MongoDB数据库，请查看！")
    print(f"保存至 MongoDB 数据库: {DB_NAME}, 集合: {COLLECTION_NAME}")