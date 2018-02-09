from requests_oauthlib import OAuth1
import json
import sys
import requests
import secret_data # file that contains OAuth credentials
import nltk # uncomment line after you install nltk

from collections import Counter

## SI 206 - HW
## COMMENT WITH:
## Your section day/time: Monday 4:00-5:30pm
## Any names of people you worked with on this assignment:

#usage should be python3 hw5_twitter.py <username> <num_tweets>
username = sys.argv[1]
num_tweets = sys.argv[2]

consumer_key = secret_data.CONSUMER_KEY
consumer_secret = secret_data.CONSUMER_SECRET
access_token = secret_data.ACCESS_KEY
access_secret = secret_data.ACCESS_SECRET

#Code for OAuth starts
url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
requests.get(url, auth=auth)
#Code for OAuth ends

#Write your code below:
#Code for Part 3:Caching
#Finish parts 1 and 2 and then come back to this
CACHE_FNAME = 'tweet_cache_file.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params, auth):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        print("Fetching cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params=params, auth=auth)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


#Code for Part 1:Get Tweets
twitter_timeline_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
params = {'screen_name':username, 'count':num_tweets}
# tweets_data = requests.get(twitter_timeline_url, params=params, auth=auth)
tweets_data = make_request_using_cache(twitter_timeline_url,params,auth)

#Code for Part 2:Analyze Tweets

def reformat_tweet_json(tweets_caught):
    tweets_formatted = json.dumps(tweets_caught,indent=2, sort_keys=True)
    with open('tweets.json','w') as file_to_write:
        file_to_write.write(tweets_formatted)

#reformat_tweet_json(tweets_data)

def tokenize_tweets(tweets_caught):
    tweet_tokens = []
    for tweet in tweets_caught:
        tweet_tokens += nltk.word_tokenize(tweet['text'])
    return tweet_tokens

def remove_unrelated_words(tweet_tokens):
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    words_to_ignore = ['http','https','RT']
    tweet_tokens_cleared = []
    for word in tweet_tokens:
        word_lower = word.lower()
        if word_lower[0] in alphabet:
            if word not in words_to_ignore:
                tweet_tokens_cleared.append(word)
    return tweet_tokens_cleared

def find_top5_words(tweet_tokens_cleared):
    tweet_tokens_freq = Counter(tweet_tokens_cleared)
    top5_words = tweet_tokens_freq.most_common(5)
    return top5_words

def print_results(username,num_tweets,top5_words):
    print('USER:',username)
    print('TWEETS ANALYZED:', num_tweets)
    common_words_str = '5 MOST FREQUENT WORDS: '
    for common_word in top5_words:
        common_words_str += common_word[0] + '(' + str(common_word[1]) + ') '
    print(common_words_str)


tweet_tokens = tokenize_tweets(tweets_data)
tweet_tokens_cleared = remove_unrelated_words(tweet_tokens)
top5_words = find_top5_words(tweet_tokens_cleared)
print_results(username,num_tweets,top5_words)

if __name__ == "__main__":
    if not consumer_key or not consumer_secret:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not access_token or not access_secret:
        print("You need to fill in this API's specific OAuth URLs in this file.")
        exit()
