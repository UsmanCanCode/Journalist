import click
from flask import current_app, g
import mysql.connector
from dotenv import load_dotenv
import os


def get_db():
    load_dotenv()

    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.environ.get("DATABASE_URL"),
            user=os.environ.get("USER"),
            password=os.environ.get("SECRET_KEY"),
            database=os.environ.get("DATABASE_NAME")
        )

        return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def get_authors():
    """
    get all DISTINCT authors from authors table
    :return: authors as list of tuples (id, author_name, profile_url, twitter_url, news_site)
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT id, author_name, profile_url, twitter_url, news_site
        FROM authors;
        """
    )

    authors = cur.fetchall()
    cur.close()

    return authors


def get_author_id(name=None):
    """
    get a single row of author by name
    :return: tuple (id, author_name, profile_url, twitter_url, news_site)
    """
    conn = get_db()
    cur = conn.cursor()

    query = """SELECT id, author_name, profile_url, twitter_url, news_site
            FROM authors
            WHERE author_name = %s;"""

    cur.execute(query, (name,))

    author = cur.fetchone()
    cur.fetchall()
    cur.close()

    return author


def get_articles():
    """
    get all DISTINCT articles
    :return: articles as list of tuples (title, url, author_id)
    """
    conn = get_db()
    cur = conn.cursor()

    query = f"""SELECT DISTINCT title, url, author_id 
            FROM articles;"""
    cur.execute(query)

    articles = cur.fetchall()
    cur.close()

    return articles


def get_articles_by_id(author_id=None):
    """
    get all DISTINCT article by id
    :return: articles by id as list of tuples (title, url, author_id)
    """
    conn = get_db()
    cur = conn.cursor()

    query = f"""SELECT DISTINCT title, url, author_id 
                FROM articles
                WHERE author_id = {author_id};"""
    cur.execute(query)

    articles = cur.fetchall()
    cur.close()

    return articles