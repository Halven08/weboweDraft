########################################################################################################################
# Print most common words in a corpus collected from Twitter to *.xlsx files with different parameters
# version 0.6.3
# 08.04.2017
#
# authors:
# Marta Mycielska
# Jacek Fidos
# Adam Szmatula
# Maciej Stanuch - macm550@gmail.com
########################################################################################################################

import sys
import json
from collections import Counter
import re
from nltk.corpus import stopwords
import string
import tablib
import time
import glob

punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via']

xd_str=r"""
(?:
    [xX]  # Eyes
    [dD]  # Mouth
)"""

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [dD\)\]\(\]/\\OpPC] # Mouth
    )"""


regex_str = [
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs
    emoticons_str,
    emoticons_str,
    xd_str,
    r"[\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF]", # emoji
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",   # hash-tags
    r'<[^>]+>',                         # HTML tags
    r'(?:@[\w_]+)',                     # @-mentions
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',       # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",        # words with - and '
    r'(?:[\w_]+)',                      # other words
]

tokens_re =  re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE )
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

Emots_str=[
    emoticons_str,
    emoticons_str,
    xd_str,
    r"[\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF]",
]
Emots_re =  re.compile(r'(' + '|'.join(Emots_str) + ')', re.VERBOSE | re.IGNORECASE )

Hash_str = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"
Hash_re = re.compile(Hash_str, re.UNICODE | re.IGNORECASE)


def tokenize(s):
    return tokens_re.findall(s)


def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

class Quantizer:
    PostLen=0
    TokensNr=0
    WordsNr=0
    EmosNr=0
    TagsNr=0


def summary2xls(fname):
    with open(fname, 'r',  newline='\r\n') as f:
        count_all = Counter()
        count_emots_n_emoji = Counter()
        count_hashes = Counter()
        FileStats=[]
        PostsNumber=0

        data = tablib.Dataset()
        data.headers = ('id', 'created_at', 'followers', 'friends', 'statuses', 'created', 'location', 'text', 'key_word', 'post_lenght', 'token_count', 'word_count', 'emo_count', 'hash_count')

        for line in f:
            FileStats.append(Quantizer())
            tweet = json.loads(line)

            keys = tweet.keys();
            if 'text' in tweet:
                textField = tweet['text'];
            else:
                continue;
            PostLength = len(textField)  # length of the tweet in singns
            tokens = preprocess(textField)
            count_all.update(tokens)

            TokensCount = sum(1 for _ in tokens)  # number of tokens in a tweet

            HashTokens = [token for token in tokens if Hash_re.match(token)]  # recognize tokens which are hashtags
            count_hashes.update(HashTokens)
            HashCount = sum(1 for _ in HashTokens)  # number of hashtags in a tweet

            EmoTokens = [token for token in tokens if Emots_re.match(token)]  # recognize tokens which are emoji
            count_emots_n_emoji.update(EmoTokens)
            EmoCount = sum(1 for _ in EmoTokens)  # number of emoji in a tweet

            WordCount = TokensCount - HashCount - EmoCount  # number of words, url's and @names in a tweet (sum)

            FileStats[PostsNumber].PostLen=PostLength
            FileStats[PostsNumber].TokensNr=TokensCount
            FileStats[PostsNumber].WordsNr = WordCount
            FileStats[PostsNumber].EmosNr = EmoCount
            FileStats[PostsNumber].TagsNr = HashCount
            PostsNumber+=1

            # date conversion
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
            ts_user = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
            # save to file
            data.append((tweet['id'], ts, tweet['user']['followers_count'], tweet['user']['friends_count'], tweet['user']['statuses_count'], ts_user, tweet['user']['location'], tweet['text'], fname, PostLength, TokensCount, WordCount, EmoCount, HashCount))

        common_tokens = count_all.most_common()  # most popular tokens in the file, string - number pair
        common_emos = count_emots_n_emoji.most_common()  # most popular emoticons and emoji in the file, string - number pair
        common_hashes = count_hashes.most_common()  # most popular hashtags in the file, string - number pair

        OverallStats = Quantizer  # values() or most_common() functions generate tables that are easier to handle for debugging
        OverallStats.TokensNr = sum(count_all.values())  # overall in file token number
        OverallStats.EmosNr = sum(count_emots_n_emoji.values())  # overall in file emoji+emoticon number
        OverallStats.TagsNr = sum(count_hashes.values())  # overall in file hashtag number
        OverallStats.WordsNr = OverallStats.TokensNr - OverallStats.EmosNr - OverallStats.TagsNr # overall count of words, url's and @names in the file

        data1 = tablib.Dataset()
        data1.headers = ('OverallStats.TokensNr', 'OverallStats.EmosNr', 'OverallStats.TagsNr', 'OverallStats.WordsN', 'key_word')
        data1.append((OverallStats.TokensNr, OverallStats.EmosNr, OverallStats.TagsNr, OverallStats.WordsNr, fname))

        data2 = tablib.Dataset()
        data2.headers = ('common_token_names', 'common_token_count', 'key_word')
        for lines in common_tokens:
            data2.append((lines[0], lines[1], fname))

        data3 = tablib.Dataset()
        data3.headers = ('common_emos', 'common_emos_count', 'key_word')
        for lines in common_emos:
            data3.append((lines[0], lines[1], fname))

        data4 = tablib.Dataset()
        data4.headers = ('common_hashes', 'common_hashes_count', 'key_word')
        for lines in common_hashes:
            data4.append((lines[0], lines[1], fname))

        book = tablib.Databook((data, data1, data2, data3, data4))

    with open(fname+'fullStat.xlsx', 'wb') as f:
        f.write(book.xlsx)

    print(fname, "sucessfully processed and printed to: ", fname+'fullStat.xlsx')


def summary2onexls(fnamesList, fname):
    data = tablib.Dataset()
    data.headers = (
        'id', 'created_at', 'followers', 'friends', 'statuses', 'created', 'location', 'text', 'key_word',
        'post_lenght',
        'token_count', 'word_count', 'emo_count', 'hash_count')
    data1 = tablib.Dataset()
    data1.headers = (
    'OverallStats.TokensNr', 'OverallStats.EmosNr', 'OverallStats.TagsNr', 'OverallStats.WordsN', 'key_word')
    data2 = tablib.Dataset()
    data2.headers = ('common_token_names', 'common_token_count', 'key_word')
    data3 = tablib.Dataset()
    data3.headers = ('common_emos', 'common_emos_count', 'key_word')
    data4 = tablib.Dataset()
    data4.headers = ('common_hashes', 'common_hashes_count', 'key_word')

    for fname in fnamesList:
        with open(fname, 'r') as f:
            count_all = Counter()
            count_emots_n_emoji = Counter()
            count_hashes = Counter()
            FileStats = []
            PostsNumber = 0

            for line in f:
                FileStats.append(Quantizer())
                tweet = json.loads(line)

                keys = tweet.keys();
                if 'text' in tweet:
                    textField = tweet['text'];
                else:
                    continue;
                PostLength = len(textField)  # length of the tweet in singns
                tokens = preprocess(textField)
                count_all.update(tokens)

                TokensCount = sum(1 for _ in tokens)  # number of tokens in a tweet

                HashTokens = [token for token in tokens if Hash_re.match(token)]  # recognize tokens which are hashtags
                count_hashes.update(HashTokens)
                HashCount = sum(1 for _ in HashTokens)  # number of hashtags in a tweet

                EmoTokens = [token for token in tokens if Emots_re.match(token)]  # recognize tokens which are emoji
                count_emots_n_emoji.update(EmoTokens)
                EmoCount = sum(1 for _ in EmoTokens)  # number of emoji in a tweet

                WordCount = TokensCount - HashCount - EmoCount  # number of words, url's and @names in a tweet (sum)

                FileStats[PostsNumber].PostLen = PostLength
                FileStats[PostsNumber].TokensNr = TokensCount
                FileStats[PostsNumber].WordsNr = WordCount
                FileStats[PostsNumber].EmosNr = EmoCount
                FileStats[PostsNumber].TagsNr = HashCount
                PostsNumber += 1

                # date conversion
                ts = time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                ts_user = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                # save processed tweets to file, tweet by tweet
                data.append((tweet['id'], ts, tweet['user']['followers_count'], tweet['user']['friends_count'],
                             tweet['user']['statuses_count'], ts_user, tweet['user']['location'], tweet['text'], fname,
                             PostLength, TokensCount, WordCount, EmoCount, HashCount))

            common_tokens = count_all.most_common()  #  most popular tokens in the file, string - number pair
            common_emos = count_emots_n_emoji.most_common()  # most popular emoticons and emoji in the file, string - number pair
            common_hashes = count_hashes.most_common()  # most popular hashtags in the file, string - number pair

            OverallStats = Quantizer  # values() or most_common() functions generate tables that are easier to handle for debugging
            OverallStats.TokensNr = sum(count_all.values())          # overall in file token number
            OverallStats.EmosNr = sum(count_emots_n_emoji.values())  # overall in file emoji+emoticon number
            OverallStats.TagsNr = sum(count_hashes.values())         # overall in file hashtag number
            OverallStats.WordsNr = OverallStats.TokensNr - OverallStats.EmosNr - OverallStats.TagsNr  # overall count of words, url's and @names in the file

            data1.append((OverallStats.TokensNr, OverallStats.EmosNr, OverallStats.TagsNr, OverallStats.WordsNr, fname))

            for lines in common_tokens:
                data2.append((lines[0], lines[1], fname))

            for lines in common_emos:
                data3.append((lines[0], lines[1], fname))

            for lines in common_hashes:
                data4.append((lines[0], lines[1], fname))

            print(fname, "sucessfully processed")

    book = tablib.Databook((data, data1, data2, data3, data4))

    with open(fname + '_all.xlsx', 'wb') as f:
        f.write(book.xlsx)

    print("sucessfully processed files from the current folder and printed to: ", fname + '_all.xlsx')