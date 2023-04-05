
# Standard library imports
import getpass
import os
from pathlib import Path
from datetime import datetime
import argparse
from enum import Enum

# Third party imports
from dotenv import load_dotenv
import oracledb
from oracledb.exceptions import DatabaseError

# Local imports
from db import User, UserTable, NewsDB
from article_view import ArticleViewer


def quit_program(msg: str = "Bye", code: int = 0):
    print(msg)
    exit(code)


def get_line(prompt: str, hidden=False) -> str:
    """Ask the user for input and return it

    Args:
        prompt (str): The prompt to display to the user
        error_msg (str): The error message to display if the user enters nothing
        hidden (bool, optional): Whether or not to hide the user's input. Useful for passwords. Defaults to False.

    Returns:
        str: Plain text input from the user
    """
    prompt = f"{prompt}: "
    if hidden:
        user_input = getpass.getpass(prompt)
    else:
        user_input = input(prompt)

    if user_input and not user_input.isspace():
        return user_input
    else:
        return None


class ApplicationStates(Enum):
    LOGGED_OUT = 1
    ARTICLE_LIST = 2
    VIEW_ARTICLE = 4


class ApplicationCLI:
    
    def __init__(self, db_interface: NewsDB):
        
        self.db_interface = db_interface
        self.article_viewer = ArticleViewer(self.db_interface)
        
        # Users will start as being logged out
        self.current_state = ApplicationStates.LOGGED_OUT
    
    def print_help(self):
        if self.current_state == ApplicationStates.ARTICLE_LIST:
            print("d (list articles by date) c (list articles in category) t (list articles by tag)\n")

    def login_prompt(self, retries=3) -> bool:
        try:
            while retries > 0:
                username = get_line("Enter username")
                password = get_line("Enter password", hidden=True)

                if username and password:
                    if self.db_interface.users.validate(username, password):
                        print(f"Successfully logged in as {username}")
                        return True
                    else:
                        print("Invalid username or password")
                        retries -= 1
        except KeyboardInterrupt:
            print("Got keyboard interrupt. Returning to main menu.")
        print("Too many retries.")
        return False

    def process_command(self, arg: str):
        if self.current_state == ApplicationStates.LOGGED_OUT:
            if arg == 'l':  # the user wants to login
                if self.login_prompt():  # give the login prompt and login if it was successful
                    self.current_state = ApplicationStates.ARTICLE_LIST
        elif self.current_state == ApplicationStates.VIEW_ARTICLE:
            if arg == 'd':  # list articles by date
                pass
            elif arg == 'c':  # list articles in a given category
                pass
            elif arg == 't':  # list articles with a given tag
                pass
        if arg == 'h':
            self.print_help()
        elif arg == 'q':  # the user wants to quit
            quit_program("You have decided to quit. Quitting...")
        else:
            print("Invalid command")

    def prompt_loop(self):
        try:
            while True:
                if self.current_state == ApplicationStates.LOGGED_OUT:
                    prompt = "Enter command l (login) | q (quit)"
                elif self.current_state == ApplicationStates.ARTICLE_LIST:
                    prompt = "Enter command: h (list commands) q (quit)"
                elif self.current_state == ApplicationStates.VIEW_ARTICLE:
                    pass
                else:
                    raise ValueError("Invalid application state")

                command = get_line(prompt)
                if command:
                    print(f"Got command: {command}")
                    self.process_command(command)
                else:  # get_line returns None if input was invalid
                    print("Command cannot be empty")

        except KeyboardInterrupt:
            quit_program("Got keyboard interrupt. Quitting...")


# Connect to oracle database
load_dotenv()  # load environment from .env file
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
oracledb.init_oracle_client()
with oracledb.connect(user=os.getenv('DB_USER'),
                      password=os.getenv('DB_PASS'),
                      port=os.getenv('DB_PORT'),
                      host=os.getenv('DB_HOST'),
                      service_name='XE') as db_conn:
    print("Successfully connected to Oracle Database")
    
    db_interface = NewsDB(db_conn)
    app = ApplicationCLI(db_interface)

    app.prompt_loop()
