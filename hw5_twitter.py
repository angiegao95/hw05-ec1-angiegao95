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

#GET AUTHORIZATION INFORMATION
consumer_key = secret_data.CONSUMER_KEY
consumer_secret = secret_data.CONSUMER_SECRET
access_token = secret_data.ACCESS_KEY
access_secret = secret_data.ACCESS_SECRET

url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
requests.get(url, auth=auth)


#CACHING
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


#Code for Part 2:Analyze Tweets
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

def get_user_tokens(username, tweets_data):
    print('Anayzing the words from @' + username + '...')
    tweet_tokens = tokenize_tweets(tweets_data)
    tweet_tokens_cleared = remove_unrelated_words(tweet_tokens)
    print('Analysis ends.')
    print('-------------------------------------------')
    return tweet_tokens_cleared

def compare_word_lists(word_list1, word_list2):
    word_list1_diff = []
    word_list2_diff = []
    for word in word_list1:
        if word not in word_list2:
            while word in word_list1:
                word_list1_diff.append(word)
                word_list1.remove(word)

    for word in word_list2:
        if word not in word_list1:
            while word in word_list2:
                word_list2_diff.append(word)
                word_list2.remove(word)

    words_in_common = word_list1 + word_list2
    compare_results = {'list1_unique_words': word_list1_diff, 'list2_unique_words': word_list2_diff, 'common_words': words_in_common}
    return compare_results

def print_results(username1, username2, user1_top5_unique, user2_top5_unique, top5_common):
    print('ANALYSIS RESULTS:')
    user1_str = '5 MOST FREQUENT UNIQUE WORDS OF @' + username1 + ': '
    for word in user1_top5_unique:
        user1_str += word[0] + '(' + str(word[1]) + ') '

    user2_str = '5 MOST FREQUENT UNIQUE WORDS OF @' + username2 + ': '
    for word in user2_top5_unique:
        user2_str += word[0] + '(' + str(word[1]) + ') '

    common_str = '5 MOST FREQUENT WORDS IN COMMON:'
    for word in top5_common:
        common_str += word[0] + '(' + str(word[1]) + ') '

    print(user1_str)
    print(user2_str)
    print(common_str)

#USER INPUT
username1 = input('PLEASE ENTER THE 1ST TWITTER USERNAME:')
username2 = input('PLEASE ENTER THE 2ND TWITTER USERNAME:')
num_tweets = input('PLEASE ENTER THE NUMBER OF TWEETS THAT YOU WANT TO ANALYZE:')
print('-------------------------------------------')

twitter_timeline_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
params_user1 = {'screen_name':username1, 'count':num_tweets}
params_user2 = {'screen_name':username2, 'count':num_tweets}
print('Trying to get tweets from @' + username1 + '...')
tweets_data_user1 = make_request_using_cache(twitter_timeline_url,params_user1,auth)
tweet_tokens_user1 = get_user_tokens(username1, tweets_data_user1)

print('Trying to get tweets from @' + username2 + '...')
tweets_data_user2 = make_request_using_cache(twitter_timeline_url,params_user2,auth)
tweet_tokens_user2 = get_user_tokens(username2, tweets_data_user2)

compare_results = compare_word_lists(tweet_tokens_user1, tweet_tokens_user2)
user1_top5_unique = find_top5_words(compare_results['list1_unique_words'])
user2_top5_unique = find_top5_words(compare_results['list2_unique_words'])
top5_common = find_top5_words(compare_results['common_words'])

print_results(username1, username2, user1_top5_unique, user2_top5_unique, top5_common)


if __name__ == "__main__":
    if not consumer_key or not consumer_secret:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not access_token or not access_secret:
        print("You need to fill in this API's specific OAuth URLs in this file.")
        exit()
