#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : read_data.py
import pymongo
import json
from loguru import logger
from extract import UU
from example.links import urls
from clearner.clean import RemoveUseless


class MongoCli(object):
    def __init__(self):
        self.u = UU()
        self.r = RemoveUseless()

    def mongo_dbs(self):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        db = client['spider_data']
        return db

    def insert(self, coll, data):
        db = self.mongo_dbs()
        resp = db[f'{coll}'].insert_one(data)
        logger.info('ItemData: %s' % resp)

    def find(self):
        db = self.mongo_dbs()
        # infos = db['model'].find({}).limit(100)
        infos = db['model'].find({})
        for info in infos:
            url = info.get('url')
            yield url

    def delete_one(self, collection, query):
        """
        Deletes the first document matching the given query in the specified collection.

        Args:
            collection (str): The name of the MongoDB collection.
            query (dict): A MongoDB query document specifying the data to match.

        Returns:
            DeleteResult: A pymongo.results.DeleteResult object containing information about the deletion operation.
        """

        db = self.mongo_dbs()
        result = db[collection].delete_one(query)
        if result.deleted_count == 1:
            logger.info(f"Deleted 1 document from '{collection}' collection.")
        else:
            logger.info(f"No document found matching the query in '{collection}' collection.")
        return result

    def uu_(self, url):
        result = self.u.uu(url=url)
        if result:
            article = result.get('article')
            title = result.get('title')
            title = title.split('_')[0] if title else ''
            if len(title) <= 5:
                self.delete_one('model', {'url': url})
                return
            for ti in ['齐鲁网', "新华网", "人民网", "频道", "中新网", "新闻", "新浪网", "网易新闻", "腾讯新闻", "2018",
                       "2019", "2020", "2021", "广播"]:
                if ti in title:
                    self.delete_one('model', {'url': url})
                    return
            html = result.get('html')
            end = self.r.clean_article_html(html)
            cle_html = end.replace('\n', '').replace(' ', '')
            items = {
                "url": url,
                "title": title,
                "content": article,
                "html": cle_html
            }
            return items

    def main(self):
        for i in self.find():
            print(i)
            item = self.uu_(i)
            print(item)
            if item:
                with open('model_data.json', 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')  # 添加换行符


if __name__ == '__main__':
    mc = MongoCli()
    mc.main()
