"""
Tests for main application driver.

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


sys.path.insert(0,'src')

# Local imports
from db import User, UserTable, NewsDB
from main import AppStates, ApplicationCLI

@pytest.mark.skip("Skipping until I can figure out how to mock input()")
class TestMain:
    
    @classmethod
    def setup_class(cls):
        # Connect to oracle database
        load_dotenv()  # load environment from .env file
        oracledb.init_oracle_client()
        with oracledb.connect(user=os.getenv('DB_USER'),
                            password=os.getenv('DB_PASS'),
                            port=os.getenv('DB_PORT'),
                            host=os.getenv('DB_HOST'),
                            service_name='XE') as db_conn:
            print("Successfully connected to Oracle Database")
            
            cls.db_interface = NewsDB(db_conn)

    def test_init(self):
        with patch("builtins.input", return_value="") as mock_input:
            main = ApplicationCLI()
            assert main.current_state == AppStates.LOGGED_OUT
