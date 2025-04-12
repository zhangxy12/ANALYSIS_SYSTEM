import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def timeConvert(timestamp):
    try:
        # 时间戳转为日期格式
        timestamp = int(timestamp)
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception as e:
        print(f"时间转换错误: {e}")
        return "无发布时间"


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
                title = article.select_one('h3').get_text(strip=True) if article.select_one('h3') else "无标题"
                link = article.select_one('h3 a')['href'] if article.select_one('h3 a') else "无链接"
                summary = article.select_one('.txt-info').get_text(strip=True) if article.select_one(
                    '.txt-info') else "无摘要"
                source = article.select_one('.s-p').get_text(strip=True) if article.select_one('.s-p') else "无来源"
                source = article.select_one('.s-p .all-time-y2').get_text(strip=True) if article.select_one(
                    '.s-p .all-time-y2') else "无来源"

                create_time_script = article.select_one('.s-p script')
                if create_time_script:
                    timestamp = create_time_script.string.split("'")[1]
                    create_time = timeConvert(timestamp)
                else:
                    create_time = "无发布时间"

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
    time.sleep(1)

    return results


if __name__ == "__main__":
    keyword = input("请输入要搜索的关键词: ").strip()
    max_pages = input("请输入要爬取的页数（默认5页）：").strip()

    if not max_pages.isdigit():
        max_pages = 5
    else:
        max_pages = int(max_pages)

    search_wechat_articles(keyword, max_pages)