# Tasks that Must be Completed for this Project

## Main Functionality
- [x] User can login
- [x] User can logout
- [ ] User can view articles
- [ ] User can view a specific article
- [ ] User can see article comments
- [ ] User can comment on articles
- [ ] User can sort articles by date
- [ ] User can view articles in specific categories
- [ ] User can view articles with specific tags

- [ ] Admin can login and be in a separate state
    - I'm not sure how to do this yet. I want admins to be able to do everything that users can do, and also be able to create reports of article popularity, but I'm not sure how to facilitate these shared functionalities.
    - Idea: Somehow the application could have two separate but interrelated sets of states that are accessed by the same login credentials. The user state would be the same as the admin state, but the admin state would have additional functionality. Then, when the application would login, it would check the user's role and call a login() function. And this login() function would know how to handle whether to put them in a user or admin state.
- [ ] 

## Quality of Life
- [ ] Put SQL queries in separate file(s)
- [ ] Pipe large output into less. Could possibly use [pager(https://pypi.org/project/pager/)]?

## Possible Future Features
- [ ] User registration
- [ ] Search for articles 
