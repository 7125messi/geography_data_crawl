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
    pattern = re.compile('<li.*?<h4>(.*?)</h4>.*?comment.*?<b>(.*?)</b>.*?<b>￥(.*?)</b>.*?tag-addr.*?addr">(.*?)<.*?comment-list.*?<b>(.*?)</b>.*?<b>(.*?)</b>.*?<b>(.*?)</b>.*?</li>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        yield{
            'shop_name':item[0],
            'comment_number':item[1],
            'avg_price':item[2],
            'address':item[3],
            'waste':item[4],
            'environment':item[5],
            'service':item[6]
        }

def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')
        f.close()


def main(page):
    url = 'http://www.dianping.com/search/category/1/10/r7p'+str(page)+'?aid=4064431%2C69852299%2C5527597%2C69267963%2C27234469%2C69231724&cpt=4064431%2C69852299%2C5527597%2C69267963%2C27234469%2C69231724'
    html = get_one_page(url)
    for item in parse_one_page(html):
        write_to_file(item)


if __name__ == '__main__':
    #for i in range(20):
    #    main(i)
    pool = Pool()
    pool.map(main,[i for i in range(20)])