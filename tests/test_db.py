"""
Tests for main database functionality.

@author: Ethan Posner
@date: 2023-04-10
"""

# Standard library imports
import os
import sys
from unittest.mock import patch

# Third party imports
from dotenv import load_dotenv
import oracledb
from oracledb.exceptions import DatabaseError
import pytest

if 'src' not in sys.path:
    sys.path.insert(0,'src')

# Local imports
from db import User, UserTable, Article, ArticleTable, NewsDB
from db_util import create_data, drop_data


class TestInterface:
    @classmethod
    def setup_class(cls):
        # Connect to oracle database
        load_dotenv()  # load environment from .env file
        oracledb.init_oracle_client()
        db_conn = oracledb.connect(user=os.getenv('DB_USER'),
                              password=os.getenv('DB_PASS'),
                              port=os.getenv('DB_PORT'),
                              host=os.getenv('DB_HOST'),
                              service_name='XE')
        print("Successfully connected to Oracle Database")

        cls.db_interface = NewsDB(db_conn)
        drop_data(cls.db_interface.conn)
        create_data(cls.db_interface.conn, output=False)

    @classmethod
    def teardown_class(cls):
        drop_data(cls.db_interface.conn, output=False)
        cls.db_interface.conn.close()
        print("Successfully closed connection to Oracle Database")
        
    def test_initialize(self):
        """Ensure all attributes were initialized successfully.
        """
        assert self.db_interface.articles is not None
        assert self.db_interface.users is not None
        assert self.db_interface.conn is not None


class TestUser:
    @classmethod
    def setup_class(cls):
        # Connect to oracle database
        load_dotenv()  # load environment from .env file
        oracledb.init_oracle_client()
        db_conn = oracledb.connect(user=os.getenv('DB_USER'),
                              password=os.getenv('DB_PASS'),
                              port=os.getenv('DB_PORT'),
                              host=os.getenv('DB_HOST'),
                              service_name='XE')
        print("Successfully connected to Oracle Database")
            
        cls.db_interface = NewsDB(db_conn)
        drop_data(cls.db_interface.conn)
        create_data(cls.db_interface.conn, output=False)

    @classmethod
    def teardown_class(cls):
        drop_data(cls.db_interface.conn, output=False)
        cls.db_interface.conn.close()
        print("Successfully closed connection to Oracle Database")
        
    def test_user_validate(self):
        """Ensure user validation works as expected.
        """
        # Valid user
        assert self.db_interface.users.validate('bob', '123') is not None
        assert self.db_interface.users.validate('rick', '123')  is not None
        
        # Invalid user
        assert self.db_interface.users.validate('bob', 'wrong_password') is None

        # Nonexistent user
        assert self.db_interface.users.validate('nonexistent_user', 'password') is None
        
    def test_user_get(self):
        """Ensure user retrieval works as expected.
        A user object should be returned if the user exists, and None otherwise.
        """
        # Valid user
        bob_id = self.db_interface.users.validate('bob', '123')
        rick_id = self.db_interface.users.validate('rick', '123')

        bob = self.db_interface.users.get(bob_id)
        rick = self.db_interface.users.get(rick_id)
        
        assert bob is not None, "Bob should exist"
        assert rick is not None, "Rick should exist"
        
        assert bob.username == 'bob', "Bob's username should be 'bob'"
        assert rick.username == 'rick', "Rick's username should be 'rick'"
        
        assert bob.password == '123', "Bob's password should be '123'"
        assert rick.password == '123', "Rick's password should be '123'"
        
        # Invalid user
        with pytest.raises(DatabaseError):
            self.db_interface.users.get(-1)
        with pytest.raises(DatabaseError):
            self.db_interface.users.get(3)


class TestArticle:

    @classmethod
    def setup_class(cls):
        # Connect to oracle database
        load_dotenv()  # load environment from .env file
        oracledb.init_oracle_client()
        db_conn = oracledb.connect(user=os.getenv('DB_USER'),
                              password=os.getenv('DB_PASS'),
                              port=os.getenv('DB_PORT'),
                              host=os.getenv('DB_HOST'),
                              service_name='XE')
        print("Successfully connected to Oracle Database")
            
        cls.db_interface = NewsDB(db_conn)
        drop_data(cls.db_interface.conn)
        create_data(cls.db_interface.conn, output=False)

    @classmethod
    def teardown_class(cls):
        drop_data(cls.db_interface.conn, output=False)
        cls.db_interface.conn.close()
        print("Successfully closed connection to Oracle Database")

    def test_article_get(self):
        """Ensure article retrieval works as expected.
        An article object should be returned if the article exists.
        If the article does not exist, a DatabaseError should be raised.
        """
        # Valid article
        venezuela_article_id = 1
        venezuela_article = self.db_interface.articles.get(venezuela_article_id)
        
        assert venezuela_article is not None, "Article should exist"
        
        assert venezuela_article.title == "President of Venezuela resigns"
        assert str(venezuela_article.content) == "President of Venezuela resigns after 10 years in office."
        assert str(venezuela_article.author) == "John Smith"
        assert venezuela_article.publishDate.strftime("%Y-%m-%d") == "2022-01-03"
        
        assert venezuela_article.articleID == venezuela_article_id

        # Invalid article
        with pytest.raises(DatabaseError):
            self.db_interface.articles.get(-1)
        with pytest.raises(DatabaseError):
            self.db_interface.articles.get(3)

    def test_article_tags(self):
        """Ensure article tags are retrieved correctly."""

        venezuela_article_id = 1
        venezuela_article = self.db_interface.articles.get(venezuela_article_id)
        assert len(venezuela_article.tags) == 1
        assert venezuela_article.tags[0] == "world leaders"
        
        venezuela_article_tags = self.db_interface.articles.get_tags(venezuela_article_id)
        assert venezuela_article_tags == venezuela_article.tags
        
    def test_get_all(self):
        pass

    def test_get_by_category(self):
        pass
    
    def test_get_comments(self):
        pass
    
    def test_add_view(self):
        pass
    
    def test_add_view(self):
        pass
