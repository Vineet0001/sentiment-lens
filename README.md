# Sentiment Lens 📊

An interactive Natural Language Processing (NLP) web dashboard that evaluates public opinion, brand perception, and topic sentiment from live X (formerly Twitter) streams and offline CSV datasets.

---

## 📸 Visual Dashboard Proof

### 1. Sentiment Split & Polarity Distribution
Real-time breakdown of sentiment proportions (Positive / Neutral / Negative) alongside mathematical polarity score distributions (-1.0 to +1.0).

![Dashboard Overview](dashboard_overview.png)

### 2. Strongest Polarized Tweets
Instant surface analysis of the most positive and most negative expressions detected across the dataset.

![Strongest Tweets](strongest_tweets.png)

### 3. Recurring Keyword Frequency Analysis
Normalized term-frequency extraction filtering out domain noise to isolate key drivers behind positive and negative feedback.

![Keyword Frequency](keyword_frequency.png)

---

## 🚀 Key Features

* **Dual-Ingestion Architecture:**
  * **Live X Streaming:** Authenticates directly with the X API v2 via Tweepy using user-supplied Bearer Tokens or environment variables.
  * **Offline Batch Ingestion:** Ingests local CSV datasets with automated UTF-8 BOM (`\ufeff`) sanitization and flexible column mapping (`text` or `tweet`).
* **Text Preprocessing & Sanitization Pipeline:** 
  * Regex-driven cleaning engine removing URLs, mentions (`@user`), hashtags, retweet tags, and non-ASCII artifacts.
* **Lexicon-Based Sentiment Engine:**
  * Powered by TextBlob to extract semantic polarity scores.
  * Employs an adjustable neutral-band threshold (`[-0.05, +0.05]`) to prevent ambiguous texts from skewing metrics.
* **Interactive Data Visualizations:**
  * Dynamic Plotly donut charts rendering percentage splits.
  * Polarity frequency histograms capturing emotional distribution.
  * Horizontal bar charts ranking top recurring terms per sentiment class.
* **CSV Export:** Download sanitized and analyzed results with assigned polarity scores directly from the interface.

---

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Frontend UI** | Streamlit |
| **Data Manipulation** | Pandas, Collections, Regex (`re`) |
| **NLP & Scoring** | TextBlob |
| **Data Visualization** | Plotly Express |
| **API Integration** | Tweepy (X API v2) |

---

## 📁 Repository Structure

```text
sentiment-lens/
├── app.py                      # Streamlit frontend & UI routing
├── sentiment_core.py           # Preprocessing, TextBlob scoring & Tweepy logic
├── requirements.txt            # Python dependencies
├── sample_tweets.csv           # Initial lightweight test dataset
├── tweets_sentiment_dataset.CSV # 600-record comprehensive test dataset
├── .gitignore                  # Git ignore rules (virtual environment, cache)
└── README.md                   # Project documentation & visual architecture
