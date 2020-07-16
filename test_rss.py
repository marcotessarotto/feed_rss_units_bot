import urllib
import feedparser
import requests
from bs4 import BeautifulSoup

dict_rss_items = {}

# def get_content_from_page(URL, attr_name='class', attr_value='foglia-box-content'):
#     if URL is None:
#         return None
#
#     soup = BeautifulSoup(urllib.request.urlopen(URL).read(), 'html.parser')
#
#     results = soup.find_all('div', attrs={attr_name: attr_value})  # https://stackoverflow.com/a/14694669/974287
#
#     if len(results) == 0:
#         return None
#
#     # s = results[0].get_text()
#     # s = process_node(results[0])
#
#     if s is not None:
#         s = s.strip()
#
#         def sub_split(x):
#             return ' '.join(x.split())
#
#         # remove single occurrences of \n but keep in place \n\n(ugly but works)
#         s = '\n\n'.join(sub_split(r) for r in s.split('\n\n'))
#
#     return s


def read_feed(url):
    # https://stackoverflow.com/questions/46641848/feedparser-returns-a-saxparseexception
    headers = []
    web_page = requests.get(url, headers=headers, allow_redirects=True)
    content = web_page.content.strip()  # drop the first newline (if any)
    feed = feedparser.parse(content)

    # feed = feedparser.parse(url)
    print(feed)
    print(feed.entries)

    for item in feed.entries:

        rss_id = item["id"]
        rss_title = item["title"]
        rss_link = item["link"]
        updated_parsed = item["updated_parsed"]
        link = item["link"]
        summary = item["summary"]

        # print(item)
        print(f"rss_id={rss_id} link={link}")

        dict_rss_items[rss_id] = item


UNITS_RSS = 'https://www.units.it/feed/notizie/ateneo'


read_feed(UNITS_RSS)

print(len(dict_rss_items))