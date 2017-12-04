# Introduction
This project provides a simple app for 'Build an Item Catalog Application' project in Udacity.
This project meets up the main properties below.

* CRUD - Can create, read, update, delete items from and to database.
* Authentication & Authorization - Only login user can add, update, delete items. (By google accounts)
* SignIn & SignOut - You can do this anytime.
* UI - Basic UI parts by bootstrap v4.0

# Files and Folder

* `static` - Folder for Single css file for template html files.
* `templates` - Including template htmls with bootstrap and jinja. 
* `category_crud.py` - Main backend python file working with CRUD and google authentication & authorization.
* `database_setup.py` - database structures written in python, sqlalchemy.
* `dummyItems.py` - Makes dummyData to display at first.
* `client_secrets.json` - google client secret json file.

# Environment

* All python files are written in `Python3`
* Tested in `window 10`, `git bash`, `vagrant(ubuntu)`, `Chrome` environment
* Requires `postgreSQL`

# How to run this program

* First, run `git bash` in window.
* Go to `vagrant` folder where you install it in `git bash`.
* In `vagrant` folder, put all the files and folders.
* Run `vagrant` by `vagrant up` `vagrant ssh` and `cd vagrant` to share the folder.
* Make dummy database setup by putting `python3 dummyItems.py` in `git bash` terminal.
* Run server by `python3 category_crud.py`.
* You can see the `Catalog App` in the web browser located at `localhost:8000`

