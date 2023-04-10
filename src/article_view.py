from rich.console import Console

from db import NewsDB, UserTable, User, ArticleTable, Article


class ArticleViewer:

    def __init__(self, db: NewsDB):
        self.db = db
        self.console = Console()

    def view_article(self, article_id):
        article = self.db.articles.get(article_id)
        with self.console.pager():
            self.console.print(article.pretty_print())

    def print_articles(self, sort_by='date'):
        assert sort_by in self.db.articles.sort_options
        articles = self.db.articles.get_all(sort_by)

        with self.console.pager():
            for article in articles:
                self.console.print(article)