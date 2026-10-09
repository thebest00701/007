# JARVIS MAX — AI Creative Studio

A Streamlit app for product infographic planning, marketing copy, and creative workflows.

## Deploy with Streamlit Community Cloud

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app** and select repository `thebest00701/007`.
3. Set branch to `main` and main file path to `app.py`.
4. Deploy the app.
5. In the deployed app, open **Manage app → Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your_api_key_here"
```

Never commit API keys to this repository. The app can open without a key, but AI generation requires a valid OpenAI API key and may incur API usage charges.

## Files

- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
