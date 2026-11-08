# Crew Image Scraper

Experiments with [CrewAI](https://crewai.com) agents (powered by Groq LLMs) that find and download images from the web.

## Scripts

| File | What it does |
|---|---|
| `crew_image_downloader.py` | Single agent that downloads every `<img>` from a target URL using raw HTML + regex. Saves to `downloaded_images/`. |
| `scrape.py` | Two-agent crew: one searches for websites about a topic, the other downloads images from them (BeautifulSoup). Saves to `downloaded_images/<topic>/`. |
| `docs/notes.txt` | Notes on CrewAI processes and agent attributes. |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your Groq API key
```

## Run

```bash
python crew_image_downloader.py
python scrape.py
```

Change `TARGET_URL` in `crew_image_downloader.py` or the `topic` input at the bottom of `scrape.py` to scrape something else.
