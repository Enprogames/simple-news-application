
--  Users(userID, username, password, registerDate)
--  Articles(articleID, title, author, publishDate, content)
--  Comments(commentID, articleID, userID, commentDate, content)
--  Tags(tagID, tagName)
--  ArticleTags(articleID, tagID)
--  Categories(catID, catName)
--  ArticleCategories(catID, articleID)
--  ArticleViews(articleID, userID, viewDate)
-- 
-- where
--  - In Comments, articleID references Articles and userID references Users
--  - In ArticleTags, articleID references Articles and tagID references Tags
--  - In ArticleCategories, catID references Categories and articleID references Articles
--  - In ArticleViews, articleID references Articles and userID references Users

-- drop table Users
-- drop table Articles
-- drop table Comments
-- drop table Tags
-- drop table ArticleTags
-- drop table Categories
-- drop table ArticleCategories
-- drop table ArticleViews


-- Create user with support for sha512 hashed password
-- TODO: Add support for salted passwords
-- TODO: Add support for user email addresses
create table Users (
    userID char(36) primary key,
    username varchar(255),
    password char(512),
    registerDate date
);

-- e.g. "How to make a database", "How to make a database in MySQL", "How to make a database in MySQL using SQL"
create table Articles (
    articleID char(36) primary key,
    title varchar(255),
    author char(36),
    publishDate date,
    content text
);

-- Comments on articles
-- e.g. "This is a great article", "I don't agree with you", "I like your article"
create table Comments (
    commentID char(36) primary key,
    articleID char(36) references Articles,
    userID char(36), references Users,
    commentDate date,
    content text
);

-- Tags for articles
-- e.g. "database", "sql", "mysql"
create table Tags (
    tagID char(36) primary key,
    tagName varchar(255),
);

-- Many to many relationship to show which tags are associated with which articles
-- e.g. article "How to make a database" might have tags "database", "sql", "mysql
create table ArticleTags (
    articleID char(36) references Articles,
    tagID char(36) references Tags
);

-- Article categories
create table Categories (
    -- TODO: Should this be removed and the catName be made the primary key?
    catID char(36) primary key,
    catName varchar(255),
    -- TODO: description varchar(1500)
);

-- Many to many relationship to show which articles are in which categories
-- TODO: Add unique contraint to ensure that each article is only in each category once?
-- TODO: Should an article only be allowed to have one category?
create table ArticleCategories (
    catID char(36) references Categories,
    articleID char(36) references Articles
);


-- Many to many relationship to show which users have viewed which articles,
-- and at what times
create table ArticleViews(
    articleID char(36) references Articles,
    userID char(36) references Users,
    viewDate date
    -- TODO: viewTime timestamp
);
