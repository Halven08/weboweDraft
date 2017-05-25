########################################################################################################################
# tweetView module for connecting with the twitter streaming API using tweepy module
# version 0.7.0
# 20.04.2017
#
# authors:
# Marta Mycielska
# Jacek Fidos
# Adam Szmatula
# Maciej Stanuch - macm550@gmail.com
########################################################################################################################

from time import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import io
import time

class listener(StreamListener):

    def __init__(self, time_limit, tweet_limit, fname, start_time = time.time()):

        self.time = start_time
        self.time_limit = time_limit
        self.tweet_limit = tweet_limit
        self.fname = fname;
        self.tweetCount = 0;


    def on_data(self, data):
        self.tweetCount = self.tweetCount + 1;
        saveFile = io.open(self.fname, 'a', encoding='utf-8', newline='\r\n')

        while (((time.time() - self.time) < self.time_limit) and (self.tweetCount <= self.tweet_limit)):

            print('number of tweets:', self.tweetCount, '/', self.tweet_limit, 'listeningTime:', (time.time() - self.time), '/', self.time_limit)
            try:
                saveFile.write(''.join(data).rstrip())
                saveFile.write('\n')
                return True

            except BaseException as e:
                print
                'failed ondata,', str(e)
                time.sleep(5)
                pass

        saveFile.close()

        self.running = False;
        print('tweets saved succesfully to ', self.fname)
        return False

    def on_error(self, status):
        print(status)

def startStream(ckey, csecret, atoken, asecret, fname, key_word, time_limit = float('inf'), tweet_limit = float('inf')):

    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, listener(time_limit=time_limit, fname=fname, tweet_limit=tweet_limit))
    twitterStream.filter(track=[key_word])
    twitterStream.disconnect();