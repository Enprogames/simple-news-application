import re
import datetime as dt

from oracledb import DatabaseError
from rich.table import Table
from rich.console import Console

from db import NewsDB, UserTable, User, ArticleTable, Article
from queries import ARTICLE_VIEW_REPORT


class ReportGenerator:

    def __init__(self, db: NewsDB):
        self.db: NewsDB = db
        self.console = Console()

    def validate_year(self, year):
        try:
            if re.match(r'^\d{4}$', year) is not None or int(year) < dt.datetime.now().year:
                return True
        except ValueError:
            print("Invalid year")
            return False
        
    def table_view(self, rows):
        # Create a new table
        table: Table = Table(show_header=True, header_style="bold magenta")

        header_row = rows[0]
        data = rows[1:]

        for header_column in header_row:
            table.add_column(header_column)
            
        for row in data:
            table.add_row(*row)

        self.console.print(table)

    def most_viewed_articles(self, year: str):

        with self.db.conn.cursor() as cursor:
            cursor.execute(ARTICLE_VIEW_REPORT, year=str(year).strip())
            rows = cursor.fetchall()
            if len(rows) == 0:
                raise DatabaseError("No rows were returned")
            # tabulate using rich
            self.table_view(rows)
        
    def most_popular_tags(self, year):
        # TODO: Implement this method
        pass
    
    def most_popular_categories(self, year):
        # TODO: Implement this method
        pass
    
    def most_active_users(self, year):
        # TODO: Implement this method
        pass
