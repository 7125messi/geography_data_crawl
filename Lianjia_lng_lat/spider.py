import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool

def get_one_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    pattern = re.compile('<li>.*?pic-panel.*?_blank.*?"(.*?)">.*?info-panel.*?<a.*?">(.*?)</a>.*?where.*?<span>(.*?)&.*?<span>(.*?)&.*?price.*?>(\d+)<.*?</li>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        yield{
            'room_link':str('http://sh.lianjia.com')+item[0].lstrip(' href=\"'),
            'room_detail':item[1],
            'room_shape':item[2],
            'room_size':item[3],
            'price':item[4]
        }

def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')
        f.close()


def main(page):
    url = 'http://sh.lianjia.com/zufang/putuo/d'+str(page)+'k0to2500'
    html = get_one_page(url)
    for item in parse_one_page(html):
        write_to_file(item)


if __name__ == '__main__':
    #for i in range(20):
    #    main(i)
    pool = Pool()
    pool.map(main,[i for i in range(4)])