# CSCI 370 - News Database Project

# Introduction

The goal of this project will be to create an application and a supporting database to display news articles. It will include the ability for users to login and view articles. Users will interact with the application through a command-line interface. 

They will be able to view recent articles, view articles by category, and view them based on tags. Each article should show what category and tags it has.

Users should also have the ability to comment on posts, and other users should be able to see those comments.

Users of this application include anyone interested in keeping up with new knowledge, or in learning new things in general. 

# Data Description

To support all application functionality, the database will be require storing the following data:

- Users login information
- Articles: Title, content, tags, categories, number of views, and who viewed it,
- Comments: Who commented, what article the comment was made on, and what the comment contains.
- Article tags: For example, articles talking about technological breakthroughs in nuclear fusion energy production might all be tagged “Nuclear Fusion Energy”.
- Article Categories: For example, articles about political events might all be put under the category of “Politics”.

# Application Requirements

Below are the major functionalities that will be supported by this application.

### 1. User Login

Upon entering the application, users will be prompted to enter a username and password. They will be unable to access the application without logging in.

### 2. View articles by date

Upon logging into the application, users should be shown a list of articles. These articles should be displayed in order based on their publication dates, with newer ones being shown first. Articles in this list should display their title, author, publication date, category, tags, and the first few sentences of the actual article.

Users should also be able to select a specific article to view, and once selected, should be shown the entire article’s contents. If the article is large, they should be able to scroll down to see the rest of it.

### 3. View articles in specific categories

After logging in and having been shown the initial display of articles, users should be able to select a specific category of articles to view. Upon selecting a category, they should be shown a list of articles in that category. These should be ordered by their publication date with newer articles being shown first.

### 4. View articles with specific tags

Similarly to categories, users should be able to view all articles that have a specific tag. 

### 5. Comment on articles and see other user comments

After selecting an article, users should be able to make comments on them. They should also be able to view other user comments at the bottom of the article. 

### Stretch Goals

### 1. User Registration

With the current development plan, users will require the database administrator to setup their accounts. If there is time, it would be more convenient for users to be able to create accounts themselves.

This might also include other complicated components, such as allowing users to reset their passwords with a recovery email. An initial implementation of this feature would be more simple, however.

### 2. Searching for Articles

An interesting and useful feature would be to allow users to search for specific articles by typing the name, or keywords, into a prompt. This could also include the ability to filter the search results further. For example, to search specifically for articles under the category of “Politics” with the tag “Canada” and make a search for “election results”.

## Usage Instructions
I use docker and docker-compose to run containers, then I do all of my work within these containers. I usually have two terminal windows running where one is for my Python scripts, which setup the database and insert data, and the other is for the actual oracle database, where I execute SQL queries.

To run these containers, do the following:
1. Open a terminal window and start the containers: `docker-compose up --build -d`
2. In this window, you can run the Python `insert_table_data.py` script with docker-compose exec: `docker-compose exec python_app_370 python3 insert_table_data.py`
    - Note: This is often what fails to work, and often requires troubleshooting.
3. Open a new terminal window and shell into the oracle database container:
    `docker-compose exec oracleex_db_370 bash`
4. Execute SQL queries using SQLPlus:
    `rlwrap sqlplus system/oracle@XE`
