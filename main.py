from extract import UU
from example.links import urls
from clearner.clean import RemoveUseless

if __name__ == '__main__':

    u = UU()
    r = RemoveUseless()
    urls = ["https://news.cctv.com/2024/11/07/ARTIBP5pVTvgDNk0ujAOa600241107.shtml",
            "https://ckxxapp.ckxx.net/pages/2024/11/04/98fdd42941d6432782c4e2c4fb1dd322.html"]
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
