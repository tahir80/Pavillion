# Pavillion
Pavilion algorithm handles asynchronous arrival/departure of workers in the waiting and active queue for enabling real-time crowdsourcing (RTC)
## Introduction
Pavilion tries to retain workers in the active queue -- a queue which contains workers who are engaged with the task-- in addition to waiting queue based on turnover conditions (e.g. when workers leave the task either from the waiting or active queue). A worker can leave the task either when she submits a task, returns it, or abandons it.
Following conditions are handled in Pavilion:
1) Worker leaves from waiting queue by submitting Human Intelligence Task (HIT) --> Pavilion hires a new worker
2) Worker leaves from active queue by submitting HIT
a. Pavilion moves worker from waiting to active queue
b. Pavilion hires a new worker to fulfil the deficiency in waiting queue

3) Worker leaves from active queue by returning HIT --> Pavilion moves worker from waiting to active queue
4) Worker leaves from waiting queue by returning HIT --> NONE

## Requirements
1. Flask==1.0.2
2. Flask-Bcrypt==0.7.1
3. Flask-Bootstrap==3.3.7.1
4. Flask-Login==0.4.1
5. Flask-SQLAlchemy==2.3.2
6. Flask-WTF==0.14.2
7. gunicorn==18.0
8. SQLAlchemy==1.2.10
9. WTForms==2.2.1
10. boto==2.49.0
11. boto3==1.9.42
12. Flask-SocketIO==3.0.2

