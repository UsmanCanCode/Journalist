# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
import mysql.connector
from SiteSpiders.settings import SECRET_KEY, USER, DATABASE_NAME, DATABASE_URL, DATABASE_PORT


class NewsPipeline:

    # any processing of items such as removing whitespace
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        return item

class NewsSaveToMySQL:

    articles_table = "articles"
    authors_table = "authors"

    #initialize pipeline to save items to the database
    def __init__(self):

        # connect to the database
        self.conn = mysql.connector.connect(
            host=  DATABASE_URL,
            user= USER,
            password= SECRET_KEY,
            database= DATABASE_NAME
        )

        # create a cursor to execute commands to the database
        self.cur = self.conn.cursor()


    # what to do when spider opens in scrapy
    # open_sider is scrapy method
    def open_spider(self, spider):


        create_authors_table = """
                CREATE TABLE IF NOT EXISTS {}(
                id int NOT NULL auto_increment,
                author_name VARCHAR(255), 
                profile_url VARCHAR(300),
                twitter_url VARCHAR(300),
                news_site VARCHAR(100),
                PRIMARY KEY (id),
                CONSTRAINT unique_name UNIQUE (id, author_name)
                );        
        """.format(self.authors_table)

        create_articles_table = """
                CREATE TABLE IF NOT EXISTS {}(
                id INT NOT NULL auto_increment,
                title TEXT,
                url VARCHAR(400),
                author_id INT, 
                PRIMARY KEY (id),
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
                );         
        """.format(self.articles_table)

        try:
            # create author table in the news database if not exist
            self.cur.execute(create_authors_table)

            # create article table in news database if not exist
            self.cur.execute(create_articles_table)

        except mysql.connector.Error as err:
            error_msg = f"{err} creating table error"
            logging.log(msg=error_msg)

        # upon closing spider
    def close_spider(self, spider):

        # end of spider close cursor and connection
        self.cur.close()
        self.conn.close()

    #  process items in mysql pipeline and add to the database
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # add author and profile_url to the table

        # check if author already in table using profile url
        query = """SELECT * FROM {}
                WHERE profile_url LIKE %s;""".format(self.authors_table)

        try:
            self.cur.execute( query,
                (adapter['author_profile_link'],)

            )
        except mysql.connector.Error as err:
            error_msg = f"{err} excuting select author profile error"
            logging.log(msg=error_msg)

        row = self.cur.fetchone()
        if row == None:

            query_insert_authors = """INSERT IGNORE INTO {} (
                    author_name, profile_url, twitter_url, news_site)
                    VALUES ( %s, %s, %s, %s);""".format(self.authors_table)
            try:
                self.cur.execute(query_insert_authors,
                    (
                        adapter['author_name'],
                        adapter['author_profile_link'],
                        adapter['author_twitter_link'],
                        adapter['news_site']
                    )
                )
            except mysql.connector.Error as err:
                error_msg = f"{err} insert into authors table"
                logging.log(msg=error_msg)

            self.conn.commit()
        else:
            if row[1] != None:
            # record already in database
            #row 0 =  id
                adapter['author_name'] = row[1]
                # adapter['author_profile_link'] = row[2]
                adapter['author_twitter_link'] = row[3]
                # adapter['news_site'] = row[4]

            rows_rest = self.cur.fetchall()  # for errors get rest of rows in above search

        # get the id of the author from authors table to be used for article table
        try:
            query_author_id = """
                SELECT id FROM {}
                WHERE author_name LIKE %s;
                """.format(self.authors_table)

            self.cur.execute(query_author_id
                ,(
                    adapter['author_name'],
                )
            )
        except mysql.connector.Error as err:
            error_msg = f"{err} getting author id for foreign id"
            logging.log(msg=error_msg)

        try:
            author_foreign_id = self.cur.fetchone()[0]
        except mysql.connector.Error:
            logging.log(msg=f"{author_foreign_id} THIS IS THE fetchone in pipeline")
        except Exception as e:
            logging.log(msg=f"{e} exception in fetch one")

        #error get all
        remaing_row = self.cur.fetchall()

        try:
            query_insert_articles = """
                INSERT INTO {} 
                (title, url, author_id)
                VALUES (%s, %s, %s);
                """.format(self.articles_table)

            self.cur.execute(query_insert_articles
                ,
                (adapter["article_title"], adapter["article_url"], author_foreign_id)
            )
        except mysql.connector.Error as err:
            error_msg = f"{err} inserting into articles"
            logging.log(msg=error_msg)

        self.conn.commit()

        return item




0######################################
### Test Pipeline for quotes spider ###
#######################################

class AuthorPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        return item


class AuthorMysqlPipeline:

    def __init__(self):
        # connect to the database
        self.conn = mysql.connector.connect(
            host=DATABASE_URL,
            user= USER,
            password=SECRET_KEY,
            database=DATABASE_NAME
        )

        # create a cursor to execute commands to the database
        self.cur = self.conn.cursor()



    def open_spider(self, spider):
        # create books table in the books database if not exist
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS authors(
            id int NOT NULL auto_increment,
            url VARCHAR(255),
            author_name VARCHAR(255), 
            PRIMARY KEY (id),
            CONSTRAINT unique_name UNIQUE (id, author_name)
            );
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes(
            id INT NOT NULL auto_increment,
            quote TEXT,
            author_name VARCHAR(255), 
            author_id INT, 
            PRIMARY KEY (id),
            FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
            );
            """
        )

    def close_spider(self, spider):
        # end of spider close cursor and connection
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # add author and url to the table

        self.cur.execute(
            """SELECT author_name FROM authors
            WHERE author_name LIKE %s""",
            (adapter['name'],)

        )
        row = self.cur.fetchone()
        if row == None:
            self.cur.execute(
                """INSERT IGNORE INTO authors (
                url, author_name)
                VALUES ( %s, %s);""", (
                    adapter['author_url'],
                    adapter['name'],
            )
            )
            self.conn.commit()
        else:
            rows_rest = self.cur.fetchall() # for errors get rest of rows in above search

        #get author id
        self.cur.execute(
            """
            SELECT id FROM authors
            WHERE author_name LIKE %s;
            """,
            (adapter['name'],)

        )
        author_foreign_id = self.cur.fetchone()[0]


        self.cur.execute(
            """
            INSERT INTO quotes (
            quote, author_name, author_id)
            VALUES (%s, %s,%s);
            """,
            (adapter['quote'], adapter['name'], author_foreign_id)

        )
        self.conn.commit()

        return item




### Test Pipeline for books spider ###

class SitespidersPipeline:

    # clean up items
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # strip whitespace
        field_names = adapter.field_names()
        for field_name in field_names:

            if field_name == 'price':
                value = adapter.get(field_name).replace('£', '')
                adapter[field_name] = float(value)
            else:
                value = adapter.get(field_name)
                adapter[field_name] = value.strip().lower()

        return item





class SaveToMysqlPipeline:

    def __init__(self):
        # connect to the database
        self.conn = mysql.connector.connect(
            host=DATABASE_URL,
            user=USER,
            password=SECRET_KEY,
            database=DATABASE_NAME
        )

        # create a cursor to execute commands to the database
        self.cur = self.conn.cursor()

        # create books table in the books database if not exist
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books(
            id int NOT NULL auto_increment,
            url VARCHAR(255),
            title TEXT, 
            price DECIMAL,
            description TEXT,
            PRIMARY KEY (id)
            )
            
            """
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        # end of spider close cursor and connection
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # add items to the table
        self.cur.execute(
            """INSERT INTO books (
            url, title, price, description)
            VALUES ( %s, %s, %s, %s)""",(
            adapter['url'],
            adapter['title'],
            adapter['price'],
            adapter['description'])
        )
        self.conn.commit()
        return item


