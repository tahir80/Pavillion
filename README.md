# Pavilion
The Pavilion algorithm handles asynchronous arrival/departure of crowd workers from MTurk.com in the waiting and active queue for enabling real-time crowdsourcing (RTC)
## Introduction
Pavilion tries to retain workers in the active queue -- a queue which contains workers who are engaged with the task-- in addition to waiting queue based on turnover conditions (e.g. when workers leave the task either from the waiting or active queue). A worker can leave the task either when she submits a task, returns it, or abandons it.
Following conditions are handled in Pavilion:
1) When worker leaves from waiting queue by submitting Human Intelligence Task (HIT) --> Pavilion hires a new worker
2) When worker leaves from the active queue by submitting HIT --> **a)** Pavilion moves worker from waiting to active queue, **b)** Pavilion hires a new worker to fullfil the deficiency in the waiting queue
3) When worker leaves from the active queue by returning HIT --> Pavilion moves worker from waiting to the active queue
4) When worker leaves from the waiting queue by returning HIT --> NONE

## Main Logic for Pavilion
The main logic for Pavilion is contained in ***Pavilion\app\Pavilion\events.py*** file and ***Pavilion\app\Pavilion\routes.py***.

***expireHIT*** event handler expires a running HIT from admin --> EXPIRE HIT button on admin interface
```python 
@socketio.on('expireHIT', namespace='/chat')
```
***stop_this_job*** event handler allows clients (crowd interfaces) to submit HITs automatically --> STOP button on admin interface
```python 
@socketio.on('stop_this_job', namespace='/chat')
```
***Connected*** is the most important event handler.  
```python 
@socketio.on('connected', namespace='/chat')
```
***Connected*** event handler does number of things;
1. Checks whether a worker is a duplicate or new.
2. adds workers in the waiting queue until they reach to minimum threshold.
3. moves workers from waiting to active queue when they reach to minimum threshold.

***IAmReady*** event handler is called when a worker is pushed from waiting to active queue. You need to write a logic to store waiting task related bonuses. 
```python 
@socketio.on('IAmReady', namespace='/chat')
```
***submit_waiting*** event handler is called when a worker submits HIT while in the waiting queue. It changes the status of worker from waiting to submitted and also posts a new job. You may also need to write your own logic to store bonus related details.
```python 
@socketio.on('submit_waiting', namespace='/chat')
```
***submit_active*** event handler is called when a worker submits HIT while in the active queue. It changes the status of worker from active to submitted and also posts a new job. You may also need to write your own logic to store bonus related details.
```python 
@socketio.on('submit_active', namespace='/chat')
```
Now if you see ***Pavilion\app\Pavilion\routes.py***, you will find this ***/api/from_mturk*** event handler.
```python 
@Pavilion.route('/api/from_mturk', methods = ['GET', 'POST', 'PUT'])
```
This uses Amazon Simple Notification System (SNS). For setting up SNS, see following links;
1. https://blog.mturk.com/tutorial-using-amazon-sns-with-amazon-mturk-a0c6562717cb (FOR NECESSARY STEPS)
2. https://gist.github.com/iMilnb/bf27da3f38272a76c801 (FOR CONFIRMATION)

SNS will take care of all HITS that were either ***returned*** or ***abandoned*** and then updates queues accordingly as explained before.


## Admin Controls
In addition to managing workers in the active and waiting queue, we have also provided basic admin controls for;
1. Creating a new project
2. Creating a HIT/task on Amazon Mechanical Turk (MTurk)
3. Stopping a current job manually --> this will auto-submit HITs from all workers
4. Expiring a HIT 
5. Migrating workers manually if needed from waiting to active queue

## What is missing?
You need to write your own code for the following;
1. Handling payments of workers
2. you need to write task related logic (Pavilion\app\Pavilion --> events.py) and database tables (Pavilion\app\Pavilion --> models.py)

## Requirements
See requirements.txt for details about required dependencies.

## Local Testing
Uncomment the following code from run.py containing in the root folder. Make sure that ***create_app*** contains 'dev' as an argument. For production settings, change this to 'prod'
```python
#--------local testing----------------
if __name__ == "__main__":
    flask_app = create_app('dev')
    with flask_app.app_context():
        db.create_all()
    flask_app.run()
#------------------------------------------
```
Then simply type: ```python run.py ```

1. To register yourself as Admin: http://127.0.0.1:5000/register 
   *(username:harry@potters.com Password: secret)
2. To create a new project: http://127.0.0.1:5000/create_project
3. See waiting sample page: http://127.0.0.1:5000/waiting_task
4. See main task sample page: http://127.0.0.1:5000/main_task

## Steps for deployment on Heroku
1. clone our project and set it up in local git repository.
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

### AMAZON S3 storage
1. login to AWS console (https://aws.amazon.com/console/)
2. select Amazon S3 from storage
3. click on create new bucket
4. click next --> in manage users page, select 'public read acces' becuase Heroku needs to access our Database
5. when you click on the bucket name, it will lead you to a page where you can add files
6. upload **"Pavilion_DB.backup"** --> it is inside the root folder
7. click on the uploaded file --> copy the link and go to console again
8. type this: heroku pg:backups:restore "https://s3.eu-central-1.amazonaws.com/mybookcatalogdatabase/local_db.backup"
9. once done, restart the service using : heroku restart
