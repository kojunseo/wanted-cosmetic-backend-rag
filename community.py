import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://sungyesa.com/"
}
API_HEADERS=  {
 "project": "PROMPTHON_PRJ_451",
 "apiKey": os.getenv("WANTED_API_KEY"),
}
API_URL = "https://api-laas.wanted.co.kr/api/preset/chat/completions"
HASH_VALUE = "e31f16e98d8480e459db075bb2ce9d39c6849b5dfcf716138534ba0dec487a5b"

def fetch_page(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def parse_contents(soup, num):
    contents = []
    us_result = soup.find('div', class_='us_result')
    if us_result:
        list_items = us_result.find_all('li')
        for li in list_items[:num]:
            us_content = li.find('div', class_='us_content')
            link = li.find('a')
            title = li.find('a').text.strip()
            if us_content:
                contents.append([us_content.text.strip(), link['href'], title])
            else:
                print("us_content not found in this list item")
    else:
        print("us_result not found")
    return contents

def send_request(content):
    body = {
        "hash": HASH_VALUE,
        "params": {"context": content},
        "preset": "community_summary_chain",
    }
    response = requests.post(API_URL, headers=API_HEADERS, json=body)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def community_summary(keyword,num):
    # 构建URL
    if " " in keyword:
        keyword = keyword.replace(" ", "+")
    url = f"https://sungyesa.com/new/plugin/elasticsearch/?gr_id=002&stx={keyword}"
    soup = fetch_page(url, HEADERS)
    results = []
    links = []
    titles = []
    if soup:
        contents = parse_contents(soup,num)
        with ThreadPoolExecutor(max_workers=3) as executor:
            contents_dict = {executor.submit(send_request, content[0]): [content[0], content[1], content[2]] for content in contents}
            
            for future in as_completed(contents_dict):                
                content = contents_dict[future]
                try:
                    result = future.result()
                    results.append(result.replace("요약", "").replace(":", ""))
                    links.append(content[1])
                    titles.append(content[2])
                except Exception as e:
                    print(f"Request failed for content: {content}, Error: {e}")
        return results, links, titles

if __name__ == "__main__":
    result, links, titles = community_summary("코성형",5)
    print(result)
    print(links)
    print(titles)


