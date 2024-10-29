from extract import UU
from example.links import urls
from clearner.clean import RemoveUseless

if __name__ == '__main__':

    u = UU()
    r = RemoveUseless()
    for ul in urls:
        result = u.uu(url=ul)
        if result is None:
            continue
        article = result.get('article')
        plain_text = result.get('plain_text')
        items = {
            "url": ul,
            "plain_text": plain_text,
            # "html": cle_html
        }
        print(items)
        print('*' * 50)
