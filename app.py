"""Sentiment Lens: a small dashboard showing what people say about a brand, product or person on X."""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from tweepy import TweepyException

from sentiment_core import analyze_texts, fetch_tweets, top_words

COLORS = {"positive": "#2E9E5B", "neutral": "#9AA0A6", "negative": "#D64545"}
ORDER = ["positive", "neutral", "negative"]

st.set_page_config(page_title="Sentiment Lens", page_icon="📊", layout="wide")
st.title("Sentiment Lens")

# ---------- sidebar: choose a data source ----------
with st.sidebar:
    st.header("Input")
    source = st.radio("Data source", ["Live from X", "Upload CSV"])
    keyword, count, uploaded, api_key = "", 50, None, ""
    
    if source == "Live from X":
        keyword = st.text_input("Keyword, brand or name", "iPhone")
        count = st.slider("Tweets to fetch", 10, 100, 50, step=10)
        api_key = st.text_input("X Bearer Token", type="password", help="Paste your API token here.")
    else:
        uploaded = st.file_uploader("CSV with a 'text' (or 'tweet') column", type="csv")
        
    run = st.button("Analyze", type="primary")

# ---------- dynamic description ----------
if source == "Live from X":
    st.caption("What are people saying? Recent tweets are pulled live from X and scored with TextBlob.")
else:
    st.caption("Custom Analysis Mode: Processing offline text data and scoring sentiment with TextBlob.")

# ---------- run the analysis ----------
if run:
    try:
        if source == "Live from X":
            if not keyword.strip():
                st.warning("Enter a keyword first.")
                st.stop()
            if not api_key.strip() and not os.environ.get("TWITTER_BEARER_TOKEN"):
                st.warning("Please enter your X Bearer Token in the sidebar.")
                st.stop()
                
            with st.spinner("Fetching tweets..."):
                texts = fetch_tweets(
                    keyword.strip(), 
                    max_results=count, 
                    bearer_token=api_key.strip() if api_key.strip() else None
                )
            label = keyword.strip()
        else:
            if uploaded is None:
                st.warning("Upload a CSV first.")
                st.stop()
            
            csv_df = pd.read_csv(uploaded)
            # Clean invisible BOM characters, whitespace, and normalize to lowercase
            csv_df.columns = csv_df.columns.str.strip().str.replace("\ufeff", "").str.lower()
            column = "text" if "text" in csv_df.columns else "tweet"  # 'tweet' = this app's own export
            texts = csv_df[column].dropna().astype(str).tolist()
            label = uploaded.name
            
        st.session_state["df"] = analyze_texts(texts)
        st.session_state["label"] = label
    except RuntimeError as e:
        st.error(str(e))
        st.stop()
    except TweepyException as e:
        st.error(f"X API error: {e}")
        st.stop()
    except KeyError:
        st.error("The CSV needs a column named 'text' or 'tweet'.")
        st.stop()

df = st.session_state.get("df")
label = st.session_state.get("label", "")

if df is None:
    st.info("Choose a data source in the sidebar and press Analyze.")
    st.stop()
if df.empty:
    st.warning("No usable tweets came back for that input.")
    st.stop()

# ---------- headline numbers ----------
counts = df["sentiment"].value_counts().reindex(ORDER, fill_value=0)
pct = (counts / len(df) * 100).round(1)

st.subheader(f"Results for: {label}  ·  {len(df)} tweets")
m1, m2, m3 = st.columns(3)
m1.metric("Positive", f"{pct['positive']}%")
m2.metric("Neutral", f"{pct['neutral']}%")
m3.metric("Negative", f"{pct['negative']}%")

# ---------- charts ----------
left, right = st.columns(2)
with left:
    donut = px.pie(
        names=counts.index,
        values=counts.values,
        hole=0.55,
        color=counts.index,
        color_discrete_map=COLORS,
        title="Sentiment split",
    )
    donut.update_layout(margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(donut, use_container_width=True, key="donut")
with right:
    hist = px.histogram(
        df,
        x="polarity",
        nbins=20,
        range_x=[-1, 1],
        color_discrete_sequence=["#4C78A8"],
        title="Polarity distribution (-1 negative, +1 positive)",
    )
    hist.update_layout(margin=dict(t=50, b=10, l=10, r=10), yaxis_title="Tweets")
    st.plotly_chart(hist, use_container_width=True, key="hist")

# ---------- strongest tweets ----------
st.subheader("Strongest tweets")
a, b = st.columns(2)
a.markdown("**Most positive**")
for tweet in df.nlargest(5, "polarity")["tweet"]:
    a.write(f"• {tweet}")
b.markdown("**Most negative**")
for tweet in df.nsmallest(5, "polarity")["tweet"]:
    b.write(f"• {tweet}")

# ---------- common words ----------
st.subheader("What keeps coming up")
exclude = set(str(label).lower().split())
w1, w2 = st.columns(2)
for col, sentiment in ((w1, "positive"), (w2, "negative")):
    words = top_words(df, sentiment, exclude=exclude)
    if not words:
        col.caption(f"Not enough {sentiment} tweets to show common words.")
        continue
    wdf = pd.DataFrame(words, columns=["word", "count"]).iloc[::-1]
    fig = px.bar(
        wdf,
        x="count",
        y="word",
        orientation="h",
        color_discrete_sequence=[COLORS[sentiment]],
        title=f"Common words in {sentiment} tweets",
    )
    fig.update_layout(margin=dict(t=50, b=10, l=10, r=10), yaxis_title="")
    col.plotly_chart(fig, use_container_width=True, key=f"words_{sentiment}")

# ---------- export + caveat ----------
st.download_button(
    "Download results (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name="sentiment_results.csv",
    mime="text/csv",
)
st.caption(
    "TextBlob is a rule-based scorer. It misreads sarcasm and slang, "
    "so treat the percentages as a rough signal, not a measurement."
)