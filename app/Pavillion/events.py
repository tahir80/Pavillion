from app import db
from app.auth.models import User
from app.admin_panel.models import Project, Task
from app.Pavillion.models import Session, LiveStatus, WorkerStatus, Worker, DetailedStatus, Assignments, SESSION_SQLALCHEMY

from app.Pavillion import Pavillion

from sqlalchemy import exc,asc, desc, and_, or_
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask import session, request
from flask import render_template, request, redirect, url_for, flash # for flash messaging
from app import socketio
import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price
import boto3

from app import connection, connection2


@socketio.on('expireHIT', namespace='/chat')
def expireHIT(data):

    #here you need to write code for HIT expireation
    s = Session.query.filter_by(status="Live").first()

    assigns = db.session.query(Assignments.hit_id).\
                            filter(Assignments.s_id == s.id).\
                            distinct()

    for assign in assigns:
        print(assign.hit_id)
        try:
            response = connection.update_expiration_for_hit(
            HITId=assign.hit_id,
            ExpireAt=datetime.datetime(2015, 1, 1))
        except:
            print("an error occured for hitID!", assign.hit_id)

    #here you can change the task + session table
    s.s_end_time = datetime.datetime.utcnow()
    s.status = "expired"

    task = db.session.query(Task).filter(Task.id==data['taskID']).first()
    task.task_status = "Not Active"
    db.session.commit()


@socketio.on('stop_this_job', namespace='/chat')
def stopJob(data):
    try:

        server_session = SESSION_SQLALCHEMY.query.filter_by(id=2).first()
        server_session.Name = 'no'

        precondition_met = SESSION_SQLALCHEMY.query.filter_by(id=3).first()
        precondition_met.Name = 'not met'

        db.session.commit()
    except:
        pass

    emit('stop', {}, broadcast = True)


@socketio.on('connected', namespace='/chat')
def connected(data):
    # isInitialConditionMet = False  # this flag will prevent premature moving waiting workers until precondition meets.
    try:

        ##Write a code to determine whether a same user with same status wants to re-join the session again? it might be due to page reload..
       duplicate = False
       worker = Worker.query.filter_by(AMT_worker_id=data['workerId']).first()

       if worker != None: # that means worker already exists in our worker's list. If value is None, then its a brand new worker and duplicate remains False
            s = Session.query.filter_by(status="Live").first() # grab live session
            status = LiveStatus.query.filter(LiveStatus.s_id == s.id).\
                                      filter(LiveStatus.w_id == worker.id).\
                                      filter(or_(LiveStatus.status_id == 1,LiveStatus.status_id == 2)).first()
            if status != None:
                if status.status_id == 1 or status.status_id == 2:
                    print(status.status_id)
                    duplicate = True
       print(duplicate)

       if not duplicate:

               ################Fethcing Queue variables in advance###########
            try:
               s = Session.query.filter_by(status="Live").first()
               task = db.session.query(Task).filter(Task.id==s.t_id).first()
               # Max.Threshold values for ACTIVE and WAITING workers
               MAX_ACTIVE = task.max_active
               MAX_WAITING = task.max_waiting
               #-------------------------------
               #pre-conditions to start the job
               #-------------------------------
               MIN_ACTIVE = task.min_active
               MIN_WAITING = task.min_waiting
               #------------------------

            except:
                pass

            waiting_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
            active_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 2).count()
            print('waiting_workers_count', waiting_workers_count)
            print('active_workers_count', active_workers_count)
            #This condition will only be executed at the start, when workers reach min.threshold value and active
            # workers are still empty.
            if waiting_workers_count == MIN_ACTIVE and active_workers_count == 0:

                server_session = SESSION_SQLALCHEMY.query.filter_by(id=3).first()
                server_session.Name = 'met'
                db.session.commit()

                records = LiveStatus.query.filter(LiveStatus.status_id == 1).all()
                workers_list = []
                for worker_status in records:
                    #change status of workers from 'waiting' to 'active'
                    worker_status.status_id = 2
                    w_ids = Worker.query.filter_by(id=worker_status.w_id).first()

                    #append workers to list (this was done to send message to only specific/active clients)
                    workers_list.append(w_ids.AMT_worker_id)

                    #also add rows to DetailedStatus table Here
                    ds = DetailedStatus(worker_status.id, 2, datetime.datetime.utcnow())
                    db.session.add(ds)
                    db.session.commit()

                emit('start_your_task', {'message': workers_list}, broadcast = True)


            # cannot accept more workers. This situation will never reach in reality (we will post the job according to waiting + active)
            if waiting_workers_count == MAX_WAITING and active_workers_count == MAX_ACTIVE:
                emit('job_is_full', {'message': "Sorry, this Job is already full. Please try later", 'id': data['workerId']}, broadcast = True)

            #store worker to DB and update live status.
            #only store data if job is not full
            if waiting_workers_count != MAX_WAITING or active_workers_count != MAX_ACTIVE:

                if not Worker.query.filter_by(AMT_worker_id=data['workerId']).first():
                    worker = Worker(data['workerId'])
                    db.session.add(worker)
                    db.session.flush()
                else:
                    worker = Worker.query.filter_by(AMT_worker_id=data['workerId']).first()
                #grab an active session
                current_session = Session.query.filter_by(status="Live").first()

                # hits = HITS.query.filter_by(s_id=current_session.id).order_by(desc(HITS.time_stamp)).first()

                assign = Assignments(worker.id, data['hit_id'], data['aid'], current_session.id, datetime.datetime.utcnow())
                db.session.add(assign)

                live_status = LiveStatus(worker.id, current_session.id, 1, datetime.datetime.utcnow())

                db.session.add(live_status)
                db.session.flush()
                #add row to DetailedStatus Table
                ds = DetailedStatus(live_status.id, 1, datetime.datetime.utcnow())
                db.session.add(ds)
                #save changes
                db.session.commit()

                #You need to check whether any waiting worker can be moved to active list?
                waiting_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
                active_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 2).count()

                precondition = SESSION_SQLALCHEMY.query.filter_by(id=3).first()

                if isMovePossible(waiting_workers_count, active_workers_count, MAX_ACTIVE, MIN_WAITING) and precondition.Name == 'met':

                    l_s_worker = LiveStatus.query.filter_by(status_id=1).order_by(asc(LiveStatus.time_stamp)).first()

                    l_s_worker.status_id = 2 # add to active member list

                    ds = DetailedStatus(l_s_worker.id, 2, datetime.datetime.utcnow())
                    db.session.add(ds)
                    db.session.commit()
                    # live_status_workers = LiveStatus.query.filter_by(status_id=1).all()
                    # l_s_worker = live_status_workers.order_by(asc(live_status_workers.time_stamp)).limit(1).first()
                    worker = Worker.query.filter_by(id=l_s_worker.w_id).first()
                    emit('start_your_task', {'message': [worker.AMT_worker_id]}, broadcast = True)


            # update notice board with worker count
            workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
            emit('update_worker_count', {'count': workers_count, 'max_count': MAX_WAITING}, broadcast = True)


    except exc.IntegrityError:
        pass

@socketio.on('IAmReady', namespace='/chat')
def client_is_ready(data):
    workerId = data['worker']
    time_waited = data['time_waited']
    reward = data['reward']

    try:
        s = Session.query.filter_by(status="Live").first()
        w = Worker.query.filter_by(AMT_worker_id=workerId).first()
        reward_waiting = RewardWaiting(w.id, s.id,reward,time_waited)
        reward_active = RewardActive(w.id, s.id,0)
        db.session.add(reward_waiting)
        db.session.add(reward_active)
        db.session.commit()
    except exc.IntegrityError:
        pass

@socketio.on('submit_waiting', namespace='/chat')
def submit_waiting(data):

    workerId = data['worker']
    time_waited = data['time_waited']
    reward = data['reward']
    assignId = data['aid']
    hitId = data['hit_id']
        # Save Reward related data
    try:
        s = Session.query.filter_by(status="Live").first()
        w = Worker.query.filter_by(AMT_worker_id=workerId).first()
        reward_waiting = RewardWaiting(w.id, s.id,reward,time_waited)
        db.session.add(reward_waiting)
        #change status from 'waiting' --> 'submitted', only select worker who is waiting
        live_status = LiveStatus.query.filter(and_(LiveStatus.w_id == w.id, LiveStatus.status_id == 1)).first()
        # live_status = LiveStatus.query.filter_by(w_id=w.id).first()
        live_status.status_id = 3

        #add row to DetailedStatus Table
        ds = DetailedStatus(live_status.id, 3, datetime.datetime.utcnow())
        db.session.add(ds)

        #update Assignments table
        assigns = Assignments.query.filter(Assignments.w_id==w.id).\
                                    filter(Assignments.hit_id==hitId).\
                                    filter(Assignments.assign_id==assignId).first()
        assigns.status_id = 3

        db.session.commit()

        waiting_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
        active_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 2).count()
        emit('workers_status', {'waiting': waiting_workers_count,
                                'active': active_workers_count},
                                 broadcast = True)
    except exc.IntegrityError:
        pass

    #Post a new Job, first check whether admin has pressed the 'stop' button? if admin press the stop
    #button then the value of name would be 'no' and posting a job would be skipped.
    server_session = SESSION_SQLALCHEMY.query.filter_by(id=2).first()
    if server_session.Name == 'yes':
        postJob(s.t_id)

@socketio.on('submit_active', namespace='/chat')
def submit_active(data):
    workerId = data['worker']
    assignId = data['aid']
    hitId = data['hit_id']

    try:

        ############STEP #1: Change the status of worker who submit the job#########################
        s = Session.query.filter_by(status="Live").first()
        w = Worker.query.filter_by(AMT_worker_id=workerId).first()

        live_status = LiveStatus.query.filter(and_(LiveStatus.w_id == w.id, LiveStatus.status_id == 2)).first()
        # live_status = LiveStatus.query.filter_by(w_id=w.id).first()
        live_status.status_id = 3

        #add row to DetailedStatus Table
        ds = DetailedStatus(live_status.id, 3, datetime.datetime.utcnow())
        db.session.add(ds)

        #update Assignments table
        assigns = Assignments.query.filter(Assignments.w_id==w.id).\
                                    filter(Assignments.hit_id==hitId).\
                                    filter(Assignments.assign_id==assignId).first()
        assigns.status_id = 3

        #update the RewardActive Table with total waiting time  + time based Bonus (Duplicate workers: again only latest worker from the current session)
        reward_active = RewardActive.query.filter(and_(RewardActive.w_id==w.id, RewardActive.s_id==s.id)).order_by(desc(RewardActive.time_stamp)).first()
        reward_active.waited_time = data['time_waited']
        reward_active.time_based_bonus = 0.0

        db.session.commit()

        ################Fethcing Queue variables in advance###########
        try:
            s = Session.query.filter_by(status="Live").first()
            task = db.session.query(Task).filter(Task.id==s.t_id).first()
            # Max.Threshold values for ACTIVE and WAITING workers
            MAX_ACTIVE = task.max_active
            MAX_WAITING = task.max_waiting
            #-------------------------------
            #pre-conditions to start the job
            #-------------------------------
            MIN_ACTIVE = task.min_active
            MIN_WAITING = task.min_waiting
            #------------------------

        except:
            pass

        waiting_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
        active_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 2).count()
        print('waiting_workers_count', waiting_workers_count)
        print('active_workers_count', active_workers_count)
        #You need to check whether any waiting worker can be moved to active list?
        if isMovePossible(waiting_workers_count, active_workers_count, MAX_ACTIVE, MIN_WAITING):

            l_s_worker = LiveStatus.query.filter_by(status_id=1).order_by(asc(LiveStatus.time_stamp)).first()

            l_s_worker.status_id = 2 # add to active member list

            ds = DetailedStatus(l_s_worker.id, 2, datetime.datetime.utcnow())
            db.session.add(ds)
            db.session.commit()
            worker = Worker.query.filter_by(id=l_s_worker.w_id).first()
            emit('start_your_task', {'message': [worker.AMT_worker_id]}, broadcast = True)

        emit('workers_status', {'waiting': waiting_workers_count,
                                'active': active_workers_count},
                                 broadcast = True)

    except exc.IntegrityError:
        pass

    #Step 3:Post a new Job ###################################################
    #Post a new Job, first check whether admin has pressed the 'stop' button? if admin press the stop
    #button then the value of name would be 'no' and posting a job would be skipped.
    server_session = SESSION_SQLALCHEMY.query.filter_by(id=2).first()
    if server_session.Name == 'yes':
        postJob(s.t_id)


@socketio.on('isJobFull', namespace='/chat')
def isJobFull(data):
    if isFull():
        emit('job_is_full', {'message': "Sorry, this Job is currently full. Please try later", 'id': data['workerId']}, broadcast = True)


def isFull():
    try:
        s = Session.query.filter_by(status="Live").first()
        task = db.session.query(Task).filter(Task.id==s.t_id).first()

        MAX_ACTIVE = task.max_active
        MAX_WAITING = task.max_waiting

        waiting_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 1).count()
        active_workers_count = LiveStatus.query.filter(LiveStatus.status_id == 2).count()

        if waiting_workers_count == None:
            waiting_workers_count = 0
        if active_workers_count == None:
            active_workers_count = 0

        if waiting_workers_count == MAX_WAITING and active_workers_count == MAX_ACTIVE:
            return True
        else:
            return False
    except:
        return False


def postJob(task_id):


    hit = db.session.query(Task).filter(Task.id==task_id).first()

    ##############################################################
    #source: https://github.com/numaer/psyturk/blob/master/hits.py
    #############################################################
    connection.create_hit_with_hit_type(
    HITTypeId = hit.HIT_Type_id,
    MaxAssignments = 1,
    LifetimeInSeconds = hit.hit_expiry,
    Question = ExternalQuestion(hit.task_url, 800).get_as_xml())


def isMovePossible(waiting, active, max_active, min_waiting):

    if (waiting - 1) > (min_waiting - 1) and (active + 1) <= max_active:
        return True
    else:
        return False
