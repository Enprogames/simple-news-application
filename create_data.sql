
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

-- For this project, this will likely consist soley of "user" and "admin". 
-- The "admin" role will be able to view reports for what articles/tags/users/categories are most popular/active
-- The "user" role will be able to view articles (with various sorting options), and comment on them.
create table UserRoles (
    roleName varchar(255) primary key,
    description varchar(1500)
);

create table Users (
    userID integer primary key,
    username varchar(255),
    password varchar(512),
    registerDate date,
    roleName varchar(255) references UserRoles
);

-- e.g. "How to make a database", "How to make a database in MySQL", "How to make a database in MySQL using SQL"
create table Articles (
    articleID integer primary key,
    title varchar(255),
    author varchar(255),
    publishDate date,
    content clob
);

-- Comments on articles
-- e.g. "This is a great article", "I don't agree with you", "I like your article"
create table Comments (
    commentID integer primary key,
    articleID integer references Articles,
    userID integer references Users,
    commentDate date,
    content clob
);

-- Article categories
create table Categories (
    catName varchar(255) primary key,
    description varchar(1500)
);

-- Tags for articles
-- e.g. "database", "sql", "mysql"
create table Tags (
    tagID integer primary key,
    tagName varchar(255),
	catName varchar(255) references Categories
);

-- Many to many relationship to show which tags are associated with which articles
-- e.g. article "How to make a database" might have tags "database", "sql", "mysql
create table ArticleTags (
    articleID integer references Articles,
    tagID integer references Tags
);

-- Many to many relationship to show which users have viewed which articles,
-- and at what times
create table ArticleViews (
    articleID integer references Articles,
    userID integer references Users,
    viewedAt timestamp
);

insert into UserRoles (roleName) values ('user');
insert into UserRoles (roleName) values ('admin');

insert into Users values (0, 'bob', '123',
                          to_date('2022-01-01', 'YYYY-MM-DD'), 'user');

insert into Users values (1, 'rick', '123',
                          to_date('2022-01-02', 'YYYY-MM-DD'), 'admin');

insert into Users values (2, 'fred', '123',
                          to_date('2022-01-03', 'YYYY-MM-DD'), 'user');

insert into Categories values ('technology', 'Technological breakthroughs, new products, etc');
insert into Categories values ('politics', 'Leaders, elections, foreign policy, etc');
insert into Categories values ('cooking', 'All things cooking and food: recipes, ingredients, etc');

insert into Tags values (0, 'database', 'technology');
insert into Tags values (1, 'quantum computing', 'technology');
insert into Tags values (2, 'world leaders', 'politics');
insert into Tags values (3, 'elections', 'politics');
insert into Tags values (4, 'italian food', 'cooking');
insert into Tags values (5, 'greek food', 'cooking');


insert into Articles (articleID, title, author, publishDate, content)
                    values (0, 'How to make a database', 'Bill Jameson',
                            to_date('2022-01-01', 'YYYY-MM-DD'),
                            'First, you need to setup a database instance. Then create your tables. Finally, create an application that does something useful with it.');

insert into Articles values (1, 'President of Venezuela resigns', 'John Smith',
                            to_date('2022-01-03', 'YYYY-MM-DD'),
                            'President of Venezuela resigns after 10 years in office.');

insert into Articles values (2, 'Quantum computing breakthrough', 'John Smith',
                            to_date('2022-01-05', 'YYYY-MM-DD'),
                            'Quantum computing breakthrough allows for faster calculations.');


insert into ArticleTags values (0, 0);
insert into ArticleTags values (1, 2);
insert into ArticleTags values (2, 1);

insert into Comments values (0, 0, 0, to_date('2022-01-01', 'YYYY-MM-DD'), 'This is a great article');
insert into Comments values (1, 0, 1, to_date('2022-01-01', 'YYYY-MM-DD'), 'I don''t agree with you');
insert into Comments values (2, 0, 2, to_date('2022-01-01', 'YYYY-MM-DD'), 'I like your article');
insert into Comments values (3, 1, 0, to_date('2022-01-01', 'YYYY-MM-DD'), 'This is a great article');
insert into Comments values (4, 2, 1, to_date('2022-01-01', 'YYYY-MM-DD'), 'You dont understand quantum mechanics');
insert into Comments values (5, 1, 2, to_date('2022-01-01', 'YYYY-MM-DD'), 'This could be disastrous for the country');

insert into ArticleViews values (0, 0, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (0, 0, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (0, 2, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (2, 2, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (2, 1, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (2, 2, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
insert into ArticleViews values (1, 2, to_timestamp('2022-01-01 12:00:00', 'YYYY-MM-DD HH24:MI:SS'));
