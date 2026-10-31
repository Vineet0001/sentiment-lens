"""Core logic for Sentiment Lens: fetch tweets, clean them, score them with TextBlob."""
import os
import re
from collections import Counter

import pandas as pd
import tweepy
from textblob import TextBlob

# Polarity within +/- this value is treated as neutral instead of positive/negative.
NEUTRAL_BAND = 0.05

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "you", "are", "was", "but", "not",
    "have", "has", "had", "its", "it's", "just", "from", "they", "their", "what",
    "when", "who", "how", "all", "can", "will", "about", "your", "out", "get",
    "got", "one", "like", "would", "there", "been", "more", "than", "then", "them",
    "his", "her", "she", "him", "our", "too", "very", "also", "into", "over",
    "some", "any", "now", "why", "did", "does", "don", "don't", "i'm", "it", "is",
    "of", "to", "in", "on", "at", "be", "as", "so", "if", "we", "my", "me", "an",
    "or", "by", "do", "no", "up", "rt", "amp",
}


def clean_tweet(text: str) -> str:
    """Strip retweet markers, URLs, mentions and special characters."""
    text = re.sub(r"^RT\s+", "", text)
    text = re.sub(r"(@[A-Za-z0-9_]+)|(\w+://\S+)", " ", text)
    text = re.sub(r"[^0-9A-Za-z\s']", " ", text)
    return " ".join(text.split())


def label_sentiment(polarity: float) -> str:
    if polarity > NEUTRAL_BAND:
        return "positive"
    if polarity < -NEUTRAL_BAND:
        return "negative"
    return "neutral"


def analyze_texts(texts) -> pd.DataFrame:
    """Score a list of raw tweets. Returns one row per tweet."""
    rows = []
    for raw in texts:
        cleaned = clean_tweet(raw)
        if not cleaned:
            continue
        polarity = TextBlob(cleaned).sentiment.polarity
        rows.append(
            {
                "tweet": raw,
                "cleaned": cleaned,
                "polarity": round(polarity, 3),
                "sentiment": label_sentiment(polarity),
            }
        )
    return pd.DataFrame(rows, columns=["tweet", "cleaned", "polarity", "sentiment"])


def fetch_tweets(query: str, max_results: int = 50, bearer_token: str | None = None):
    """Fetch recent English tweets (no retweets) for a keyword via the X v2 API."""
    token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        raise RuntimeError(
            "No X API token found. Set the TWITTER_BEARER_TOKEN environment variable, "
            "or use the CSV upload option."
        )
    client = tweepy.Client(bearer_token=token)
    response = client.search_recent_tweets(
        query=f"{query} -is:retweet lang:en",
        max_results=max(10, min(max_results, 100)),
    )
    return [t.text for t in (response.data or [])]


def top_words(df: pd.DataFrame, sentiment: str, n: int = 8, exclude=()):
    """Most common meaningful words among tweets with the given sentiment."""
    text = " ".join(df.loc[df["sentiment"] == sentiment, "cleaned"]).lower()
    skip = STOPWORDS | set(exclude)
    words = [w for w in text.split() if len(w) > 2 and w not in skip]
    return Counter(words).most_common(n)