import requests
from bs4 import BeautifulSoup
import csv
import time
import re

from motor.motor_asyncio import AsyncIOMotorDatabase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from bert_class.predict import TextClassifier

# 新增随机等待函数
def random_delay():
    time.sleep(max(1, abs(1.5 + 0.5 * (ord('武') % 3))))  # 带有武大元素的延时逻辑

async def search_and_save_rumors(db: AsyncIOMotorDatabase):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        'Referer': 'https://www.piyao.org.cn/'
    }

    url = 'https://www.piyao.org.cn/jrpy/index.htm'
    # 设置 Chrome 为无头模式
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe", options=chrome_options)

    # 获取当前日期日期
    current_date = datetime.now().date()

    # 用于记录已经处理过的文章链接
    processed_links = set()

    # 获取 rumors 集合
    collection = db['rumors']

    # 查询数据库中第一条记录的日期
    first_record = await collection.find_one(sort=[('date', -1)])
    print(datetime.strptime(first_record['date'], '%Y-%m-%d').date())
    print(current_date)
    if first_record and datetime.strptime(first_record['date'], '%Y-%m-%d').date() == current_date:
        print("数据库第一条记录日期为今天，无需爬取")
        driver.quit()
        return

    try:
        driver.get(url)

        while True:
            random_delay()
            soup = BeautifulSoup(driver.page_source, 'lxml')
            articles = soup.find_all('li')

            for article in articles:
                # 提取标题
                title_tag = article.find('a')
                if title_tag:
                    title = title_tag.text.strip()
                    link = 'https://www.piyao.org.cn' + title_tag['href'].lstrip('.')
                else:
                    title = ''
                    link = ''

                # 提取发布日期
                date_tag = article.find('p', class_='domPC')
                if date_tag:
                    date_str = date_tag.text.strip()
                    try:
                        article_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        print(article_date)
                        # 如果数据库中有记录，只爬取大于数据库中第一条记录日期的数据
                        if first_record:
                            last_db_date = datetime.strptime(first_record['date'], '%Y-%m-%d').date()
                            print(last_db_date)
                            if article_date <= last_db_date:
                                return
                        # 检查链接是否已经处理过
                        if link not in processed_links:
                            # 将数据存入 MongoDB
                            data = {
                                'title': title,
                                'date': date_str,
                                'url': link
                            }
                            await collection.insert_one(data)
                            # 将链接添加到已处理集合中
                            processed_links.add(link)
                    except ValueError:
                        continue

            try:
                more_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "more"))
                )
                more_button.click()
            except:
                print("没有更多数据了，结束抓取")
                break
    finally:
        driver.quit()



async def crawl_and_save_rumor_details(db):
    # 初始化文本分类器
    classifier = TextClassifier()
    # 获取 rumors 集合
    rumors_collection = db['rumors']
    # 获取 rumor_detail 集合
    detail_collection = db['rumor_detail']

    # 获取当前日期和昨天的日期
    current_date = datetime.now().date()

    # 查询 rumor_detail 数据库中第一条记录的日期
    first_record = await detail_collection.find_one(sort=[('date', -1)])
    if first_record and datetime.strptime(first_record['date'], '%Y-%m-%d').date() == current_date:
        print("rumor_detail 数据库第一条记录日期为今天，无需爬取")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }

    # 如果数据库中有记录，获取最新记录的日期
    if first_record:
        last_db_date = datetime.strptime(first_record['date'], '%Y-%m-%d').date()
        print(last_db_date)
    else:
        last_db_date = None

    # 获取 rumors 集合中的前 30 条记录，按日期降序排列
    records = rumors_collection.find().sort('date', -1).limit(30)

    for record in await records.to_list(length=30):  # 使用 to_list 方法获取实际结果
        url = record['url']
        date = record['date']
        article_date = datetime.strptime(date, '%Y-%m-%d').date()
        print(article_date)
        # 如果数据库中有记录，只处理日期大于数据库中最新记录日期的数据
        if last_db_date and article_date <= last_db_date:
            return

        try:
            # 发送请求
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # 定位到正文内容所在的 div
            content_div = soup.find('div', id='detailContent')

            if content_div:
                # 提取谣言和真相内容
                rumors_and_truths = []
                current_rumor = None
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text.startswith('谣言：'):
                        current_rumor = text.replace('谣言：', '').strip()
                    elif current_rumor and text.startswith('真相：'):
                        truth = text.replace('真相：', '').strip()
                        rumors_and_truths.append((current_rumor, truth))

                        current_rumor = None

                # 将提取的谣言和真相内容保存到 rumor_detail 集合中
                for rumor, truth in rumors_and_truths:
                    # 对真相进行分类
                    classification_result = classifier.classify_text(truth)
                    data = {
                        'url': url,
                        'date': date,
                        'rumor': rumor,
                        'truth': truth,
                        'classification_result': classification_result
                    }
                    await detail_collection.insert_one(data)
        except Exception as e:
            print(f"处理 {url} 时出现错误: {e}")



