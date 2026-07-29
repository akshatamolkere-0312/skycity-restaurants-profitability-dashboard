"""
Cost Structure and Channel-Wise Profitability Analysis for Multi-Channel Restaurants
Streamlit dashboard — SkyCity Auckland Restaurants & Bars project

Run locally:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# Page config & constants
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Channel Restaurant Profitability",
    page_icon="🍽️",
    layout="wide",
)

CHANNELS = ["InStore", "UberEats", "DoorDash", "SelfDelivery"]
CHANNEL_LABELS = {"InStore": "In-Store", "UberEats": "Uber Eats",
                   "DoorDash": "DoorDash", "SelfDelivery": "Self-Delivery"}
COLORS = {"InStore": "#1a2744", "UberEats": "#EB5757", "DoorDash": "#F2994A", "SelfDelivery": "#27AE60"}

DATA_PATH = "restaurant_channel_data.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def recompute_whatif(df, commission_rate, delivery_cost):
    """Recompute aggregator and self-delivery profit/margin under user-adjusted
    commission rate and delivery cost-per-order, holding COGS/OPEX fixed."""
    out = df.copy()

    # Uber Eats
    out["UberEatsNetProfit_wi"] = out["UberEatsRevenue"] * (
        1 - out["COGSRate"] - out["OPEXRate"] - commission_rate
    )
    # DoorDash (kept at the dataset's convention of a slightly higher effective rate)
    out["DoorDashNetProfit_wi"] = out["DoorDashRevenue"] * (
        1 - out["COGSRate"] - out["OPEXRate"] - (commission_rate * 1.03)
    )
    # Self-delivery
    out["SD_DeliveryTotalCost_wi"] = out["SelfDeliveryOrdersCount"] * delivery_cost
    out["SelfDeliveryNetProfit_wi"] = (
        out["SelfDeliveryRevenue"] * (1 - out["COGSRate"] - out["OPEXRate"])
        - out["SD_DeliveryTotalCost_wi"]
    )
    out["InStoreNetProfit_wi"] = out["InStoreNetProfit"]  # unaffected by sliders

    for ch in CHANNELS:
        rev_col = f"{ch}Revenue"
        profit_col = f"{ch}NetProfit_wi"
        orders_col = f"{ch}OrdersCount"
        out[f"{ch}_MarginPct_wi"] = np.where(out[rev_col] > 0, out[profit_col] / out[rev_col] * 100, np.nan)
        out[f"{ch}_NetProfitPerOrder_wi"] = np.where(out[orders_col] > 0, out[profit_col] / out[orders_col], np.nan)

    return out


# ----------------------------------------------------------------------------
# Load & sidebar filters
# ----------------------------------------------------------------------------
df_raw = load_data()

st.sidebar.title("🍽️ Filters & What-If Controls")

st.sidebar.subheader("Channel selector")
selected_channels = st.sidebar.multiselect(
    "Channels to include", options=CHANNELS,
    default=CHANNELS, format_func=lambda c: CHANNEL_LABELS[c],
)
if not selected_channels:
    selected_channels = CHANNELS

st.sidebar.subheader("Cuisine & segment filters")
cuisine_filter = st.sidebar.multiselect(
    "Cuisine type", options=sorted(df_raw["CuisineType"].unique()),
    default=sorted(df_raw["CuisineType"].unique()),
)
segment_filter = st.sidebar.multiselect(
    "Segment", options=sorted(df_raw["Segment"].unique()),
    default=sorted(df_raw["Segment"].unique()),
)
subregion_filter = st.sidebar.multiselect(
    "Subregion", options=sorted(df_raw["Subregion"].unique()),
    default=sorted(df_raw["Subregion"].unique()),
)

st.sidebar.subheader("What-if sliders")
commission_rate = st.sidebar.slider(
    "Aggregator commission rate (%)", min_value=10.0, max_value=40.0,
    value=float(round(df_raw["CommissionRate"].mean() * 100, 1)), step=0.5,
) / 100
delivery_cost = st.sidebar.slider(
    "Self-delivery cost per order ($)", min_value=0.5, max_value=8.0,
    value=float(round(df_raw["DeliveryCostOrder"].mean(), 2)), step=0.1,
)

df = df_raw[
    df_raw["CuisineType"].isin(cuisine_filter)
    & df_raw["Segment"].isin(segment_filter)
    & df_raw["Subregion"].isin(subregion_filter)
].copy()

if df.empty:
    st.warning("No restaurants match the current filters. Adjust the filters in the sidebar.")
    st.stop()

df = recompute_whatif(df, commission_rate, delivery_cost)

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("Cost Structure & Channel-Wise Profitability Analysis")
st.caption("Multi-Channel Restaurants · SkyCity Auckland Restaurants & Bars")

total_rev = sum(df[f"{c}Revenue"].sum() for c in selected_channels)
total_profit = sum(df[f"{c}NetProfit_wi"].sum() for c in selected_channels)
blended_margin = total_profit / total_rev * 100 if total_rev else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Restaurants in view", f"{df.shape[0]:,}")
k2.metric("Monthly revenue (selected channels)", f"${total_rev:,.0f}")
k3.metric("Monthly net profit (selected channels)", f"${total_profit:,.0f}")
k4.metric("Blended net margin", f"{blended_margin:.1f}%")

st.divider()

# ----------------------------------------------------------------------------
# Module 1 — Channel-wise profit comparison
# ----------------------------------------------------------------------------
st.header("1. Channel-Wise Profit Comparison")

col1, col2 = st.columns(2)

margin_data = []
ppo_data = []
for c in selected_channels:
    margin_data.append({"Channel": CHANNEL_LABELS[c], "Net Margin (%)": df[f"{c}_MarginPct_wi"].mean()})
    ppo_data.append({"Channel": CHANNEL_LABELS[c], "Net Profit / Order ($)": df[f"{c}_NetProfitPerOrder_wi"].mean()})

margin_df = pd.DataFrame(margin_data)
ppo_df = pd.DataFrame(ppo_data)
color_map = {CHANNEL_LABELS[c]: COLORS[c] for c in selected_channels}

with col1:
    fig = px.bar(margin_df, x="Channel", y="Net Margin (%)", color="Channel",
                 color_discrete_map=color_map, text_auto=".1f", title="Average Net Margin by Channel")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(ppo_df, x="Channel", y="Net Profit / Order ($)", color="Channel",
                 color_discrete_map=color_map, text_auto=".2f", title="Average Net Profit per Order")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

rev_vs_profit = []
for c in selected_channels:
    rev_vs_profit.append({"Channel": CHANNEL_LABELS[c], "Type": "Revenue", "Value": df[f"{c}Revenue"].sum()})
    rev_vs_profit.append({"Channel": CHANNEL_LABELS[c], "Type": "Net Profit", "Value": df[f"{c}NetProfit_wi"].sum()})
rvp_df = pd.DataFrame(rev_vs_profit)
fig = px.bar(rvp_df, x="Channel", y="Value", color="Type", barmode="group",
             title="Revenue Volume vs. Actual Profit Contribution",
             color_discrete_map={"Revenue": "#3B6EF6", "Net Profit": "#27AE60"})
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Module 2 — Margin waterfall / cost component breakdown
# ----------------------------------------------------------------------------
st.header("2. Cost Component Breakdown & Margin Waterfall")

st.write("Pick a restaurant (or use the filtered-average profile) to see how revenue "
         "is eroded by COGS, OPEX, and the channel-specific commission or delivery cost.")

restaurant_options = ["Filtered-average restaurant"] + list(df["RestaurantID"])
selected_restaurant = st.selectbox("Restaurant", restaurant_options)

if selected_restaurant == "Filtered-average restaurant":
    rep = df.mean(numeric_only=True)
else:
    rep = df[df["RestaurantID"] == selected_restaurant].iloc[0]

waterfall_cols = st.columns(len([c for c in selected_channels if c != "InStore"]) or 1)
delivery_channels = [c for c in selected_channels if c != "InStore"]

for col, c in zip(waterfall_cols, delivery_channels):
    rev = rep[f"{c}Revenue"]
    cogs = rev * rep["COGSRate"]
    opex = rev * rep["OPEXRate"]
    if c == "SelfDelivery":
        extra = rep["SelfDeliveryOrdersCount"] * delivery_cost
        extra_label = "Delivery Cost"
    else:
        rate = commission_rate * (1.03 if c == "DoorDash" else 1.0)
        extra = rev * rate
        extra_label = "Commission"
    profit = rev - cogs - opex - extra

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Revenue", "COGS", "OPEX", extra_label, "Net Profit"],
        y=[rev, -cogs, -opex, -extra, profit],
        decreasing={"marker": {"color": "#EB5757"}},
        increasing={"marker": {"color": "#27AE60"}},
        totals={"marker": {"color": "#1a2744"}},
    ))
    fig.update_layout(title=f"{CHANNEL_LABELS[c]} Cost Waterfall", showlegend=False, height=380)
    col.plotly_chart(fig, use_container_width=True)

if "InStore" in selected_channels:
    rev = rep["InStoreRevenue"]
    cogs = rev * rep["COGSRate"]
    opex = rev * rep["OPEXRate"]
    profit = rev - cogs - opex
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=["absolute", "relative", "relative", "total"],
        x=["Revenue", "COGS", "OPEX", "Net Profit"], y=[rev, -cogs, -opex, profit],
        decreasing={"marker": {"color": "#EB5757"}}, increasing={"marker": {"color": "#27AE60"}},
        totals={"marker": {"color": "#1a2744"}},
    ))
    fig.update_layout(title="In-Store Cost Waterfall", showlegend=False, height=380)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Module 3 — Cuisine & segment profitability heatmaps
# ----------------------------------------------------------------------------
st.header("3. Cuisine & Segment Profitability Heatmaps")

heat_cols = [f"{c}_MarginPct_wi" for c in selected_channels]
heat_labels = [CHANNEL_LABELS[c] for c in selected_channels]

cuisine_pivot = df.groupby("CuisineType")[heat_cols].mean()
cuisine_pivot.columns = heat_labels

fig = px.imshow(cuisine_pivot, text_auto=".1f", color_continuous_scale="RdYlGn",
                 aspect="auto", title="Average Net Margin (%) by Cuisine Type and Channel",
                 labels=dict(color="Net Margin (%)"))
st.plotly_chart(fig, use_container_width=True)

seg_pivot = df.groupby("Segment")[heat_cols].mean()
seg_pivot.columns = heat_labels
seg_long = seg_pivot.reset_index().melt(id_vars="Segment", var_name="Channel", value_name="Net Margin (%)")
fig = px.bar(seg_long, x="Channel", y="Net Margin (%)", color="Segment", barmode="group",
             title="Channel Margin by Business Segment: Cafe vs QSR",
             color_discrete_map={"Cafe": "#3B6EF6", "QSR": "#F2994A"})
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Module 4 — Commission & delivery sensitivity + risk
# ----------------------------------------------------------------------------
st.header("4. Commission Sensitivity & Profit Volatility")

col1, col2 = st.columns(2)

with col1:
    avg_cogs = df["COGSRate"].mean()
    avg_opex = df["OPEXRate"].mean()
    comm_range = np.arange(0.10, 0.41, 0.01)
    sens_margin = (1 - avg_cogs - avg_opex - comm_range) * 100
    sens_df = pd.DataFrame({"Commission Rate (%)": comm_range * 100, "Resulting Net Margin (%)": sens_margin})
    fig = px.line(sens_df, x="Commission Rate (%)", y="Resulting Net Margin (%)",
                  title="Aggregator Margin Sensitivity to Commission Rate")
    fig.add_vline(x=commission_rate * 100, line_dash="dash", line_color="#1a2744",
                  annotation_text="Current slider value")
    fig.add_hline(y=0, line_dash="dot", line_color="grey")
    st.plotly_chart(fig, use_container_width=True)
    breakeven_comm = (1 - avg_cogs - avg_opex) * 100
    st.caption(f"Breakeven commission rate at current average COGS/OPEX: **{breakeven_comm:.1f}%**")

with col2:
    vol_data = []
    for c in selected_channels:
        vol_data.append({
            "Channel": CHANNEL_LABELS[c],
            "Margin Volatility (std dev, pp)": df[f"{c}_MarginPct_wi"].std(),
            "% Restaurants at a Loss": (df[f"{c}_MarginPct_wi"] < 0).mean() * 100,
        })
    vol_df = pd.DataFrame(vol_data)
    fig = px.bar(vol_df, x="Channel", y="% Restaurants at a Loss", color="Channel",
                 color_discrete_map=color_map, text_auto=".1f",
                 title="Share of Restaurants Operating at a Net Loss, by Channel")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(vol_df.set_index("Channel").round(1), use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Data table
# ----------------------------------------------------------------------------
with st.expander("View filtered restaurant-level data"):
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        df.to_csv(index=False).encode("utf-8"),
        "filtered_restaurant_data.csv",
        "text/csv",
    )

st.caption(
    "Data note: figures are computed from a simulated dataset built to match the project's schema "
    "and value ranges. Replace `restaurant_channel_data.csv` with the production dataset to reproduce "
    "this dashboard on live figures — the app logic and formulas require no changes."
)
