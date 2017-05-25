########################################################################################################################
# tweetView
# version 0.7.0
# 20.04.2017
#
# authors:
# Marta Mycielska
# Jacek Fidos
# Adam Szmatula
# Maciej Stanuch - macm550@gmail.com
#
# this app allows to stream data from Twitter in real-time concerning tweets with specified key words
# it allows also to process collected tweets and save them to the *.xlsx file
#
# input:
#       -   fType - type of action you want to perform, list of actions if defined right after import statements
#       -   conf.py - file with Twitter API dev codes
#       -   key word - specifies what should be in tweets that you want to gather
#       -   time limit - how long do we want to stream data, if not given the time is not limited
#       -   tweets limit - how many tweets do we want to stream, if not given the number of tweets is not limited
#       -   fname - name for the *.xlsx output file
# output:
#       -   *.json file - raw file with tweets containing all the possible meta-data
#       -   *.xlsx file - output file containing basic statistics for the downloaded file
#
# notes:
#       To handle bigger data sets it is recommended to use 64-bit python build
#######################################################################################################################

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

def action(fType):
    return {
        'streamTwitter': 1,
        'oneFile': 2,
        'multi2mult': 3,
        'multi2one': 4,
        'tweetCount': 5,
        'tweetCountMulti': 6
    }[fType]

def tweetView(fType, fname = 'raw_test.json', key_word = '#python',
              time_limit = float('inf'), tweet_limit = float('inf')):

    actionType = action(fType)

    if (actionType == 1):
        confSecret.getCodes()

        #listens until one of the limits is met, if a limit is not set the limit is disabled
        tweetStream.startStream(ckey = confSecret.ckey, csecret = confSecret.csecret, atoken = confSecret.atoken,
                                asecret = confSecret.asecret, fname = fname, key_word = key_word,
                                time_limit = time_limit,
                                tweet_limit = tweet_limit
                                );

    elif (actionType == 2):
     #   fname = 'raw_testTweet.json'  # set the file to process
    #   processes the downloaded file and makes a *.xlsx file with statistics
        JSON2XLS.summary2xls(fname)

    elif(actionType == 3):
    #   to process all the files in the folder to separate *.xlsx files
        fileNames = glob.glob('*.json')
        for fname in fileNames:
            JSON2XLS.summary2xls(fname)

    elif(actionType == 4):
    #   to process all the files into a single *.xlsx file
        fnamesList = glob.glob('*.json')
        fname = os.path.relpath(".","..")
        JSON2XLS.summary2onexls(fnamesList, fname)

    elif(actionType == 5):
    #   to count number of tweets in a file
        tweetCount.tweetCount(fname)
    elif(actionType == 6):
    #   to count number of tweets in files in current folder
        fnamesList = glob.glob('*.json')
        tweetCount.tweetCountMulti(fnamesList)


# fname2 = 'raw_test14.json';
# tweetView('streamTwitter', fname2, 'trump', time_limit = 10, tweet_limit = float('inf'))
# tweetView('tweetCountMulti')
#
# tweetView('oneFile', fname2)

#tweetView('tweetCount', fname2)