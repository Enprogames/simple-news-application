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

# Third party imports
from dotenv import load_dotenv
import oracledb
from oracledb.exceptions import DatabaseError

# Local imports
from db import User, UserTable, NewsDB
from article_view import ArticleViewer
from generate_report import ReportGenerator


def quit_program(msg: str = "Bye", code: int = 0):
    print(msg)
    exit(code)


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
        v (view article)
        x (comment on article)
        z (view comments on article)
        """

        if self.current_state == AppStates.LOGGED_OUT:
            print(f"l (login)\n{global_help}\n")
        elif self.current_user and self.current_user.is_admin and self.current_state == AppStates.ADMIN_MENU:
            print(f"{admin_help} l (logout)\n{global_help}\n")
        elif self.current_state == AppStates.ARTICLE_LIST:
            print(f"{user_menu} l (logout)\n{global_help}\n")
        elif self.current_state == AppStates.VIEW_ARTICLE:
            pass  # TODO: add help for viewing an article
        else:
            print(global_help)

    def login_prompt(self, retries=3) -> str:
        try:
            while retries > 0:
                username = get_line("Enter username")
                password = get_line("Enter password", hidden=True)

                if username and password:
                    user_id = str(self.db_interface.users.validate(username, password))
                    if not user_id.isspace():
                        return user_id
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
            quit_program("You have decided to quit. Quitting...")
            return
        elif arg == 'l':
            # the user wants to login
            if self.current_state == AppStates.LOGGED_OUT:
                user_id = self.login_prompt()
                if user_id:  # give the login prompt and login if it was successful
                    ### THE USER IS LOGGED IN HERE ###
                    self.current_user = self.db_interface.users.get(user_id)
                    empty_prompt(f"Successfully logged in as {self.current_user.username}")
                    if self.current_user.is_admin:
                        self.current_state = AppStates.ADMIN_MENU
                    else:
                        self.current_state = AppStates.ARTICLE_LIST
                return

            # User wants to logout
            elif self.current_state == AppStates.ADMIN_MENU or self.current_state == AppStates.VIEW_ARTICLE or self.current_state == AppStates.ARTICLE_LIST:
                self.current_user = None
                self.current_state = AppStates.LOGGED_OUT
                print("Successfully logged out")
                return

        elif self.current_state == AppStates.ADMIN_MENU:
            if arg == 'r1':
                year = get_line("Enter year: ")
                self.report_generator.most_viewed_articles(year)
                return
            elif arg == 'r2':
                year = get_line("Enter year: ")
                self.report_generator.most_popular_tags(year)
                return
            elif arg == 'r3':
                year = get_line("Enter year: ")
                self.report_generator.most_popular_categories(year)
                return
            elif arg == 'r4':
                year = get_line("Enter year: ")
                self.report_generator.most_active_users(year)
                return

        elif self.current_state == AppStates.ARTICLE_LIST:
            if arg == 'd':  # list articles by date
                self.article_viewer.print_articles(sort_by='date')
                return
            elif arg == 'c':  # list articles in a given category
                # TODO: 
                return
            elif arg == 't':  # list articles with a given tag
                # TODO: 
                return
            elif arg == 'v':  # view an article
                articleID = get_line("Enter ID of article to view: ")
                try:
                    int(articleID)
                    if not articleID.isspace():
                        self.article_viewer.print_article(articleID)
                except ValueError:
                    empty_prompt("Invalid article ID")
                except DatabaseError as e:
                    empty_prompt("Error viewing article. Article may not exist.")
                return
            elif arg == 'x':  # comment on an article
                articleID = get_line("Enter ID of article to comment on: ")
                content = get_line("Enter comment: ")
                try:
                    if not articleID.isspace() and not content.isspace():
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
            while True:
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
