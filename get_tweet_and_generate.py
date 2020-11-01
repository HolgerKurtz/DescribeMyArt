import tweepy
import json
import pandas as pd 
import sys
from translate import Translator
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '4' 

twitter_credential_path = 'twitter_creds.json'
with open(twitter_credential_path, "r") as json_file:
    twitter_creds = json.load(json_file)

# Daten aus der JSON Datei
CONSUMER_KEY = twitter_creds["consumer_key"]
CONSUMER_SECRET = twitter_creds["consumer_secret"]
ACCESS_KEY = twitter_creds["access_key"]
ACCESS_SECRET = twitter_creds["access_secret"]

# Authentifizierung
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(
    auth, 
    wait_on_rate_limit=True, 
    wait_on_rate_limit_notify=True
    )

hashtag = '#DescribeMyArt'
hashtag2 = '#describemyart'

tweets_dict = {}
# Sucht Tweets zum Trending Topic
def get_tweets():
    tweets = tweepy.Cursor(
        api.search,
        q= hashtag + "-filter:retweets -from:DescribeMyArt",
        result_type = 'recent' # 'popular', 'mixed' oder 'recent'
        ).items(1) # 1 da nur das neueste genutzt wird # später vieleicht 5 auf einmal erstellen

    for tweet in tweets:
        tweets_dict['index'] = [0]
        tweets_dict['user'] = tweet.user.screen_name
        tweets_dict['tweet'] = tweet.text
        tweets_dict['date'] = str(tweet.created_at)[0:20] 
get_tweets()

def db_check():
    db = pd.read_csv("db.csv").to_dict()
    if tweets_dict['date'] == str(db['date'][0]):
        print ('Tweet ist bereits getwittert', flush=True)
        print (db['date'][0], flush=True)
        print (tweets_dict['date'], flush=True)
        sys.exit()
    else:
        print (db['date'][0], flush=True)
        print (tweets_dict['date'], flush=True)
        df = pd.DataFrame.from_dict(tweets_dict)
        print(df, flush=True)
        df.to_csv("db.csv")
        print ('Ein neuer Tweet in db.csv – es geht los', flush=True)
db_check()

# Bearbeiten des Titels und uebersetzung
tweet_ohne_hashtag_de = tweets_dict['tweet'].replace(hashtag,'').replace(hashtag2,'').rstrip("\n")
translator = Translator(from_lang="de", to_lang="en")
tweet_ohne_hashtag = translator.translate(tweet_ohne_hashtag_de)

# GPT2 PART
prefix = '===' + tweet_ohne_hashtag + '==='
import gpt_2_simple as gpt2
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)
text = gpt2.generate(
    sess,
    length=50,
    prefix=prefix,
    return_as_list=True
    )[0]

split_text = text.split("\n\n")
tweet_lang = split_text[0].replace('===','')

# Filter out all examples which are longer than 260 characters
if len(tweet_lang) >= 260:
    k = 0
    tweet_geteilt = tweet_lang.split('.')
    tweet_final_liste = []
    while sum(len(i) for i in tweet_final_liste) +  len(tweet_geteilt[k]) <= 260:
        tweet = tweet_geteilt[k]
        tweet_final_liste.append(tweet)
        k += 1
else:
    tweet_final_liste = [tweet_lang]

# Bestandteile Tweet
user = '@' + str(tweets_dict['user'])

# Fertiger Tweet
new_tweet = user + '\n' + '.'.join(tweet_final_liste)
api.update_status(new_tweet[0:280])