import requests
from bs4 import BeautifulSoup as BS
import html5lib
import urllib.parse
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
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
        with open("data/" + novel_name + ".txt", "w", encoding="utf-8") as file:
            file.write(data)


def save_all_novels_in_category(link, save_to_file=True):
    end = get_max_page_of_category(link)
    for i in range(1, end+1):
        print('Starting: ', i)
        url = link + str(i) + ".html"
        novels = get_novels_from_category_url(url)
        # print('Total: ', len(novels))
        log_content = ""
        for novel in novels:
            log_content += novel[0] + '\t' + novel[1] + '\n'
        if save_to_file:
            with open('links_get.txt', 'a', encoding='utf-8') as file:
                file.write(log_content)


def get_max_page_of_category(url):
    url = url + "1.html"
    r = requests_retry_session().get(url)
    r.encoding = "GBK"
    soup = BS(r.text, 'html5lib')
    return int(soup.find('span', id='pagestats').text.strip().split('/')[1])

start_time = time.time()
save_all_novels_in_category("http://www.xinyushuwu.com/xianxia/")
print("--- %s seconds ---" % (time.time() - start_time))


"""--- 3.775822877883911 seconds ---"""