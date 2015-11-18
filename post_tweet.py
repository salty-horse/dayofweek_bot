#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import random
import datetime
import tweepy
from secret import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
bad_words = set(open(ROOT_PATH + 'badwords.txt').read().splitlines())

def post_tweet():
    now = datetime.datetime.now()
    day_name = now.strftime("%A").lower()
    month_name = now.strftime("%B").lower()
    short_month_name = now.strftime("%b").lower()
    date_formats = [
        now.strftime("%m/%d/%Y"),
        now.strftime("%m/%d"),
        now.strftime("%d/%m/%Y"),
        now.strftime("%d/%m"),
    ]

    all_day_names = [
        'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 
    ]

    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.secure = True
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)

    api = tweepy.API(auth)
    query = '{0} OR {0}s since:{1}'.format(day_name, now.strftime('%Y-%m-%d'))

    good_tweets = []
    while True:
        search_results = tweepy.Cursor(api.search, q=query, lang='en').pages()
        for results_page in search_results:
            # print 'new page', 'results:', len(good_tweets)
            for result in results_page:
                if result.user.screen_name == 'easternclock':
                    continue

                text = result.text
                lower_text = text.lower()
                text_words = lower_text.split()

                # No weather reports
                if u'°' in text:
                    continue

                if any(d in text_words for d in date_formats):
                    continue

                if any(other_day in text_words for other_day in all_day_names if other_day != day_name):
                    continue

                if 'next ' + day_name in lower_text:
                    continue

                if month_name in text_words or short_month_name in text_words:
                    continue


                if 'http' in text:
                    continue
                if 'RT' in text:
                    continue
                if '@' in text:
                    continue

                if any(w in bad_words for w in text_words):
                    continue

                if len(text.split()) > 15:
                    continue
                good_tweets.append(result)
                if len(good_tweets) >= 50:
                    break
            if len(good_tweets) >= 50:
                break
        if len(good_tweets) >= 50:
            break

    selected_tweet = random.choice(good_tweets)

    # Submit to Twitter
    api.retweet(selected_tweet.id)

if __name__ == '__main__':
    post_tweet()
