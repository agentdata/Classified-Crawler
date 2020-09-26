## About

The function of this web app is to crawl classified web pages, at the moment it just crawls craigslist or offerup page with the user's search query and grabs relevant info about the ads on the search page then crawls each of the classified links it get's and parses all the classified info and stores it in the database. There is a second part which allows the user to query the items that have already been crawled and stored in the database.

It's a little bit quicker running locally but over the cloud on my mobile phone seems to work pretty decent.

#### Languages and framework
The main web app was written in python 3.7 using with django2.2.7, with javascript handling some UI and the ajax post and get requests.

The crawler is using the scrapy framework which runs as separate service from the web app, the django views submit the job directly through the running daemon on the server.

## Instructions
### Environment setup
I used debian linux as a base for these instructions.

- First clone this project then enter its root directory
- Install python 3.7 if you don't have it already
- create python 3.7 virtual environment 
    - **python3.7 -m venv .venv3-7**

- add packages
    - enter virtual environment
        - **source .venv3-7/bin/activate**
    - **pip install wheel**
    - **pip install -r requirements.txt** (it will grab the packages specified in this list)
- setup db
    - you will need to fill in the database settings in the finalproject/settings.py file under DATABASES
    - you will need to run both **python manage.py makemigrations** and  **python manage.py migrate -run-syncdb** to create the necessary tables
    - in order to run tests you will need to change the selected DB to use sqlite3 or use an account that can create and delete databases on the MYSQL server. **See below under tests**

### Running the crawler

there are 2 parts to running this crawler, django and scrapy

- Start django server
    - enter virtual environment if you are not still in it
    - **python manage.py runserver IP:PORT** from the root directory where manage.py exists
        - substitute IP and PORT for the address and port you want to use your browser to connect with
        - if running this on a server and connecting from another computer you may need to add edit **ALLOWED_HOSTS** section in **./finalproject/settings.py**
        
 
- Start scrapy daemon
    - open another terminal or ssh connection and **cd ./scrapy_app**
    - enter the same virtual environment, can do **source ../.venv3-7/bin/activate**
    - start daemon with **scrapyd** this runs on the server at http://localhost:6800 by default

At this point both the django page and the scrapy daemon are running, you can browse to the site @ **IP:PORT/** and you will get the page to start the crawler. 

To stop running the servers, hit **ctrl+c** in each of the terminals.

### Tests

Test coverage should be over 90% at this point.

**READ THIS TO GET TESTS WORKING** The tests use a separate database, typically django will create a database TEST_defaultDatabaseName but we don't have permission to create databases on the class mysql server.
first you will need to change the database section in settings.py file under the finalproject folder, comment out the currently active Default section, then uncomment the section that looks like the lines below. This will use a local sqlite db file that it will create in the root directory.

    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'sqlite3.db', 
    }

- to run the unit tests enter virtual environment from root directory
    - **source .venv3-7/bin/activate**
    - you must also have the scrapyd server running for tests to execute properly.
        - Start scrapy daemon
            - open another terminal or ssh connection and **cd ./scrapy_app**
            - enter the same virtual environment, can do **source ../.venv3-7/bin/activate**
            - start daemon with command **scrapyd** this runs on the server at http://localhost:6800 by default
- finally execute command **python manage.py test**  this will execute the tests located in the tests directory

### Known issues/ future improvements
I prioritized my time elsewhere so here are a couple notable things that could be changed in future releases.

- I did not have a good way to pull date listed on offer up because they did not use abosolute time values and it would have needed conversion. ie datelisted = "Posted 8 hours ago".
- check the database for duplicates before saving them.
- adding some extra logic to the search function on Search DB tab, for example, demon pulls results that include demonstrate which may not be what the user wants.
- store address for main classified image so it can be shown.
- make a popover that shows full description text, not just title.
- change the way the link works, instead of it being in it's own cell.. maybe make the whole row clickable.
- maybe show items as cards instead of in a boring table.
- modify text boxes and site list they are just boring. 

#### resources

I have to give some credit to 2 resources (below) which I used and found helpful as I began to work on this project, they were focused on using django and scrapy together.

- https://medium.com/@ali_oguzhan/how-to-use-scrapy-with-django-application-c16fabd0e62e

- https://github.com/toukika/scrapy-with-django
