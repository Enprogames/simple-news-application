"""
Main database functionality.

@author: Ethan Posner
@date: 2023-04-10

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


from typing import List, Union

import oracledb
from oracledb.exceptions import DatabaseError

from queries import (ADD_COMMENT, ADD_VIEW, ARTICLE_COMMENTS, ARTICLE_TAGS,
                     ARTICLES_SORTED, ARTICLES_BY_CATEGORY,
                     ARTICLES_BY_TAG, CATEGORY_EXISTS, CHECK_USER_EXISTS, CREATE_USER, DELETE_USER, GET_USER, HIGHEST_COMMENT_ID, SINGLE_ARTICLE, SINGLE_CATEGORY, SINGLE_TAG, TAG_EXISTS, VALIDATE_USER)


class User:
    def __init__(self, userID, username, password, registerDate, roleName):
        self.userID = userID
        self.username = username
        self.password = password
        self.registerDate = registerDate
        self.roleName = roleName

    @property
    def is_admin(self):
        return self.roleName == 'admin'


class UserTable:
    """A class for interacting with the Users table in the database.
    """
    def __init__(self, conn):
        """Initialize a new UserTable object.

        Args:
            conn (oracledb.connection.Connection): The connection to the oracle database.
        """
        self.conn: oracledb.connection.Connection = conn

    def create(self, user: User):
        """Create a new user in the database.

        Args:
            user (User): The user to create.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(CREATE_USER, username=user.username, password=user.password, registerDate=user.registerDate)
        self.conn.commit()

    def delete(self, userID: int):
        """Delete a user from the database.

        Args:
            userID (int): The ID of the user to delete.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(DELETE_USER, userID=userID)
        self.conn.commit()

    def exists(self, userID: int) -> bool:
        """Check if a user exists in the database.

        Args:
            userID (int): The ID of the user to check.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(CHECK_USER_EXISTS, userID=userID)
            return cursor.fetchone()[0] > 0

    def get(self, userID: int):
        """Get a user from the database.

        Args:
            userID (int): The ID of the user to get.

        Raises:
            DatabaseError: If the user does not exist.

        Returns:
            User: Object for user with the given ID.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(GET_USER, userID=userID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("User not found")
            return User(*row)

    def validate(self, username: str, password: str) -> Union[int, None]:
        """
        Give a username and password, return the user's ID if the user exists. Otherwise return None.
        
        Args:
            username (str): The username to check
            password (str): The password to check
        Returns:
            str: The user's ID if the user exists, otherwise None
        """

        with self.conn.cursor() as cursor:
            cursor.execute(VALIDATE_USER, username=username, password=password)
            result = cursor.fetchone()

            if result and result[0] == 1:
                return result[1]
            elif result is None or (result and result[0] == 0):
                return None
            elif result is not None:
                raise DatabaseError(f"Unexpected result from validate_user. There should only be one row returned. Got {result[0]} instead.")

            raise DatabaseError("Unexpected result from validate_user. There should only be one row returned.")


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
    
    def pretty_print(self):
        return f"""
        Article {self.articleID}
        Title: {self.title}
        Date: {self.publishDate}
        Tags: {self.tags}

        {self.content}
        """
        
    __repr__ = __str__
    
class Comment:
    def __init__(self, commentID, articleID, userID, commentDate, content, username: str):
        self.commentID = commentID
        self.articleID = articleID
        self.userID = userID
        self.commentDate = commentDate
        self.content = content
        self.username = username

    def __str__(self):
        return f"""
        User: {self.username}
        Date: {self.commentDate}
        Content: {self.content}
        """

    __repr__ = __str__


class ArticleTable:

    sort_options = ['date', 'title', 'author']

    def __init__(self, conn):
        self.conn = conn

    def get(self, articleID):
        with self.conn.cursor() as cursor:
            cursor.execute(SINGLE_ARTICLE, articleID=articleID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Article not found")
            articleID = row[0]
            cursor.execute(ARTICLE_TAGS, articleID=articleID)
            tags = [row[0] for row in cursor.fetchall()]
            return Article(*row, tags=tags)

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
    
    def get_by_category(self, catName: str, sort_by='date') -> List[Article]:
        
        assert sort_by in self.sort_options

        articles = []

        if sort_by == 'date':
            sort_by = 'publishDate'
        elif sort_by == 'title':
            sort_by = 'title'
        elif sort_by == 'author':
            sort_by = 'author'
        
        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLES_BY_CATEGORY, catName=catName, sort_by=sort_by)
            rows = cursor.fetchall()
            for row in rows:
                articleID = row[0]
                cursor.execute(ARTICLE_TAGS, articleID=articleID)
                tags = [row[0] for row in cursor.fetchall()]
                articles.append(Article(*row, tags=tags))

        return articles
    
    def get_by_tag(self, tagID: int, sort_by='date') -> List[Article]:

        assert sort_by in self.sort_options

        articles = []

        if sort_by == 'date':
            sort_by = 'publishDate'
        elif sort_by == 'title':
            sort_by = 'title'
        elif sort_by == 'author':
            sort_by = 'author'
        
        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLES_BY_TAG, tagID=tagID, sort_by=sort_by)
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
        
    def get_comments(self, articleID: int) -> List[Comment]:
        with self.conn.cursor() as cursor:
            cursor.execute(ARTICLE_COMMENTS, articleID=articleID)
            return [Comment(*row) for row in cursor.fetchall()]

    def add_view(self, articleID: int, userID: int):
        with self.conn.cursor() as cursor:
            cursor.execute(ADD_VIEW, articleID=articleID, userID=userID)
            self.conn.commit()
            
    def add_comment(self, articleID: int, userID: int, content: str):
        with self.conn.cursor() as cursor:
            cursor.execute(HIGHEST_COMMENT_ID)
            commentID = int(cursor.fetchone()[0]) + 1

            cursor.execute(ADD_COMMENT, commentID=commentID, articleID=articleID, userID=userID, content=content)
            self.conn.commit()


class TagTable:

    def __init__(self, conn):
        self.conn = conn
        
    def exists(self, tagID: int) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(TAG_EXISTS, tagID=tagID)
            return cursor.fetchone()[0] == 1

    def get(self, tagID: int):
        with self.conn.cursor() as cursor:
            cursor.execute(SINGLE_TAG, tagID=tagID)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Tag not found")
            return Tag(*row)


class Tag:
    def __init__(self, tagID, tagName, catName):
        self.tagID = tagID
        self.tagName = tagName
        self.catName = catName

    def __str__(self):
        return f"""
        Tag {self.tagID}
        Name: {self.tagName}
        """

    __repr__ = __str__
    

class CategoryTable:

    def __init__(self, conn):
        self.conn = conn
        
    def exists(self, catName: str) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(CATEGORY_EXISTS, catName=catName)
            return cursor.fetchone()[0] == 1

    def get(self, catName: str):
        with self.conn.cursor() as cursor:
            cursor.execute(SINGLE_CATEGORY, catName=catName)
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Category not found")
            return Tag(*row)


class Category:
    def __init__(self, catName, description):
        self.catName = catName
        self.description = description

    def __str__(self):
        return f"""
        Category: {self.catName}
        Description: {self.description}
        """

    __repr__ = __str__


class NewsDB:
    def __init__(self, conn):
        self.conn: oracledb.connection.Connection = conn
        self.users = UserTable(self.conn)
        self.articles = ArticleTable(self.conn)
        self.tags = TagTable(self.conn)
        self.categories = CategoryTable(self.conn)
