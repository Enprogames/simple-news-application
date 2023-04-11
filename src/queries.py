"""
Home for SQL scripts that will be used by various modules in this project.

@author: Ethan Posner
@date: 2023-04-10
"""


HIGHEST_COMMENT_ID = """SELECT MAX(commentID) FROM Comments"""

ADD_VIEW = """INSERT INTO ArticleViews (articleID, viewDate, viewedAt)
              values (:articleID, :viewDate, CURRENT_TIMESTAMP)"""
              
ADD_COMMENT = """INSERT INTO Comments (commentID, articleID, userID, commentDate, content)
                 values (:commentID, :articleID, :userID, SYSDATE, :content)"""


VALIDATE_USER = """SELECT COUNT(*), userID
                 FROM users
                 WHERE username = :username AND password = :password
                 GROUP BY userID"""


SINGLE_ARTICLE = """SELECT articleID, title, author, publishDate, content
                 FROM articles WHERE articleID = :articleID"""


ARTICLE_TAGS = """SELECT T.tagName
               FROM tags T join articleTags AT on T.tagID = AT.tagID
                         join articles A on AT.articleID = A.articleID
               WHERE A.articleID = :articleID"""

ARTICLE_COMMENTS = """SELECT C.commentID, C.articleID, C.userID, C.commentDate, C.content, U.username
                      FROM Comments C join Users U on C.userID = U.userID
                      WHERE C.articleID = :articleID"""

ARTICLES_SORTED = """SELECT articleID, title, author, publishDate, content
                      FROM articles
                      ORDER BY :sort_by ASC"""


ARTICLES_BY_CATEGORY = """SELECT articleID, title, author, publishDate, content
                          FROM articles A join ArticleTags AT on A.articleID = AT.articleID
                                          join Tags T on AT.tagID = T.tagID
                          WHERE T.catName = :catName"""

# TODO: 
ARTICLES_BY_TAG = """SELECT articleID, title, author, publishDate, content
                     FROM articles A join ArticleTags AT on A.articleID = AT.articleID"""


ARTICLE_VIEW_REPORT = """SELECT 'ID', 'Title', 'Views', 'Comments'
                         FROM dual
                         UNION ALL
                         SELECT to_char(A.articleID), to_char(A.title), to_char(NVL(V.viewcount, 0)), to_char(NVL(C.commentcount, 0))
                         FROM articles A
                            left join (SELECT articleID, count(*) as viewcount
                                       FROM ArticleViews
                                       GROUP BY articleID) V on A.articleID = V.articleID
                            left join (SELECT articleID, count(*) as commentcount
                                       FROM Comments
                                       GROUP BY articleID) C on A.articleID = C.articleID
                         WHERE extract(year from A.publishDate) = :year"""

# TODO: 
TAG_VIEW_REPORT = """
                  """

# TODO: 
CATEGORY_VIEW_REPORT = """
                       """

# TODO: 
USER_ACTIVITY_REPORT = """
                       """
