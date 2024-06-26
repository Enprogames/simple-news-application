"""
Driver for all application functionality.

@author: Ethan Posner
@date: 2023-04-10
"""

# Standard library imports
import getpass
import os
from pathlib import Path
from datetime import datetime
import argparse
from enum import Enum, auto
from typing import Union

# Third party imports
from dotenv import load_dotenv
import oracledb
from oracledb.exceptions import DatabaseError

# Local imports
from db import User, UserTable, NewsDB
from article_view import ArticleViewer
from generate_report import ReportGenerator


def empty_prompt(prompt: str) -> None:
    """Prints prompt and waits for user to press enter

    Args:
        prompt (str): An important message for the user to read.
    """
    input(f"{prompt} (Press enter to continue)")


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


class AppStates(Enum):
    LOGGED_OUT = auto()
    ARTICLE_LIST = auto()
    ADMIN_MENU = auto()
    ADMIN_YEAR_PROMPT = auto()


class ApplicationCLI:

    def __init__(self, db_interface: NewsDB):

        self.db_interface = db_interface
        self.article_viewer = ArticleViewer(self.db_interface)
        self.report_generator = ReportGenerator(self.db_interface)

        # Users will start as being logged out
        self.current_state = AppStates.LOGGED_OUT

        # the currently logged in user
        self.current_user = None
        self.running = True
        
        try:
            self.db_interface.verify()
        except DatabaseError as e:
            print(f"*****Database error: {e}")
            print("*****The database was not properly initialized. Ensure that you ran `make initdb` or the `create_data.txt` script before running.")
            print("If you just ran the unit tests, the database will have been deleted.")
            print("*****Quitting...")
            self.running = False

    def print_help(self):
        global_help = "h (list commands) q (quit)"

        admin_help = """
        LOGGED IN AS ADMIN. AVAILABLE COMMANDS:

        r1 (Generate report of most viewed articles)
        r2 (Generate report of most popular article tags)
        r3 (Generate report of most popular article categories)
        r4 (Generate report of most active users)
        """

        user_menu = """
        d (list articles by date)
        c (list articles in category)
        t (list articles with tag)
        g (list all tags)
        a (list all categories)
        v (view article)
        x (comment on article)
        z (view comments on article)
        l (logout)
        """

        if self.current_state == AppStates.LOGGED_OUT:
            print(f"l (login)\n{global_help}\n")
        elif self.current_user and self.current_user.is_admin and self.current_state == AppStates.ADMIN_MENU:
            print(f"{admin_help} l (logout)\n{global_help}\n")
        elif self.current_state == AppStates.ARTICLE_LIST:
            print(f"{user_menu}\n{global_help}\n")
        else:
            print(global_help)

    def login_prompt(self, retries=3) -> Union[int, None]:
        try:
            while retries > 0:
                username = get_line("Enter username")
                password = get_line("Enter password", hidden=True)

                if username and password:
                    user_id = self.db_interface.users.validate(username, password)
                    if user_id is not None:
                        return int(user_id)
                    else:
                        print("Invalid username or password")
                        retries -= 1
        except KeyboardInterrupt:
            print("Got keyboard interrupt. Returning to main menu.")
        print("Too many retries.")
        return None

    def process_command(self, arg: str):

        ### Commands that can be used at any time ###
        if arg == 'h':
            self.print_help()
            return
        elif arg == 'q':  # the user wants to quit
            print("You have decided to quit. Quitting...")
            self.running = False
            return
        elif arg == 'l':
            # the user wants to login
            if self.current_state == AppStates.LOGGED_OUT:
                user_id = self.login_prompt()
                if user_id is not None:  # give the login prompt and login if it was successful
                    ### THE USER IS LOGGED IN HERE ###
                    self.current_user = self.db_interface.users.get(user_id)
                    empty_prompt(f"Successfully logged in as {self.current_user.username}")
                    if self.current_user.is_admin:
                        self.current_state = AppStates.ADMIN_MENU
                    else:
                        self.current_state = AppStates.ARTICLE_LIST
                return

            # User wants to logout
            elif self.current_state == AppStates.ADMIN_MENU or self.current_state == AppStates.ARTICLE_LIST:
                self.current_user = None
                self.current_state = AppStates.LOGGED_OUT
                print("Successfully logged out")
                return

        elif self.current_state == AppStates.ADMIN_MENU:
            if arg == 'r1':
                year = get_line("Enter year: ")
                if year and year.isnumeric():
                    self.report_generator.most_viewed_articles(year)
                else:
                    empty_prompt("year invalid")
                return
            elif arg == 'r2':
                year = get_line("Enter year: ")
                if year and year.isnumeric():
                    self.report_generator.most_popular_tags(year)
                else:
                    empty_prompt("year invalid")
                return
            elif arg == 'r3':
                year = get_line("Enter year: ")
                if year and year.isnumeric():
                    self.report_generator.most_popular_categories(year)
                else:
                    empty_prompt("year invalid")
                return
            elif arg == 'r4':
                year = get_line("Enter year: ")
                if year and year.isnumeric():
                    self.report_generator.most_active_users(year)
                else:
                    empty_prompt("year invalid")
                return

        elif self.current_state == AppStates.ARTICLE_LIST:
            if arg == 'd':  # list articles by date
                self.article_viewer.print_articles(sort_by='date')
                return
            elif arg == 'c':  # list articles in a given category
                catName = get_line("Enter name of category: ")
                if catName and self.db_interface.categories.exists(catName):
                    self.article_viewer.print_articles(catName=catName)
                else:
                    empty_prompt(f"category '{catName}' does not exist")
                return
            elif arg == 't':  # list articles with a given tag
                tagID = get_line("Enter ID of tag: ")
                if tagID and tagID.isdigit() and self.db_interface.tags.exists(tagID):
                    self.article_viewer.print_articles(tagID=tagID)
                elif not tagID or not tagID.isdigit():
                    empty_prompt("Invalid tag ID")
                else:
                    empty_prompt(f"Tag with ID '{tagID}' does not exist")
                return
            elif arg == 'g':  # list all tags
                self.report_generator.tag_details()
                return
            elif arg == 'a':  # list all categories
                self.report_generator.category_details()
                return
            elif arg == 'v':  # view an article
                articleID = get_line("Enter ID of article to view: ")
                try:
                    if articleID is not None and articleID.isnumeric():
                        articleID = int(articleID)
                        self.article_viewer.print_article(articleID)
                        self.db_interface.articles.add_view(articleID, self.current_user.userID)
                    else:
                        empty_prompt(f"Invalid article ID: '{articleID}'")
                except DatabaseError as e:
                    empty_prompt(f"Error viewing article: {str(e)}")
                return
            elif arg == 'x':  # comment on an article
                articleID = get_line("Enter ID of article to comment on: ")
                content = get_line("Enter comment: ")
                try:
                    if articleID and content and not articleID.isspace() and not content.isspace():
                        self.db_interface.articles.add_comment(articleID, self.current_user.userID, content)
                        empty_prompt("Comment successfully added")
                    else:
                        empty_prompt("Invalid input")
                except ValueError as e:
                    empty_prompt("invalid article ID")
                except DatabaseError as e:
                    empty_prompt("Error adding comment. Article may not exist.")
                return
            elif arg == 'z':  # view comments on an article
                articleID = get_line("Enter ID of article to view comments on: ")
                try:
                    int(articleID)
                    if not articleID.isspace():
                        self.article_viewer.print_comments(articleID)
                    else:
                        empty_prompt("Invalid input")
                except ValueError as e:
                    empty_prompt("Enter an integer value for the article ID.")
                except DatabaseError as e:
                    empty_prompt("Article may not exist.")
                return

        print("Invalid command")

    def prompt_loop(self):
        try:
            while self.running:
                if self.current_state == AppStates.LOGGED_OUT:
                    prompt = "Enter command l (login) | h (list commands) | q (quit)"
                elif self.current_state == AppStates.ARTICLE_LIST:
                    prompt = "Enter command: h (list commands) q (quit)"
                elif self.current_state == AppStates.ADMIN_MENU:
                    prompt = "Enter command: h (list commands) q (quit)"
                else:
                    raise ValueError("Invalid application state")

                command = get_line(prompt)
                if command:
                    print(f"Got command: {command}")
                    self.process_command(command.strip().lower())
                else:  # get_line returns None if input was invalid
                    print("Command cannot be empty")

        except KeyboardInterrupt:
            print("Got keyboard interrupt. Quitting...")
            self.running = False


if __name__ == '__main__':
    # Connect to oracle database
    load_dotenv()  # load environment from .env file
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    assert os.getenv('DB_USER'), "DB_USER cannot be empty. Ensure it is set in the .env file"
    assert os.getenv('DB_PASS'), "DB_PASS cannot be empty. Ensure it is set in the .env file"
    assert os.getenv('DB_PORT'), "DB_PORT cannot be empty. Ensure it is set in the .env file"
    assert os.getenv('DB_HOST'), "DB_HOST cannot be empty. Ensure it is set in the .env file"
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
