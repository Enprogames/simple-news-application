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


from datetime import datetime
import hashlib

import oracledb
from oracledb.exceptions import DatabaseError


class User:
    def __init__(self, user_id, username, password, registerDate):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.registerDate = registerDate


class UserTable:
    def __init__(self, conn):
        self.conn = conn

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
        sql = """SELECT userID, username, password, registerDate
                 FROM users WHERE userID = :userID"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, userID=userID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("User not found")
            return User(row.userID, row.username, row.password, row.registerDate)

    def validate(self, username: str, password: str):
        sql = """SELECT COUNT(*) FROM users WHERE username = :username AND password = :password"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, username=username, password=password)
            return cursor.fetchone()[0] > 0
        
    def hash_pwd(self, pwd: str):
        return hashlib.sha512(pwd.encode('utf8')).hexdigest()


class Article:
    pass

class ArticleTable:
    pass


class ArticleTable:

    def __init__(self, conn):
        self.conn = conn


class NewsDB:
    def __init__(self, conn):
        self.conn = conn
        self.users = UserTable(self.conn)
        self.articles = ArticleTable(self.conn)
