from flask import render_template, url_for, flash, redirect,request,abort,jsonify,session
import requests
import json
import imaplib
from THAT import application,db,bcrypt,mail #using bcrypt to has the passwords in user database
from THAT.models import User, Lecture
from THAT.forms import RegistrationForm, LoginForm,LectureForm,SearchForm,MessageForm,UpdateAccountForm,FeedbackForm

from flask_login import login_user,current_user,logout_user,login_required
from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime, timedelta
from random import sample
from THAT.search import KMPSearch

import urllib.request
import urllib.parse
from flask_mail import Message

#--------------------------------------------------------------------------------------------
import time
import string
import pyaudio
import speech_recognition as sr
from plyer import notification 
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from nltk.tokenize import sent_tokenize, word_tokenize 
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from THAT.features import getRoS, getTranscript
#--------------------------------------------------------------------------------------------

import os
from os import path
import moviepy.editor as mp

#--------------------------------------------------------------------------------------------
#everything here that begins with @ is a decorator
@application.route("/")
@application.route("/home", methods=['GET', 'POST'])

@application.route("/home")
def home():
    return render_template('home.html',db=db,User=User,Lecture=Lecture)

@application.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')#looks for queries in request; args is a dictionary; we use get and not directly use 'next' as key to return the value because key might be empty leading to an error. get, in that case would fetch a none
            flash('Greetings '+form.username.data+'!','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@application.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.user_type == 'Professor':
        lectures=Lecture.query.filter_by(user_id=current_user.id).all()
    else:
        lectures=Lecture.query.all()
        
    lectures.reverse()
    form1=SearchForm()
    if form1.validate_on_submit():
        arr=[] 
        lectures2=[]
        for lecture in lectures:
            a=form1.search.data
            b=lecture.title
            if KMPSearch(a.casefold(),b.casefold()):
                arr.append(lecture.id)
                lectures2.append(Lecture.query.filter_by(id=lecture.id).first())
        if len(arr)==0:
            flash('Lecture not found!','warning')
            return redirect(url_for('dashboard'))
        else:
            data=json.dumps(form1.search.data)
            return render_template('search_lecture.html', title='Searched Lecture', lectures2=lectures2,data=data)
    return render_template('dashboard.html', title='Dashboard', lectures=lectures,form1=form1)
    

@application.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) #redirects user to dashboard if already logged in; function name is passed in url_for
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        #if app_password field is not-empty
        user=User(username=form.username.data,email=form.email.data,user_type = form.user_type.data,password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash(f'You have successfully registered.', 'success')
        return redirect(url_for('dashboard'))
    image_file=url_for('static',filename='images/user.png')
    return render_template('register.html', title='Register', image_file=image_file,form=form)

@application.route("/logout")
def logout():
    logout_user()
    flash('You have logged out  !','success')
    return redirect(url_for('home'))

@application.route("/account")
@login_required
def account():
    image_file=url_for('static',filename='images/user.png')
    return render_template('account.html',title='Account',image_file=image_file)

@application.route("/account/update",methods=['GET', 'POST'])
@login_required
def update_account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
       # hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #returns hashed password, decode converts it from byte to string
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Account updated successfully!','success')
        return redirect(url_for('account'))
    elif request.method=='GET':  #if submit btn is not clicked and account page is requested, it eill already fill the usename field with existing data
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('update_account.html',title='Update Account',image_file=image_file,form=form,legend='Update credentials')

@application.route("/account/delete",methods=['GET', 'POST'])
@login_required
def delete_account():
    user=User.query.filter_by(id=current_user.id).first()
    lectures=Lecture.query.filter_by(user_id=current_user.id).all()
    for lecture in lectures:
        db.session.delete(lecture)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted','success')
    return redirect(url_for('home'))

@application.route("/lecture/new",methods=['GET', 'POST'])
@login_required
def new_lecture():
    form=LectureForm()
    if form.validate_on_submit():
        lecture1=Lecture(title=form.title.data,date=form.date.data,starttime=form.starttime.data, endtime=form.endtime.data,details=form.details.data,video_path=form.video_path.data,user_id=current_user.id)
        db.session.add(lecture1)
        db.session.commit()               
        flash('Lecture scheduled!','success')
        return redirect(url_for('dashboard'))
    return render_template('upload_lecture.html',title='New Lecture',form=form, legend='Schedule Lecture')


@application.route("/lecture/ <int:lecture_id>")
@login_required
def lecture(lecture_id):
    lecture=Lecture.query.get_or_404(lecture_id) #get_or_404 returns the requested page if it exists else it returns a 404 error
    return render_template('lecture.html',title=lecture.title,lecture=lecture)

@application.route("/lecture/ <int:lecture_id>/update",methods=['GET', 'POST'])
@login_required
def update_lecture(lecture_id):
    lecture=Lecture.query.get_or_404(lecture_id)
    if lecture.user_id!=current_user.id:  # this is optional since we display only a prticular user's lectures in his dashboard
        abort(403)
    form=LectureForm()
    if form.validate_on_submit():
        lecture.title = form.title.data
        lecture.details = form.details.data
        lecture.date=form.date.data
        lecture.starttime=form.starttime.data
        lecture.endtime=form.endtime.data
        db.session.commit()
        flash('Lecture updated!', 'success')
        return redirect(url_for('lecture',lecture_id=lecture.id))
    elif request.method == 'GET':
        form.title.data = lecture.title
        form.details.data = lecture.details
        form.date.data=lecture.date
        form.starttime.data=lecture.starttime
        form.endtime.data=lecture.endtime
    return render_template('upload_lecture.html', title='Update Lecture',form=form, legend='Update Lecture')

@application.route("/lecture/ <int:lecture_id>/delete",methods=['GET', 'POST'])

@login_required
def delete_lecture(lecture_id):
    lecture=Lecture.query.get_or_404(lecture_id)
    if lecture.user_id!=current_user.id:  # this is optional since we display only a prticular user's lectures in his dashboard
        abort(403)
    db.session.delete(lecture)
    db.session.commit()
    flash('Lecture deleted!','warning')
    return redirect(url_for('dashboard'))

@application.route("/contact_us",methods=['GET', 'POST'])
def contact_us():
    form=MessageForm()
    if current_user.is_authenticated:
        form.email.data=current_user.email
    if form.validate_on_submit():
        msg=Message('Sent by THAT user: '+current_user.username,sender=form.email.data,recipients=['that.admn@gmail.com']) 
        msg.body=f'''Sent from THAT contact us page:
        {form.message.data}'''
        mail.send(msg)
        flash('Your message has been sent.','success')
    return render_template("contact_us.html",form=form)

@application.route("/feedback",methods=['GET', 'POST'])
def feedback():
    form=FeedbackForm()
    if current_user.is_authenticated:
        form.email.data=current_user.email
    if form.validate_on_submit():
        msg=Message('Sent by THAT Student: '+current_user.username,sender=form.email.data,recipients=['kgp.admin@gmail.com']) 
        msg.body=f'''Sent from THAT Feedback:
        {form.feedback.data}'''
        mail.send(msg)
        flash('Your message has been sent.','success')
    return render_template("feedback.html",form=form)

#--------------------------------------------------------------------------------------------
@application.route("/speechAsisstance",methods=['GET', 'POST'])
def speechAsisstance():
    return render_template("speechAsisstance.html") 


@application.route("/speechAsisstance_RoS")
def speechAsisstance_RoS():
    print("Starting Recording\n")
    average_RoS, words_in_speech, text = getRoS()
    string3 = str(words_in_speech) + " words"
    string4 = str(average_RoS) + " words/min" 
    message1 = "<h3>" +str(average_RoS) + " words/min</h3>" 
    message2 = "<h5 class=\"mb-6\">You said        : <span class=\"text-muted h5 font-weight-normal\">" + text + "<br></span></h5>"
    message3 = "<h5 class=\"mb-6\">Words in Speech : <span class=\"text-muted h5 font-weight-normal\">" + string3 + "<br></></h5>"
    message4 = "<h5 class=\"mb-6\">Rate of Speech  : <span class=\"text-muted h5 font-weight-normal\">" + string4 + "<br></></h5>"
    
    ret_val = jsonify(message1 =message1, message2= message2 ,message3=message3,message4=message4)
    return ret_val

#--------------------------------------------------------------------------------------------
# Devarshi Functions
#--------------------------------------------------------------------------------------------
@application.route("/transcripts",methods=['GET', 'POST'])
def transcripts():
    if current_user.user_type == 'Professor':
        lectures=Lecture.query.filter_by(user_id=current_user.id).all()
    else:
        lectures=Lecture.query.all()
        
    lectures.reverse()
    return render_template("transcripts.html",lectures=lectures) 

@application.route("/getranscripts",methods=['GET', 'POST'])
def getranscripts():
    #path = path of current_lecture
    path = "C:/Users/abhin/Downloads/THAT_V1/THAT/static/video/video_7.mp4"
    transcript = getTranscript(path)
    transcript ="<h4 id =\"Transcripts\" style=\"font-size: medium;font-family: 'Courier New', Courier, monospace;\">" + str(transcript) + "</h4>"  
    ret_val = jsonify(message = transcript)
    return ret_val


@application.route("/video_player/ <int:lecture_id>")
@login_required
def video_player(lecture_id):
    lecture=Lecture.query.get_or_404(lecture_id) #get_or_404 returns the requested page if it exists else it returns a 404 error
    return render_template('video_player.html',title=lecture.title,lecture=lecture)

    
@application.route("/video_transcripts/ <int:lecture_id>",methods=['GET', 'POST'])
@login_required
def video_transcripts(lecture_id):
    lecture=Lecture.query.get_or_404(lecture_id) #get_or_404 returns the requested page if it exists else it returns a 404 error
    return render_template('video_transcripts.html',title=lecture.title,lecture=lecture)


#--------------------------------------------------------------------------------------------