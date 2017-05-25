from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import statistics

# modules for the easyStream function
from time import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import io
import time

# modules for the JSON2XLS_oneFIle function
import json
from collections import Counter
import re
from nltk.corpus import stopwords
import string
import tablib
import time
import glob
import os

import confSecret
import tweetStream
import JSON2XLS
import tweetCount
from mainTweetView import tweetView
import mainTweetView

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'

db = SQLAlchemy(app)

class Formdata(db.Model):
    __tablename__ = 'formdata'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    firstname = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    age = db.Column(db.Integer)
    income = db.Column(db.Integer)
    satisfaction = db.Column(db.Integer)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)

    def __init__(self, firstname, email, age, income, satisfaction, q1, q2):
        self.firstname = firstname
        self.email = email
        self.age = age
        self.income = income
        self.satisfaction = satisfaction
        self.q1 = q1
        self.q2 = q2

db.create_all()


@app.route("/")
def welcome():
    return render_template('welcome.html')

@app.route("/form")
def show_form():
    return render_template('form.html')

@app.route("/analysis")
def show_analysis():
    return render_template('analysis.html')

@app.route("/raw")
def show_raw():
    fd = db.session.query(Formdata).all()
    return render_template('raw.html', formdata=fd)

@app.route("/resultDebate")
def show_debateResult():
    return render_template('resultDebate.html')

@app.route("/result")
def show_result():

    return render_template('result.html')


@app.route("/save", methods=['POST'])
def save():
    # Get data from FORM
    firstname = request.form['firstname']
    email = request.form['email']
    age = request.form['age']
    income = request.form['income']
    satisfaction = request.form['satisfaction']
    q1 = request.form['q1']
    q2 = request.form['q2']

    # Save the data
    fd = Formdata(firstname, email, age, income, satisfaction, q1, q2)
    db.session.add(fd)
    db.session.commit()

    return redirect('/')

@app.route("/tweetAnalysis", methods=['POST'])
def tweetAnalysis():
    # Get data from FORM
    keyword = request.form['keyword']
    noOfTweets = int(request.form['noTweetsToGet'])
    timeOfListening = int(request.form['timeOfListening'])

    dateString = str(datetime.now())

    #fname2 = (keyword + dateString + '.json').rstrip();
    fname2 = keyword + '.json';
    # Save the data
    #keyword = string(keyword);
    tweetView('streamTwitter', fname2, 'water', time_limit=10, tweet_limit=10)
    # if 'noOfTweets' in locals():
    #     # myVar exists.
    #     if 'timeOfListening' in locals():
    #         tweetView('streamTwitter', fname2, keyword, time_limit=timeOfListening, tweet_limit=noOfTweets)
    #
    #     else:
    #         tweetView('streamTwitter', fname2, keyword, time_limit=300, tweet_limit=noOfTweets)
    # else:
    #     if 'timeOfListening' in locals():
    #         tweetView('streamTwitter', fname2, keyword, time_limit=timeOfListening, tweet_limit=500)
    #     else:
    #         tweetView('streamTwitter', fname2, keyword, time_limit=300, tweet_limit=500)

    tweetCountString = tweetView('tweetCount', fname2);
    tweetView('oneFile', fname2);
    return redirect('/')


if __name__ == "__main__":
    app.debug = True
    app.run()