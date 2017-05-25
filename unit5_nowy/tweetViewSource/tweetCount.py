########################################################################################################################
# tweetView module for counting tweets in *.json files
# version 0.6.3
# 08.04.2017
#
# authors:
# Marta Mycielska
# Jacek Fidos
# Adam Szmatula
# Maciej Stanuch - macm550@gmail.com
########################################################################################################################

def tweetCount(fname):
    with open(fname, 'r', newline='\r\n') as f:
        tweetsCountLocal = 0;
        for line in f:
            #tweet = json.loads(line)  # loads tweets 'line by line', in this case one line is one tweet
            tweetsCountLocal = tweetsCountLocal + 1

    print('fname: ', fname)
    print('number of tweets in the data: ', tweetsCountLocal)


def tweetCountMulti(fnamesList):
    tweetsCountGlobal = 0;
    for fname in fnamesList:
        with open(fname, 'r', newline='\r\n') as f:
            tweetsCountLocal = 0;
            for line in f:
                #tweet = json.loads(line)  # loads tweets 'line by line', in this case one line is one tweet
                tweetsCountLocal = tweetsCountLocal + 1

        tweetsCountGlobal = tweetsCountLocal + tweetsCountGlobal;
        print('fname: ', fname)
        print('number of tweets in the data: ', tweetsCountLocal)
    print('overall tweets count: ', tweetsCountGlobal)
