# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class TravelNotesPipeline(object):
    def process_item(self, item, spider):

        db = pymysql.connect(host="localhost", user="root",
                             password="admin", db="travel_notes", port=3306)
        cur = db.cursor()
        sql_insert = """insert into mafengwo_travel_notes values(null, '%s', '%s',
                    '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                     '%s', '%s', '%s', '%s')
                """ % (item['title'], item['author'],
                       item['shareTime'], item['viewCount'],
                       item['commentCount'], item['favCount'],
                       item['shareCount'], item['startTime'],
                       item['duration'], item['personType'],
                       item['averageCost'], item['content'],
                       item['iid'])

        try:
            cur.execute(sql_insert)
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

        return item
