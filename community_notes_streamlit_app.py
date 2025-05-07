import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(layout="wide")
st.title('Community Notes Explorer')

uploaded_file = st.file_uploader("Upload your annotated notes CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())

    # Parse dates
    if 'createdAtMillis' in df.columns:
        # Remove commas and ensure numeric
        df['createdAtMillis'] = pd.to_numeric(df['createdAtMillis'], errors='coerce')
        df['createdAtMillis'] = pd.to_datetime(df['createdAtMillis'], unit='ms', errors='coerce')
        df['week'] = df['createdAtMillis'].dt.to_period('W').apply(lambda r: r.start_time)
    else:
        st.warning("No 'createdAtMillis' column found. Time series plots will be unavailable.")

    # Sidebar filters
    indian_langs = ['hi', 'ta', 'ur', 'mr']
    language_options = ['All', 'India (hi+ta+ur+mr)'] + sorted(df['detected_language'].dropna().unique().tolist()) if 'detected_language' in df.columns else ['All']
    sentiment_options = ['All', 'positive', 'neutral', 'negative'] if 'sentiment_category' in df.columns else ['All']
    week_options = ['All'] + sorted(df['week'].dropna().unique().astype(str).tolist()) if 'week' in df.columns else ['All']
    political_options = ['All', True, False] if 'is_political' in df.columns else ['All']
    hateful_options = ['All', True, False] if 'is_hateful' in df.columns else ['All']
    keyword_search = st.sidebar.text_input("Keyword search (in summary_en)")

    language = st.sidebar.selectbox("Language", options=language_options)
    sentiment = st.sidebar.selectbox("Sentiment", options=sentiment_options)
    week = st.sidebar.selectbox("Week", options=week_options)
    is_political = st.sidebar.selectbox("Political?", options=political_options)
    is_hateful = st.sidebar.selectbox("Hateful?", options=hateful_options)

    filtered = df.copy()
    if language == 'India (hi+ta+ur+mr)':
        filtered = filtered[filtered['detected_language'].isin(indian_langs)]
    elif language != 'All' and 'detected_language' in filtered.columns:
        filtered = filtered[filtered['detected_language'] == language]
    if sentiment != 'All' and 'sentiment_category' in filtered.columns:
        filtered = filtered[filtered['sentiment_category'] == sentiment]
    if week != 'All' and 'week' in filtered.columns:
        filtered = filtered[filtered['week'].astype(str) == week]
    if is_political != 'All' and 'is_political' in filtered.columns:
        filtered = filtered[filtered['is_political'] == is_political]
    if is_hateful != 'All' and 'is_hateful' in filtered.columns:
        filtered = filtered[filtered['is_hateful'] == is_hateful]
    if keyword_search:
        filtered = filtered[filtered['summary_en'].str.contains(keyword_search, case=False, na=False)]

    st.write(f"Filtered Notes ({len(filtered)})", filtered.head(100))

    # Download filtered results
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download filtered results as CSV", csv, "filtered_notes.csv", "text/csv")

    # Trend: Notes per week
    if 'week' in df.columns:
        st.subheader("Notes per Week")
        week_counts = df.groupby('week').size()
        fig, ax = plt.subplots(figsize=(10,4))
        week_counts.plot(ax=ax, marker='o')
        plt.xlabel('Week')
        plt.ylabel('Number of Notes')
        plt.title('Notes per Week')
        st.pyplot(fig)

    # Sentiment breakdown over time
    if 'week' in df.columns and 'sentiment_category' in df.columns:
        st.subheader("Sentiment Breakdown Over Time")
        sent_counts = df.groupby(['week', 'sentiment_category']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(10,4))
        sent_counts.plot(ax=ax, marker='o')
        plt.xlabel('Week')
        plt.ylabel('Number of Notes')
        plt.title('Sentiment Breakdown Over Time')
        st.pyplot(fig)

    # Language breakdown
    if 'detected_language' in df.columns:
        st.subheader("Language Breakdown")
        lang_counts = df['detected_language'].value_counts()
        fig, ax = plt.subplots(figsize=(8,4))
        lang_counts.plot(kind='bar', ax=ax)
        plt.xlabel('Language')
        plt.ylabel('Number of Notes')
        plt.title('Notes by Language')
        st.pyplot(fig)

    # Top keywords (if available)
    if 'political_keywords_flagged' in df.columns:
        st.subheader("Top Political Keywords (Flagged)")
        from collections import Counter
        all_keywords = []
        for kw in df['political_keywords_flagged'].dropna():
            all_keywords.extend([k.strip() for k in kw.split(',') if k.strip()])
        top_keywords = Counter(all_keywords).most_common(10)
        if top_keywords:
            keywords, counts = zip(*top_keywords)
            fig, ax = plt.subplots(figsize=(8,4))
            sns.barplot(x=list(counts), y=list(keywords), ax=ax, orient='h')
            plt.xlabel('Frequency')
            plt.title('Top 10 Political Keywords')
            st.pyplot(fig)

    # Show total filtered notes
    st.write(f"**Total filtered notes: {len(filtered)}**")
    # Pagination for filtered notes table
    page_size = 50
    total_pages = (len(filtered) - 1) // page_size + 1 if len(filtered) > 0 else 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    # Add clickable tweet links to the table
    tweet_col = 'tweetId' if 'tweetId' in filtered.columns else 'noteId' if 'noteId' in filtered.columns else None
    if tweet_col:
        filtered = filtered.copy()
        filtered['tweet_link'] = filtered[tweet_col].apply(
            lambda x: f"[{x}](https://www.x.com/i/web/status/{x})" if pd.notna(x) else ""
        )
        # Move tweet_link to the front for visibility
        cols = ['tweet_link'] + [col for col in filtered.columns if col != 'tweet_link']
        filtered = filtered[cols]
        st.markdown(filtered.iloc[start_idx:end_idx].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.write(filtered.iloc[start_idx:end_idx])
    st.write(f"Showing rows {start_idx+1} to {min(end_idx, len(filtered))} of {len(filtered)}")

    # Show total tweet links
    tweet_col = 'tweetId' if 'tweetId' in filtered.columns else 'noteId' if 'noteId' in filtered.columns else None
    if tweet_col:
        tweet_count = filtered[tweet_col].notna().sum()
        st.write(f"**Total filtered tweets with IDs: {tweet_count}**")

    # Combined Indian language count
    indian_langs = ['hi', 'ta', 'ur', 'mr']
    if 'detected_language' in df.columns:
        india_count = df[df['detected_language'].isin(indian_langs)].shape[0]
        st.write(f"**Total notes for India (hi+ta+ur+mr): {india_count}**") 