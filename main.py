from extract import UU
from example.links import urls
from clearner.clean import RemoveUseless
import re

if __name__ == '__main__':

    u = UU()
    r = RemoveUseless()
    urls = [
        # "https://www.aibase.com/zh/news/14255",
        # "https://www.ithome.com/0/819/145.htm",
        # "https://www.ithome.com/0/820/095.htm",
        "https://www.jiemian.com/article/12161417.html",

    ]
    for ul in urls:
        result = u.uu(url=ul)
        if result is None:
            continue
        # print(result)
        article = result.get('article')
        source = result.get('source')
        plain_text = result.get('plain_text')
        items = {
            "url": ul,
            "plain_text": plain_text,
            "source": source,
            # "html": cle_html
        }
        print(items)
        print('*' * 50)
