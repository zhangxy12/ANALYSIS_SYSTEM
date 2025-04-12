
from celery_task.renmin_crawler.fetchUrl import fetchUrl
from celery_task.renmin_crawler.parseJson import parseJson



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

        # 将数据累积到 all_data 中
        all_data.extend(parsed_data)

        print("第{}页爬取完成".format(page))

    # 爬虫完成提示信息
    print("爬虫执行完毕！数据已保存至MongoDB数据库，请查看！")
