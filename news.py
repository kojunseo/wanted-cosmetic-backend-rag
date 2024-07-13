import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://search.naver.com/"
}

API_HEADERS=  {
 "project": "PROMPTHON_PRJ_451",
 "apiKey": os.getenv("WANTED_API_KEY"),
}
API_URL = "https://api-laas.wanted.co.kr/api/preset/chat/completions"
HASH_VALUE = "0e8d2def889d51e6163e451944e143155f6884d96b195b9f02013f869724a396"

def fetch_page(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def parse_contents(soup, num):
    contents = []
    news_list = soup.find('ul', class_='list_news')
    news_items = news_list.find_all('li', class_="bx")
    for li in news_items[:num]:
        title = li.find("a", class_="news_tit").text.strip()
        link = li.find("a", class_="news_tit")['href']
        main_content = li.find("div", class_="dsc_wrap").text.strip()
        contents.append([title, link, main_content])
    return contents

def send_request(title, main_content):
    body = {
        "hash": HASH_VALUE,
        "params": {"title": title, "content": main_content},
        "preset": "community_summary_chain",
    }
    response = requests.post(API_URL, headers=API_HEADERS, json=body)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def news_summary(keyword,num):
    # 构建URL
    if " " in keyword:
        keyword = keyword.replace(" ","+")
    url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&query={keyword}"
    soup = fetch_page(url, HEADERS)
    results = []
    links = []
    titles = []
    if soup:
        contents = parse_contents(soup,num)
        with ThreadPoolExecutor(max_workers=3) as executor:
            contents_dict = {executor.submit(send_request, content[0], content[2]): [content[0], content[1], content[2]] for content in contents}
            
            for future in as_completed(contents_dict):
                content = contents_dict[future]
                try:
                    result = future.result()
                    results.append(result.replace("요약", "").replace(":", ""))
                    links.append(content[1])
                    titles.append(content[0])
                except Exception as e:
                    print(f"Request failed for content: {content}, Error: {e}")
        return results, links, titles

if __name__ == "__main__":
    result, links, titles = news_summary("코성형",3)
    print(result)
    print(links)
    print(titles)


