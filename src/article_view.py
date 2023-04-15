"""
Helper module for presenting articles to the user in a nice format.

@author: Ethan Posner
@date: 2023-04-10
"""

from rich.console import Console

from db import NewsDB


class ArticleViewer:

    def __init__(self, db: NewsDB):
        self.db = db
        self.console = Console()

    def print_article(self, article_id):
        article = self.db.articles.get(article_id)
        with self.console.pager():
            self.console.print(article.pretty_print())

    def print_articles(self, sort_by='date', catName=None, tagID=None):
        assert sort_by in self.db.articles.sort_options
        info = ""
        if catName is not None and tagID is not None:
            raise ValueError("Feature not yet implemented")
        elif catName is not None:
            articles = self.db.articles.get_by_category(catName)
            info = f" in category '{catName}'"
        elif tagID is not None:
            tag = self.db.tags.get(tagID)
            articles = self.db.articles.get_by_tag(tagID)
            info = f" with tag '{tag.tagName}'"
        else:
            articles = self.db.articles.get_all(sort_by)

        if len(articles) > 0:
            with self.console.pager():
                self.console.print(f"Got {len(articles)} Article(s){info} (sorted By {sort_by}):")
                for article in articles:
                    self.console.print(article)
        else:
            self.console.print(f"No Articles Found{info}")

    def print_comments(self, article_id):
        comments = self.db.articles.get_comments(article_id)
        with self.console.pager():
            self.console.print(f"Comments for article {article_id}:")
            for comment in comments:
                self.console.print(comment)
