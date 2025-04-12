from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random


def setup_driver():
    """设置 Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 启用无头模式
    options.add_argument("--start-maximized")  # 最大化窗口
    options.add_argument("--disable-blink-features=AutomationControlled")  # 防止被识别为爬虫
    driver = webdriver.Chrome(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe", options=options)
    return driver


def random_wait():
    """模拟人类行为的随机等待."""
    time.sleep(random.uniform(1, 3))


def fetch_posts(keyword, cursor, output_data):
    """爬取指定页的贴吧搜索结果并返回数据."""
    driver = setup_driver()
    url_template = "https://tieba.baidu.com/f/search/res?isnew=1&kw=&qw={keyword}&rn=10&pn={page}&sm=2"

    try:
        # 只爬取指定的cursor页
        page_url = url_template.format(keyword=keyword, page=(cursor - 1) * 10)
        print(f"正在爬取第 {cursor} 页...")

        driver.get(page_url)
        random_wait()

        try:
            # 等待搜索结果加载完成
            post_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s_post"))
            )
            print(f"发现 {len(post_elements)} 个帖子.")
        except Exception as e:
            print(f"解析帖子错误: {e}")
            return output_data  # 如果爬取失败，直接返回空数据

        for post in post_elements:
            try:
                # 更新选择器，逐一解析所需信息
                title = post.find_element(By.CSS_SELECTOR, ".p_title a").text.strip()
                link = post.find_element(By.CSS_SELECTOR, ".p_title a").get_attribute("href")
                author = post.find_element(By.CSS_SELECTOR, ".p_violet").text.strip()
                content = post.find_element(By.CSS_SELECTOR, ".p_content").text.strip()
                time_posted = post.find_element(By.CSS_SELECTOR, ".p_green").text.strip()
                output_data.append({
                    "title": title,
                    "url": link,
                    "author": author,
                    "content": content,
                    "time": time_posted
                })
            except Exception as e:
                print(f"解析帖子详情错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        driver.quit()

    # 返回抓取的数据
    return output_data

if __name__ == "__main__":

     keyword = input("请输入要查询的关键词: ")
     tieba_data = []
     tieba_data = fetch_posts(keyword, 1, tieba_data)
     print(tieba_data)
