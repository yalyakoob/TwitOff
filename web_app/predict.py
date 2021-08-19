import numpy as np
from sklearn.linear_model import LogisticRegression
from web_app.models import User
import spacy


def predict_user(user1_name, user2_name, tweet_text, cache=None):
    """Predict which user is most likely to tweet a particular tweet"""
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
    user1_labels = np.zeros(len(user1.tweets))
    user2_labels = np.ones(len(user2.tweets))
    embeddings_1 = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([user1_labels, user2_labels])
    log_reg = LogisticRegression(solver='lbfgs', max_iter=1000)
    log_reg.fit(embeddings_1, labels)
    nlp = spacy.load('en')
    tweet_embedding = nlp(tweet_text).vector
    return log_reg.predict(np.array([tweet_embedding]).reshape(1,-1))
