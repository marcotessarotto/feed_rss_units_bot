import feedparser
import requests


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

        print(item)
        print(rss_id)
        print(updated_parsed)

UNITS_RSS = 'https://www.units.it/feed/notizie/ateneo'


read_feed(UNITS_RSS)