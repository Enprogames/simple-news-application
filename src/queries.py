"""
Home for SQL scripts that will be used by various modules in this project.

@author: Ethan Posner
@date: 2023-04-10
"""

# Used for getting the most recent comment for when we create a new one.
# I used this instead of a trigger due to time constraints.
HIGHEST_COMMENT_ID = """SELECT MAX(commentID) FROM Comments"""

ADD_VIEW = """INSERT INTO ArticleViews (articleID, userID, viewedAt)
              values (:articleID, :userID, CURRENT_TIMESTAMP)"""
              
ADD_COMMENT = """INSERT INTO Comments (commentID, articleID, userID, commentDate, content)
                 values (:commentID, :articleID, cast(:userID as integer), SYSDATE, :content)"""


CREATE_USER = """INSERT INTO users (username, password, registerDate)
                 VALUES (:username, :password, :registerDate)"""

DELETE_USER = """DELETE FROM users WHERE userID = cast(:userID as integer)"""

CHECK_USER_EXISTS = """SELECT COUNT(*) FROM users WHERE userID = cast(:userID as integer)"""

GET_USER = """SELECT userID, username, password, registerDate, roleName
              FROM users
              WHERE userID = cast(:userID as integer)"""

VALIDATE_USER = """SELECT COUNT(*), userID
                 FROM users
                 WHERE username = :username AND password = :password
                 GROUP BY userID"""


SINGLE_ARTICLE = """SELECT articleID, title, author, publishDate, to_char(content)
                 FROM articles WHERE articleID = cast(:articleID as integer)"""

SINGLE_TAG = """SELECT tagID, tagName, catName
                FROM Tags WHERE tagID = cast(:tagID as integer)"""

TAG_EXISTS = """SELECT COUNT(*) FROM Tags WHERE tagID = cast(:tagID as integer)"""

SINGLE_CATEGORY = """SELECT catName, description FROM Categories WHERE lower(catName) = lower(:catName)"""

CATEGORY_EXISTS = """SELECT COUNT(*) FROM Categories WHERE lower(catName) = lower(:catName)"""


ARTICLE_TAGS = """SELECT T.tagName
                  FROM tags T join articleTags AT on T.tagID = AT.tagID
                            join articles A on AT.articleID = A.articleID
                  WHERE A.articleID = cast(:articleID as integer)
                  GROUP BY T.tagName"""

ARTICLE_COMMENTS = """SELECT C.commentID, C.articleID, C.userID, C.commentDate, to_char(C.content), U.username
                      FROM Comments C join Users U on C.userID = U.userID
                      WHERE C.articleID = cast(:articleID as integer)"""

ARTICLES_SORTED = """SELECT articleID, title, author, publishDate, content
                      FROM articles
                      ORDER BY :sort_by ASC"""

ARTICLES_BY_CATEGORY = """SELECT A.articleID, A.title, A.author, A.publishDate, to_char(A.content)
                          FROM articles A join ArticleTags AT on A.articleID = AT.articleID
                                          join Tags T on AT.tagID = T.tagID
                          WHERE T.catName = :catName
                          GROUP BY A.articleID, A.title, A.author, A.publishDate, to_char(A.content)
                          ORDER BY :sort_by ASC"""

ARTICLES_BY_TAG = """SELECT A.articleID, A.title, A.author, A.publishDate, to_char(A.content)
                     FROM articles A join ArticleTags AT on A.articleID = AT.articleID
                     WHERE AT.tagID = cast(:tagID as integer)
                     GROUP BY A.articleID, A.title, A.author, A.publishDate, to_char(A.content)
                     ORDER BY :sort_by ASC"""


######### ADMIN REPORTS #########

ARTICLE_VIEW_REPORT = """SELECT R."ID", R."Title", R."Views", R."Comments"
                         FROM
                         (SELECT 'ID' as "ID", 'Title' as "Title", 'Views' as "Views", 'Comments' as "Comments"
                         FROM dual
                         UNION ALL
                         SELECT to_char(A.articleID), to_char(A.title), to_char(NVL(V.viewcount, 0)), to_char(NVL(C.commentcount, 0))
                         FROM articles A
                            left join (SELECT articleID, count(*) as viewcount
                                       FROM ArticleViews
                                       WHERE extract(year from viewedAt) = :year
                                       GROUP BY articleID) V on A.articleID = V.articleID
                            left join (SELECT articleID, count(*) as commentcount
                                       FROM Comments
                                       WHERE extract(year from commentDate) = :year
                                       GROUP BY articleID) C on A.articleID = C.articleID
                         WHERE extract(year from A.publishDate) = :year) R
                         ORDER BY R."Views" DESC"""

TAG_VIEW_REPORT = """SELECT R."ID", R."TagName", R."Articles", R."Views"
                     FROM
                     (SELECT 'ID' as "ID", 'Tag Name' as "TagName", 'Articles' as "Articles", 'Views' as "Views"
                     FROM dual
                     UNION ALL
                     SELECT to_char(T.tagID), to_char(T.tagName), to_char(NVL(A.articleCount, 0)), to_char(NVL(V.viewcount, 0))
                     FROM Tags T
                        left join (SELECT tagID, count(distinct AT.articleID) as articleCount
                                    FROM ArticleTags AT join articles A on AT.articleID = A.articleID
                                    WHERE extract(year from A.publishDate) = :year
                                    GROUP BY tagID) A on T.tagID = A.tagID
                        left join (SELECT tagID, count(*) as viewcount
                                    FROM ArticleTags AT join ArticleViews AV on AT.articleID = AV.articleID
                                       join articles A on AT.articleID = A.articleID
                                    WHERE extract(year from A.publishDate) = :year
                                      and extract(year from AV.viewedAt) = :year
                                    GROUP BY tagID) V on T.tagID = V.tagID) R
                     ORDER BY R."Views" DESC"""

CATEGORY_VIEW_REPORT = """SELECT R."catName", R."description", R."articleCount", R."comCount", R."viewCount"
                          FROM
                          (SELECT 'Category' as "catName", 'Description' as "description", 'Articles' as "articleCount", 'Comments' as "comCount", 'Views' as "viewCount"
                           FROM dual
                           UNION ALL
                           SELECT distinct C.catName, C.description, to_char(NVL(AC.articleCount, 0)), to_char(NVL(CM.comCount, 0)), to_char(NVL(V.viewCount, 0))
                           FROM Categories C

                              left join (SELECT distinct T1.catName as catName, count(*) as articleCount
                                         FROM Tags T1 join ArticleTags AT1 on AT1.tagID = T1.tagID
                                                      join Articles A1 on AT1.articleID = A1.articleID
                                         WHERE extract(year from A1.publishDate) = :year
                                         GROUP BY T1.catName) AC on AC.catName = C.catName

                              left join (SELECT distinct T2.catName as catName, count(*) as comCount
                                         FROM Tags T2 join ArticleTags AT2 on AT2.tagID = T2.tagID
                                                      join Articles A2 on A2.articleID = AT2.articleID
                                                      join Comments C2 on C2.articleID = AT2.articleID
                                         WHERE extract(year from A2.publishDate) = :year
                                         and extract(year from C2.commentDate) = :year
                                         GROUP BY T2.catName) CM on CM.catName = C.catName

                              left join (SELECT distinct T3.catName as catName, count(*) as viewCount
                                         FROM Tags T3 join ArticleTags AT3 on T3.tagID = AT3.tagID
                                                      join Articles A3 on A3.articleID = AT3.articleID
                                                      join ArticleViews V3 on V3.articleID = AT3.articleID
                                         WHERE extract(year from A3.publishDate) = :year
                                         and extract(year from V3.viewedAt) = :year
                                         GROUP BY T3.catName) V on V.catName = C.catName) R
                          ORDER BY R."viewCount" DESC"""

USER_ACTIVITY_REPORT = """SELECT R."userID", R."username", R."comCount", R."viewCount", R."vea"
                          FROM
                          (SELECT 'ID' as "userID", 'Username' as "username", 'Comments' as "comCount", 'Views' as "viewCount", 'Viewed Every Article?' as "vea"
                           FROM dual
                           UNION ALL
                           SELECT to_char(U.userID), U.username, to_char(NVL(CM.comCount, 0)), to_char(NVL(V.viewCount, 0)), to_char(NVL(D.vea, 'N'))
                           FROM Users U

                              left join (SELECT userID, count(*) as comCount
                                         FROM Comments
                                         WHERE extract(year from commentDate) = :year
                                         GROUP BY userID) CM on CM.userID = U.userID

                              left join (SELECT userID, count(*) as viewCount
                                         FROM ArticleViews
                                         WHERE extract(year from viewedAt) = :year
                                         GROUP BY userID) V on V.userID = U.userID

                              left join (SELECT U.userID as userID, 'Y' as vea
                                         FROM Users U
                                         WHERE not exists (SELECT *
                                                           FROM Articles A
                                                           WHERE not exists (SELECT *
                                                                             FROM ArticleViews AV
                                                                             WHERE AV.userID = U.userID
                                                                               and AV.articleID = A.articleID))) D
                                 on D.userID = U.userID) R
                          ORDER BY R."viewCount" DESC"""


######### USER REPORTS #########

# TODO: The article count returns the total number of articles, but should only be the number of articles for a given tag.
TAG_REPORT = """SELECT R."ID", R."TagName", R."Category", R."ArticleCount"
                FROM
                (SELECT 'ID' as "ID", 'Tag Name' as "TagName", 'Category' as "Category", 'Article Count' as "ArticleCount"
                FROM dual
                UNION ALL
                SELECT to_char(T.tagID), to_char(T.tagName), to_char(T.catName), to_char(NVL(A.articleCount, 0))
                FROM Tags T
                  left join (SELECT tagID, count(*) as articleCount
                             FROM ArticleTags
                             GROUP BY tagID) A on T.tagID = A.tagID) R
                ORDER BY R."ArticleCount" DESC"""

# TODO: This says there are 8 articles in each category, and only 3 articles exist, so something is wrong.
CATEGORY_REPORT = """SELECT R."CategoryName", R."Description", R."ArticleCount"
                     FROM
                     (SELECT 'Category Name' as "CategoryName", 'Description' as "Description", 'Article Count' as "ArticleCount"
                      FROM dual
                      UNION ALL
                      SELECT to_char(C.catName), to_char(C.description), to_char(NVL(A.articleCount, 0))
                      FROM Categories C
                        left join (SELECT T.catName, count(*) as articleCount
                                   FROM Tags T join ArticleTags AT on T.tagID = AT.tagID
                                   GROUP BY T.catName) A on C.catName = A.catName) R
                     ORDER BY R."ArticleCount" DESC"""
