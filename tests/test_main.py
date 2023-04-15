"""
Tests for main application driver.

@author: Ethan Posner
@date: 2023-04-10
"""

# Standard library imports
from io import StringIO
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
from db import NewsDB
from db_util import create_data, drop_data
import main
from main import AppStates, ApplicationCLI

# @pytest.mark.skip("Skipping until I can figure out how to mock input()")
class TestMain:
    
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

    def test_init(self, monkeypatch):

        with monkeypatch.context() as m:
            m.setattr('builtins.input', lambda prompt: 'q')
            app = ApplicationCLI(self.db_interface)
            assert app.current_user is None
            assert app.current_state == AppStates.LOGGED_OUT
    
    def test_login(self, monkeypatch):
        # Define a generator function that yields a sequence of values
        input_vals = iter(['l', 'bob', '123', 'q'])

        with monkeypatch.context() as m:
            m.setattr('main.get_line', lambda prompt, *a, **kw: next(input_vals))
            m.setattr('builtins.input', lambda prompt: '')
            app = ApplicationCLI(self.db_interface)
            assert app.current_user is None
            assert app.current_state == AppStates.LOGGED_OUT
            app.prompt_loop()
