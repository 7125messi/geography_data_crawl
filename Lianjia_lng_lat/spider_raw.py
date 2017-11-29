import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode
import json
from bs4 import BeautifulSoup
import re
from config import *
import pymongo
from  multiprocessing import Pool
from json import JSONDecodeError

client = pymongo.MongoClient(MONGO_URL,connect=False)
db = client(MONGO_DB)


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}

def get_page_index(offset,keyword):
    data = {
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':1
    }
    url = 'https://www.toutiao.com/search_content/?'+ urlencode(data)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None

def parse_page_idnex(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item  in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass

def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详细页出错',url)
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile('BASE_DATA.galleryInfo =(.*?);',re.S)
    result = re.search(images_pattern,html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_iamges')
            images = [item.get('url') for item in sub_images]
            return {
                'title':title,
                'url':url,
                'images':images
            }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功',result)
        return True
    return False



def main(offset):
    html = get_page_index(offset,'KEYWORD')
    #print(html)
    for url in parse_page_idnex(html):
        #print(url)
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html,url)
            #print(result)
            save_to_mongo(result)

if __name__ == '__main__':
    main()
    groups = [x*20 for x in range(GROUP_START,GROUP_END+1)]
    pool = Pool()
    pool.map(main,groups)
