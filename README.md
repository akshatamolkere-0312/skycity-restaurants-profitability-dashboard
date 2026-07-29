# Cost Structure and Channel-Wise Profitability Analysis for Multi-Channel Restaurants

Interactive Streamlit dashboard analyzing net profitability across In-Store, Uber Eats,
DoorDash, and Self-Delivery channels for a portfolio of Auckland restaurants — built for
the SkyCity Auckland Restaurants & Bars project (Unified Mentor).

## What it does

- **Channel-wise profit comparison** — net margin and net profit per order by channel
- **Cost waterfall charts** — visualizes how revenue is eroded by COGS, OPEX, commission, and delivery cost per channel
- **Cuisine & segment heatmaps** — margin comparison across cuisine type and Cafe/QSR segment
- **Commission & delivery cost sliders** — live what-if recalculation of aggregator and self-delivery profitability
- **Risk view** — margin volatility and share of restaurants operating at a loss, per channel

## Project background

See the accompanying research paper (`Cost_Structure_Channel_Profitability_Research_Paper.docx`)
for full methodology, objectives, and findings. In short: modern restaurants sell through
in-store, aggregator, and self-delivery channels that carry very different cost structures.
High order volume does not guarantee profitability — this project quantifies exactly where
margin is being made or lost, channel by channel.

## Data

`restaurant_channel_data.csv` — 260 restaurants across Auckland subregions, cuisine types,
and business segments, with order counts, revenue, and cost-rate parameters for all four
channels. Generated to match the exact schema and value ranges specified in the project brief.
Swap in a production dataset with the same column names to reproduce this dashboard on live data.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud — free)

1. Push this repo to GitHub (public).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, select this repo, branch `main`, main file path `app.py`.
4. Click **Deploy**. The app builds automatically from `requirements.txt`.
5. Copy the resulting `https://<app-name>.streamlit.app` URL — that's your **Deployed project link**.

## Repo structure

```
.
├── app.py                       # Streamlit dashboard
├── requirements.txt             # Python dependencies
├── restaurant_channel_data.csv  # Dataset
└── README.md
```
