# Pavilion
Pavilion algorithm handles asynchronous arrival/departure of workers in the waiting and active queue for enabling real-time crowdsourcing (RTC)
## Introduction
Pavilion tries to retain workers in the active queue -- a queue which contains workers who are engaged with the task-- in addition to waiting queue based on turnover conditions (e.g. when workers leave the task either from the waiting or active queue). A worker can leave the task either when she submits a task, returns it, or abandons it.
Following conditions are handled in Pavilion:
1) Worker leaves from waiting queue by submitting Human Intelligence Task (HIT) --> Pavilion hires a new worker
2) Worker leaves from the active queue by submitting HIT --> **a)** Pavilion moves worker from waiting to active queue, **b)** Pavilion hires a new worker to fullfil the deficiency in the waiting queue
3) Worker leaves from the active queue by returning HIT --> Pavilion moves worker from waiting to the active queue
4) Worker leaves from the waiting queue by returning HIT --> NONE

## Admin Controls
In addition to managing workers in the active and waiting queue, We have also provided basic admin controls for;
1. Creating a new project
2. Creating a HIT/task on Amazon Mechanical Turk (MTurk)
3. Stopping a current job manually --> this will auto-submit HITs from all workers
4. Expiring a HIT 
5. Migrating workers manually if needed from waiting to active queue

## What is missing?
You need to write your own code for the following;
1. Handling payments of workers
2. adding contents for waiting and main task pages

## Requirements (selected)
1. Flask==1.0.2
2. Flask-Bcrypt==0.7.1
3. Flask-Bootstrap==3.3.7.1
4. Flask-Login==0.4.1
5. Flask-SQLAlchemy==2.3.2
6. Flask-WTF==0.14.2
7. gunicorn==18.0
8. eventlet==0.24.1
9. SQLAlchemy==1.2.10
10. WTForms==2.2.1
11. boto==2.49.0
12. boto3==1.9.42
13. Flask-SocketIO==3.0.2   
**Note:** See requirements.txt for more packages.

## Local Testing
uncomment the following code from run.py from the root folder
```python
#--------local testing----------------
if __name__ == "__main__":
    flask_app = create_app('dev')
    with flask_app.app_context():
        db.create_all()
    flask_app.run()
#------------------------------------------
```
## Steps for deployment on Heroku
1. clone our project
2. Sign up for Heroku
3. download and install Heroku CLI
4. create an app first, give it a unique name
5. then create a database --> click on resources tab under your newly created app --> search postgres --> and add hobby-dev (it's free)
6. click on your database name -->click on settings -->credentials --> you can copy the URI to the prod.py file but its NOT RECOMMENDED, you don't need to do anything. Everything is setup in prod.py under config folder.
7. now come back to console and type: heroku login
8. go back to app, and click on deploy and then run the following commands(you must be in the root folder of your project)
```
git add .
git commit -am "make it better"
git push heroku master
```
9. you can open the website using heroku open or use provided url after successful installtion

## AMAZON S3 storage
1. login to AWS console (https://aws.amazon.com/console/)
2. select Amazon S3 from storage
3. click on create new bucket
4. click next --> in manage users page, select 'public read acces' becuase Heroku needs to access our Database
5. when you click on the bucket name, it will lead you to a page where you can add files
6. upload **"Pavilion_DB.backup"** --> it is inside the root folder
7. click on the uploaded file --> copy the link and go to console again
8. type this: heroku pg:backups:restore "https://s3.eu-central-1.amazonaws.com/mybookcatalogdatabase/local_db.backup"
9. once done, restart the service using : heroku restart
