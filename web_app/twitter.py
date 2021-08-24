"""Retrieve Tweets and users then create embeddings and populate DB"""
from os import getenv

import tweepy
import spacy
from web_app.models import DB, Tweet, User





TWITTER_API_KEY = 'lvZgIbYSaKPDWQ9VaMtUeMKID'
TWITTER_API_KEY_SECRET = 'GYGVjh4WxzOfo0S3fVLKsmhdz0VyavrImOe00WLT3hJx1EA8IN'
TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)


# user = 'nasa'
# twitter_user = twitter.get_user(user)
# twitter_user.screen_name
# tweets = twitter_user.timeline(count = 200, exclude_replies = True, include_rts = False, tweet_mode = 'Extended')
# tweets[0].text #most recent tweet_
# tweets[0].retweet_count
def add_or_update_user(username):
    """Add or update a user and their Tweets, error if not a Twitter user."""
    twitter_user = TWITTER.get_user(username)
    db_user = (User.query.get(twitter_user.id)) or User(
        id=twitter_user.id, name=username)
    DB.session.add(db_user)
    tweets = twitter_user.timeline(
        count=200, exclude_replies=True, include_rts=False,
        tweet_mode='extended', since_id=db_user.newest_tweet_id
    )

    # db_user = (User.query.get(twitter_user.id)) or User(
    #     id=twitter_user.id, name=username, newest_tweet_id = )
    # DB.session.add(db_user)

    if tweets:
        db_user.newest_tweet_id = tweets[0].id
    for tweet in tweets:
        nlp = spacy.load('en')
        # nlp = spacy.load(en_core_web_sm)
        embeddings = nlp(tweet.full_text).vector
        db_tweet = Tweet(id=tweet.id, text=tweet.full_text, embedding=embeddings)
        db_user.tweets.append(db_tweet)
        #breakpoint()
        DB.session.add(db_tweet)
    DB.session.commit()


def update_all_users():
    """Update all tweets for all ysers in the user table."""
    for user in User.query.all():
        add_or_update_user(user.name)


def add_users(users):
    """Add/update a list of users for debugging database"""
    for user in users:
        add_or_update_user(user)
