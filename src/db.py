"""
Users(userID, username, password, registerDate)
Articles(articleID, title, author, publishDate, content)
Comments(commentID, articleID, userID, commentDate, content)
Tags(tagID, tagName)
ArticleTags(articleID, tagID)
Categories(catID, catName)
ArticleCategories(catID, articleID)
ArticleViews(articleID, userID, viewDate)
here
- In Comments, articleID references Articles and userID references Users
- In ArticleTags, articleID references Articles and tagID references Tags
- In ArticleCategories, catID references Categories and articleID references Articles
- In ArticleViews, articleID references Articles and userID references Users
"""


from typing import List

import oracledb
from oracledb.exceptions import DatabaseError

from queries import ARTICLE_TAGS, ARTICLES_SORTED, ARTICLES_BY_CATEGORY, ARTICLES_BY_TAG


class User:
    def __init__(self, user_id, username, password, registerDate, roleName):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.registerDate = registerDate
        self.roleName = roleName
        
    @property
    def is_admin(self):
        return self.roleName == 'admin'


class UserTable:
    def __init__(self, conn):
        self.conn: oracledb.connection.Connection = conn

    def create(self, user: User):
        sql = "INSERT INTO users (username, password, registerDate) VALUES (:username, :password, :registerDate)"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, username=user.username, password=user.password, registerDate=user.registerDate)
        self.conn.commit()

    def delete(self, userID):
        sql = "DELETE FROM users WHERE userID = :userID"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, userID=userID)
        self.conn.commit()

    def exists(self, userID):
        sql = "SELECT COUNT(*) FROM users WHERE userID = :userID"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, userID=userID)
            return cursor.fetchone()[0] > 0

    def get(self, userID):
        sql = """SELECT userID, username, password, registerDate, roleName
                 FROM users
                 WHERE userID = :userID"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, userID=userID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("User not found")
            return User(*row)

    def validate(self, username: str, password: str) -> str:
        """
        Give a username and password, return the user's ID if the user exists. Otherwise return None.
        
        Args:
            username (str): The username to check
            password (str): The password to check
        Returns:
            str: The user's ID if the user exists, otherwise None
        """
        sql = """SELECT COUNT(*), userID
                 FROM users
                 WHERE username = :username AND password = :password
                 GROUP BY userID"""

        with self.conn.cursor() as cursor:
            cursor.execute(sql, username=username, password=password)
            result = cursor.fetchone()

            if result and result[0] == 1:
                return result[1]
            else:
                return None


class Article:
    def __init__(self, articleID, title, author, publishDate, content, tags: List[str]):
        self.articleID = articleID
        self.title = title
        self.author = author
        self.publishDate = publishDate
        self.content = content
        self.tags = tags
        
    def __str__(self):
        return f"""
        Article {self.articleID}
        Title: {self.title}
        Date: {self.publishDate}
        Tags: {self.tags}
        """
        
    __repr__ = __str__


class ArticleTable:

    sort_options = ['date', 'title', 'author']

    def __init__(self, conn):
        self.conn = conn

    def get(self, articleID):
        sql = """SELECT articleID, title, author, publishDate, content
                 FROM articles WHERE articleID = :articleID"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, articleID=articleID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Article not found")
            return Article(row.articleID, row.title, row.author, row.publishDate, row.content)

    def get_all(self, sort_by='date') -> List[Article]:
        assert sort_by in self.sort_options

        articles = []

        if sort_by == 'date':
            sort_by = 'publishDate'
        elif sort_by == 'title':
            sort_by = 'title'
        elif sort_by == 'author':
            sort_by = 'author'

        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLES_SORTED, sort_by=sort_by)
            rows = cursor.fetchall()
            for row in rows:
                articleID = row[0]
                cursor.execute(ARTICLE_TAGS, articleID=articleID)
                tags = [row[0] for row in cursor.fetchall()]
                articles.append(Article(*row, tags=tags))
                
        return articles
    
    def get_from_category(self, category: str) -> List[Article]:
        
        articles = []
        
        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLES_BY_CATEGORY, catName=category)
            rows = cursor.fetchall()
            for row in rows:
                articleID = row[0]
                cursor.execute(ARTICLE_TAGS, articleID=articleID)
                tags = [row[0] for row in cursor.fetchall()]
                articles.append(Article(*row, tags=tags))
        
        return articles

    def get_tags(self, articleID: int):
        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLE_TAGS, articleID=articleID)
            return [row[0] for row in cursor.fetchall()]
                
    def add_view(self, articleID: int, userID: int):
        pass


class NewsDB:
    def __init__(self, conn):
        self.conn: oracledb.connection.Connection = conn
        self.users = UserTable(self.conn)
        self.articles = ArticleTable(self.conn)
