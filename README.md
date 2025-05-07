# Community Notes Streamlit App

This app lets you upload, filter, and explore Community Notes data, including sentiment, language, and political/hateful flags. You can also view and download filtered results and click through to the original tweets.

## Features
- Upload your annotated CSV file (with tweetId, sentiment, language, etc.)
- Filter by language, sentiment, week, political/hateful flags, and keyword search
- Paginated table with clickable tweet links
- Download filtered results as CSV
- Visualize trends: time series, sentiment, language, top keywords

## Setup (Local)
1. Clone this repo:
   ```bash
   git clone <your-repo-url>
   cd community-notes-app
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run community_notes_streamlit_app.py
   ```

## Deploy to Streamlit Community Cloud
1. Push your code to a GitHub repo (public or private).
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and connect your repo.
3. Select `community_notes_streamlit_app.py` as the app file and deploy.
4. Share the public URL with your team!

## Notes
- If your app needs users to upload data, use the file uploader widget (already included).
- If you need to download NLTK data (like vader_lexicon), the app will do this automatically.
- For large files, use the file uploader rather than bundling data in the repo.

## Example Data
- You can use any CSV with the required columns (e.g., tweetId, noteId, summary_en, sentiment_category, detected_language, etc.).

## Troubleshooting
- If you see `ModuleNotFoundError`, add the missing package to `requirements.txt` and redeploy.
- If you see “App failed to start,” check the logs in Streamlit Cloud for details.

---
For questions or help, contact your project maintainer or open an issue in this repo.
