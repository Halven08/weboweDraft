# Print most common words in a corpus collected from Twitter
#
# Full description:
# http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/
# http://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/
# http://marcobonzanini.com/2015/03/17/mining-twitter-data-with-python-part-3-term-frequencies/
#
# Run:
# python twitter_most_common_words.py <filename.jsonl>

import sys
#import statistics
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
    # do zliczania emotikon tyle wystarczy tyle
    # jeśli potrzebujemy hashtagów, długości posta itd. Jeśli tylko emotki, to zakomentować do końca struktury
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
]

tokens_re =  re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE )
emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

#NotEmots_str=regex_str
#NotEmots_str.remove(xd_str)
#NotEmots_str.remove(emoticons_str)
#NotEmots_str.remove(emoticons_str)
#NotEmots_str.remove(r"[\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF]")
#NotEmots_re =  re.compile(r'(' + '|'.join(NotEmots_str) + ')', re.VERBOSE | re.IGNORECASE )

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


def summary2onexls(fnamesList, fname):
    #fnamesList = glob.glob('*.json')
    #fname='raw_car2.json'; #EDYTOWAĆ JAK NAJBARDZIEJ
    data = tablib.Dataset()
    data.headers = (
    'id', 'created_at', 'followers', 'friends', 'statuses', 'created', 'location', 'text', 'key_word', 'post_lenght',
    'token_count', 'word_count', 'emo_count', 'hash_count')
    data1 = tablib.Dataset()
    data1.headers = ('OverallStats.TokensNr', 'OverallStats.EmosNr', 'OverallStats.TagsNr', 'OverallStats.WordsN', 'key_word')
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
            FileStats=[]
            PostsNumber=0

            for line in f:
                FileStats.append(Quantizer())
                tweet = json.loads(line)

                keys = tweet.keys();
                if 'text' in tweet:
                    textField = tweet['text'];
                else:
                    continue;
                PostLength=len(textField) # długość tweeta w znakach
                tokens = preprocess(textField)
                count_all.update(tokens)
                #print(tokens)
                TokensCount = sum(1 for _ in tokens) # ilość tokenów ogółem w tweecie
                # tokens_nostopwords = [term for term in tokens if term not in stop] # tu było ongi usuwanie spójników

                # EmojiAddr=re.findall(r"[\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF]", tweet['text'], re.UNICODE)
                # EmojiCount = sum(1 for _ in EmojiAddr) # To zlicza same emoji bez emotek
                # NotEmAddr = re.finditer (NotEmots_re,textField); # zliczenie nie-emoji i nie-emotikon
                # NotEmCount = sum(1 for _ in NotEmAddr)  # Ten cały blok kodu jest zbyteczny
                # TokensAddr = tokens_re.finditer (textField) # Ten cały blok kodu jest zbyteczny
                # TokensCount = sum(1 for _ in TokensAddr) # Ten cały blok kodu jest zbyteczny

                HashTokens=[token for token in tokens if Hash_re.match(token)] # wychwyć tokeny, które są hashtagami
                count_hashes.update(HashTokens)
                HashCount=sum(1 for _ in HashTokens) # ilość hashtagów w tweecie

                EmoTokens=[token for token in tokens if Emots_re.match(token)] # wychwyć tokeny, które są emotami
                count_emots_n_emoji.update(EmoTokens)
                EmoCount = sum(1 for _ in EmoTokens) # ilość emotek w tweecie

                WordCount = TokensCount - HashCount - EmoCount # ilość słów, linków i @-odnośników (suma) w tweecie

                #print(EmoTokens, EmoCount,HashTokens, HashCount) # wartości chwilowe w danej pętli

                FileStats[PostsNumber].PostLen=PostLength
                FileStats[PostsNumber].TokensNr=TokensCount
                FileStats[PostsNumber].WordsNr = WordCount
                FileStats[PostsNumber].EmosNr = EmoCount
                FileStats[PostsNumber].TagsNr = HashCount
                PostsNumber+=1

                ## date conversion
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                ts_user = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
                ## save to file
                data.append((tweet['id'], ts, tweet['user']['followers_count'], tweet['user']['friends_count'], tweet['user']['statuses_count'], ts_user, tweet['user']['location'], tweet['text'], fname, PostLength, TokensCount, WordCount, EmoCount, HashCount))

            # dane które uzyskałeś w pętli

            common_tokens = count_all.most_common() # najpopularniejsze wyrażenia ogólnie w pliku, pary string-ilość
            common_emos = count_emots_n_emoji.most_common() # najpopularniejsze emoty i emoji w pliku, pary string-ilość
            common_hashes = count_hashes.most_common() # najpopularniejsze hashe w pliku, pary string-ilość


            OverallStats = Quantizer # funkcje values(), most_common() generują fajniejsze tablice niż ten zapis niżej
            OverallStats.TokensNr = sum(count_all.values()) # tyle jest w pliku ogółem tokenów
            OverallStats.EmosNr = sum(count_emots_n_emoji.values()) # tyle jest w pliku emoji+emotikon
            OverallStats.TagsNr = sum(count_hashes.values()) # tyle jest w pliku hashtagów
            OverallStats.WordsNr = OverallStats.TokensNr - OverallStats.EmosNr - OverallStats.TagsNr # tyle jest w pliku słów, linków i @-odnośników zbiorczo
            for stat in FileStats:
                OverallStats.PostLen += stat.PostLen
            #print()

            #MeanTokensInPost = sum(count_all.values()) / PostsNumber # średnia ilość tokenów w poście
            #MeanCharsInPost = OverallStats.PostLen / PostsNumber # średnia ilość znaków w poście
            #... itd.

            #for stat in FileStats:
                #stat.PostLen,stat.TokensNr,stat.WordsNr,stat.EmosNr,stat.TagsNr #odwołania do kolejnych pól struktury żeby wyciągać z niej rzeczy.
                # Unikać tego zapisu jak psa, ale może być ewentualnie przydatny...
                # Skype do mnie jacek_ld jakby coś nie szło


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

