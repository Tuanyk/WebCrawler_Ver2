import requests
from bs4 import BeautifulSoup as BS
import html5lib
import urllib.parse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from slugify import slugify
import time

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 400, 403, 408, 409, 413, 429, 503),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_content_from_url(url):
    """Cào nội dung trong 1 chương truyện"""
    r = requests_retry_session().get(url)
    r.encoding = "GBK"
    soup = BS(r.text, 'html5lib')
    title = soup.find("h3").text.strip()
    content = soup.find("p", id="articlecontent").text
    return title, content


def get_links_from_url(url):
    """Lấy link từ trang truyện"""
    r = requests_retry_session().get(url)
    r.encoding = "GBK"
    soup = BS(r.text, 'html5lib')

    links_list = soup.find('div', class_='ml_list').find('ul').find_all('a')

    links = []
    for item in links_list:
        link = urllib.parse.urljoin(url, item['href'])
        links.append(link)
    
    return links

def get_novels_from_category_url(url):
    """Hàm lấy link về truyện"""
    r = requests_retry_session().get(url)
    r.encoding = "GBK"
    soup = BS(r.text, 'html5lib')

    links_list = soup.find('div', class_='fl_right').find_all('h3')

    novels = []

    for item in links_list:
        name = item.find('a').text
        link = item.find('a')['href']
        novels.append([name, link])

    return novels


def get_novels_from_allvisit_url(url):
    r = requests_retry_session().get(url)
    r.encoding = "GBK"
    soup = BS(r.text, 'html5lib')

    links_list = soup.find('table', id='rankinglist').find_all('tr')


    novels = []
    num = 0
    for link_tag in links_list:
        num += 1
        if num == 1:
            continue
        novel_name, link = link_tag.find('a').text, link_tag.find('a')['href']
        novels.append([novel_name, link])

    return novels


def save_novel_content_from_url(novel_name, url):
    links_chapter = get_links_from_url(url)
    data = ""
    num = 0
    for link in links_chapter:
        num += 1
        print(num, "/", len(links_chapter))
        title, content = get_content_from_url(link)
        data += title + "\n\n" + content
        with open("data/" + slugify(novel_name) + ".txt", "w", encoding="utf-8") as file:
            file.write(data)


def get_novels():
    with open('novel_links.txt', 'r', encoding='utf-8') as file:
        data = file.read().strip().split('\n')

    return data


novels = get_novels()

for index, novel in enumerate(novels):
    start_time = time.time()
    try:
        save_novel_content_from_url(str(index), novel)
        with open('saved_novel.txt', 'a', encoding='utf-8') as file:
            file.write(novel + '\n')
    except AttributeError:
        with open('error_save_novel.txt', 'a', encoding='utf-8') as file:
            file.write(novel + '\n')
    print("--- %s seconds ---" % (time.time() - start_time))