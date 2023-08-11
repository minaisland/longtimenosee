# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class BasePipeLine:

    def __init__(self):
        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')
        port = os.getenv('DB_PORT')

        self.connection = psycopg2.connect(host=hostname, database=database, user=username, password=password, port=port)

        self.cur = self.connection.cursor()

    def close_spider(self, spider):

        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()


class GeneratorURLPipeline:

    def __init__(self):
        print("GeneratorURLPipeline")
        self.f = open("ls.txt", "a")

    def process_item(self, item, spider):
        self.f.write("https://jp.finalfantasyxiv.com/lodestone/linkshell/%s/\n"%item["lodestone_id"])
        return item

    def close_spider(self, spider):
        self.f.close()

class LinkshellPipeline(BasePipeLine):

    def process_item(self, item, spider):
        self.cur.execute(" INSERT INTO linkshells (name, world, lodestone_id) VALUES (%s, %s, %s)", (
            item["name"],
            item["world"],
            item["lodestone_id"]
        ))
        self.connection.commit()
        print("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))
        return item

class CrossLinkshellPipeline(BasePipeLine):

    def process_item(self, item, spider):
        self.cur.execute(" INSERT INTO crossworld_linkshells (name, datacenter, lodestone_id) VALUES (%s, %s, %s)", (
            item["name"],
            item["world"],
            item["lodestone_id"]
        ))
        self.connection.commit()
        print("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))
        return item

class CrossLinkshellCharacterPipeline(BasePipeLine):

    def process_item(self, item, spider):
        self.cur.execute(" SELECT id FROM characters where lodestone_id = %s", (item['lodestone_id'],))
        result = self.cur.fetchone()

        character_id = 0
        if result:
            character_id = result[0]
            spider.logger.warn("Item already in database: %s" % item['name'])
        else:
            self.cur.execute(" INSERT INTO characters (name, world, lodestone_id, avatar_url) VALUES (%s, %s, %s, %s) RETURNING id", (
                item["name"],
                item["world"],
                item["lodestone_id"],
                item["avatar_url"]
            ))
            result = self.cur.fetchone()
            character_id = result[0]

            spider.logger.info("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))

        self.cur.execute("SELECT id FROM crossworld_linkshells where lodestone_id = %s", (item['cwls_lodestone_id'],))
        result = self.cur.fetchone()
        if result and character_id > 0:
            try:
                self.cur.execute(" INSERT INTO characters_on_crossworld_linkshells (crossworld_linkshell_id, character_id) VALUES (%s, %s)", (
                    result[0],
                    character_id
                ))
                self.connection.commit()
            except psycopg2.DatabaseError as error:
                self.cur.execute("ROLLBACK")
                self.connection.commit()
        return item

class CharacterPipeline(BasePipeLine):

    def process_item(self, item, spider):
        self.cur.execute("SELECT id from characters where lodestone_id = %s", (item['lodestone_id'],))
        result = self.cur.fetchone()

        character_id = 0
        if result:
            character_id = result[0]
            spider.logger.warn("Item already in database: %s" % item['name'])
        else:
            self.cur.execute(" INSERT INTO characters (name, world, lodestone_id, avatar_url) VALUES (%s, %s, %s, %s) RETURNING id", (
                item["name"],
                item["world"],
                item["lodestone_id"],
                item["avatar_url"]
            ))
            result = self.cur.fetchone()
            character_id = result[0]

            spider.logger.info("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))

        self.cur.execute("SELECT id from linkshells where lodestone_id = %s", (item['ls_lodestone_id'],))
        result = self.cur.fetchone()
        if result and character_id > 0:
            try:
                self.cur.execute("INSERT INTO linkshell_groups (linkshell_id, character_id) VALUES (%s, %s)", (
                    result[0],
                    character_id
                ))
                self.connection.commit()
            except psycopg2.DatabaseError as error:
                self.cur.execute("ROLLBACK")
                self.connection.commit()
        return item
