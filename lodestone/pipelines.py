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
        self.f = open("ls.txt", "a")

    def process_item(self, item, spider):
        self.f.write("https://jp.finalfantasyxiv.com/lodestone/%s/%s/\n"%(item["type_string"], item["lodestone_id"]))
        return item

    def close_spider(self, spider):
        self.f.close()

class LinkshellPipeline(BasePipeLine):

    def process_item(self, item, spider):
        try:
            self.cur.execute(" INSERT INTO linkshells (name, world, lodestone_id) VALUES (%s, %s, %s)", (
                item["name"],
                item["world"],
                item["lodestone_id"]
            ))
            self.connection.commit()
            spider.logger.info("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))
        except psycopg2.DatabaseError as error:
            self.cur.execute("ROLLBACK")
            self.connection.commit()
            spider.logger.info("linkshells %s is existed"%(item["name"]))
        return item

class CrossLinkshellPipeline(BasePipeLine):

    def process_item(self, item, spider):
        try:
            self.cur.execute(" INSERT INTO crossworld_linkshells (name, datacenter, lodestone_id) VALUES (%s, %s, %s)", (
                item["name"],
                item["world"],
                item["lodestone_id"]
            ))
            self.connection.commit()
            spider.logger.info("%s@%s in [%s] is commited"%(item["name"], item["world"], item["lodestone_id"]))
        except psycopg2.DatabaseError as error:
            self.cur.execute("ROLLBACK")
            self.connection.commit()
            spider.logger.info("linkshells %s is existed"%(item["name"]))
        return item

class BaseCharacterPipeline(BasePipeLine):

    def create_character(self, item, spider):
        self.cur.execute("SELECT id from characters WHERE lodestone_id = %s", (item['lodestone_id'],))
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
        return character_id

class CrossLinkshellCharacterPipeline(BaseCharacterPipeline):

    def process_item(self, item, spider):
        character_id = self.create_character(item, spider)

        if character_id > 0:
            crossworld_linkshell_id = 0
            if item["is_owner"]:
                self.cur.execute("UPDATE crossworld_linkshells SET owner_id = %s WHERE lodestone_id = %s RETURNING id", (character_id, item['cwls_lodestone_id']))
                result = self.cur.fetchone()
                crossworld_linkshell_id = result[0]
            else:
                self.cur.execute("SELECT id from crossworld_linkshells WHERE lodestone_id = %s", (item['cwls_lodestone_id'],))
                result = self.cur.fetchone()
                crossworld_linkshell_id = result[0]
            if crossworld_linkshell_id > 0:
                try:
                    self.cur.execute("INSERT INTO characters_on_crossworld_linkshells (crossworld_linkshell_id, character_id) VALUES (%s, %s)", (
                        crossworld_linkshell_id,
                        character_id
                    ))
                    self.connection.commit()
                except psycopg2.DatabaseError as error:
                    self.cur.execute("ROLLBACK")
                    self.connection.commit()
        return item

class LinkshellCharacterPipeline(BaseCharacterPipeline):

    def process_item(self, item, spider):
        character_id = self.create_character(item, spider)

        if character_id > 0:
            linkshell_id = 0
            if item["is_owner"]:
                self.cur.execute("UPDATE linkshells SET owner_id = %s WHERE lodestone_id = %s RETURNING id", (character_id, item['ls_lodestone_id']))
                result = self.cur.fetchone()
                linkshell_id = result[0]
            else:
                self.cur.execute("SELECT id from linkshells WHERE lodestone_id = %s", (item['ls_lodestone_id'],))
                result = self.cur.fetchone()
                linkshell_id = result[0]
            if linkshell_id > 0:
                try:
                    self.cur.execute("INSERT INTO characters_on_linkshells (linkshell_id, character_id) VALUES (%s, %s)", (
                        linkshell_id,
                        character_id
                    ))
                    self.connection.commit()
                except psycopg2.DatabaseError as error:
                    self.cur.execute("ROLLBACK")
                    self.connection.commit()
        return item
