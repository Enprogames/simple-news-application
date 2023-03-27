
-- UserRoles(roleName, description)
-- Users(userID, username, password, registerDate)
-- Articles(articleID, title, author, publishDate, content)
-- Comments(commentID, articleID, userID, commentDate, content)
-- Categories(catName, description)
-- Tags(tagID, tagName, catName)
-- ArticleTags(articleID, tagID)
-- ArticleViews(articleID, userID, viewedAt)
-- 
-- where
-- In Users, roleName references UserRoles
-- In Comments, articleID references Articles and userID references Users
-- In Tags, catName references Categories
-- In ArticleTags, articleID references Articles and tagID references Tags
-- In ArticleViews, articleID references Articles and userID references Users

-- drop table ArticleViews
-- drop table ArticleTags
-- drop table Tags
-- drop table Categories
-- drop table Comments
-- drop table Articles
-- drop table Users
-- drop table UserRoles

-- For this project, this will likely consist soley of "user" and "admin". 
-- The "admin" role will be able to view reports for what articles/tags/users/categories are most popular/active
-- The "user" role will be able to view articles (with various sorting options), and comment on them.
create table UserRoles (
    roleName varchar(255) primary key,
    description varchar(1500)
)

-- Create user with support for sha512 hashed password
-- TODO: Add support for user email addresses?
create table Users (
    userID char(36) primary key,
    username varchar(255),
    password RAW(512),
    registerDate date,
    roleName varchar(255) references UserRoles
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

-- Article categories
create table Categories (
    catName varchar(255) primary key,
    description varchar(1500)
);

-- Tags for articles
-- e.g. "database", "sql", "mysql"
create table Tags (
    tagID char(36) primary key,
    tagName varchar(255),
		catName varchar(255) references Categories
);

-- Many to many relationship to show which tags are associated with which articles
-- e.g. article "How to make a database" might have tags "database", "sql", "mysql
create table ArticleTags (
    articleID char(36) references Articles,
    tagID char(36) references Tags
);

-- Many to many relationship to show which users have viewed which articles,
-- and at what times
create table ArticleViews(
    articleID char(36) references Articles,
    userID char(36) references Users,
    viewedAt timestamp
);
