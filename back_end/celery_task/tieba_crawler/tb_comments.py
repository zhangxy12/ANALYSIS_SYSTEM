import time

import requests
from bs4 import BeautifulSoup
import random


# 爬取贴吧评论的函数
def crawl_tieba_comments(url):
    # 截取 URL 前 37 位
    url = url[:37]
    print(url)

    # 设置请求头，模拟浏览器请求
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
    ]

    headers = {
        'User-Agent': random.choice(user_agents)
    }

    all_comments = []
    page_num = 1

    while True:
        # 构建当前页的 URL
        current_url = f"{url}&pn={page_num}"

        try:
            # 发送HTTP请求获取页面内容
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            page_source = response.text
        except Exception as e:
            print(f"访问页面 {current_url} 时出错: {e}")
            break

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(page_source, 'html.parser')

        # 找到所有评论块
        comments = soup.find_all('div', class_='l_post')

        if not comments:
            # 如果没有找到评论，说明已经到了最后一页，退出循环
            break
        if page_num == 3:
            break

        # 循环处理所有评论
        for comment in comments:
            try:
                # 提取用户名
                user_name = comment.find('a', class_='p_author_name').text.strip()
                # 提取 IP 地址
                ip_element = comment.find('span', string=lambda t: 'IP属地' in str(t))
                ip = ip_element.text.strip().replace('IP属地:', '') if ip_element else '未获取到 IP'
                # 提取评论时间
                time_element = comment.find('span', class_='tail-info', string=lambda t: '-' in str(t))
                comment_time = time_element.text.strip() if time_element else '未获取到时间'
                # 提取评论内容
                content_element = comment.find('div', class_='d_post_content')
                content = content_element.text.strip() if content_element else '未获取到内容'
                print(content)
                all_comments.append({
                    'user_name': user_name,
                    'ip': ip,
                    'comment_time': comment_time,
                    'content': content,
                })
            except Exception as e:
                print(f"解析评论时出错: {e}")
        print(page_num)
        # 页码加 1，继续下一页
        page_num += 1
        time.sleep(10)

    return all_comments


# 示例使用
if __name__ == "__main__":
    url = "https://tieba.baidu.com/p/9475240608?"  # 替换为实际的贴吧帖子链接
    comments = crawl_tieba_comments(url)