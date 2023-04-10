ARTICLE_TAGS = """SELECT T.tagName
               FROM tags T join articleTags AT on T.tagID = AT.tagID
                         join articles A on AT.articleID = A.articleID
               WHERE A.articleID = :articleID"""
               

ARTICLES_SORTED = """SELECT articleID, title, author, publishDate, content
                      FROM articles
                      ORDER BY :sort_by ASC"""


ARTICLES_BY_CATEGORY = """SELECT articleID, title, author, publishDate, content
                          FROM articles A join ArticleTags AT on A.articleID = AT.articleID
                                          join Tags T on AT.tagID = T.tagID
                          WHERE T.catName = :catName"""


ARTICLES_BY_TAG = """SELECT articleID, title, author, publishDate, content
                     FROM articles A join ArticleTags AT on A.articleID = AT.articleID"""


ARTICLE_VIEW_REPORT = """SELECT 'ID', 'Title', 'Views'
                         FROM dual
                         UNION ALL
                         SELECT to_char(A.articleID), to_char(A.title), to_char(NVL(V.viewcount, 0))
                         FROM articles A
                            left join (SELECT articleID, count(*) as viewcount
                                       FROM ArticleViews
                                       GROUP BY articleID) V on A.articleID = V.articleID
                         WHERE extract(year from A.publishDate) = :year"""
