from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Click Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IP_RISK_FILE = PROJECT_ROOT / "output" / "real_ip_risk" / "part-r-00000"
HOURLY_FILE = PROJECT_ROOT / "output" / "hourly_stats" / "part-r-00000"

RISK_COLORS = {
    "HIGH_RISK": "#ef4444",
    "MEDIUM_RISK": "#f59e0b",
    "LOW_RISK": "#3b82f6",
}


@st.cache_data
def load_data():
    ip_columns = [
        "ip",
        "click_count",
        "unique_app_count",
        "unique_channel_count",
        "conversions",
        "median_app_id",
        "risk_score",
        "risk_label",
    ]

    ip_risk = pd.read_csv(
        IP_RISK_FILE,
        header=None,
        names=ip_columns,
        dtype={"ip": str},
    )

    hourly = pd.read_csv(
        HOURLY_FILE,
        header=None,
        names=["click_hour", "click_count", "conversions"],
    )

    for column in [
        "click_count",
        "unique_app_count",
        "unique_channel_count",
        "conversions",
        "risk_score",
    ]:
        ip_risk[column] = pd.to_numeric(ip_risk[column], errors="coerce").fillna(0)

    hourly["click_count"] = pd.to_numeric(hourly["click_count"], errors="coerce")
    hourly["conversions"] = pd.to_numeric(hourly["conversions"], errors="coerce")
    hourly["click_hour"] = pd.to_datetime(hourly["click_hour"])
    hourly["conversion_rate"] = (
        hourly["conversions"] / hourly["click_count"] * 100
    ).fillna(0)

    ip_risk["conversion_rate"] = (
        ip_risk["conversions"] / ip_risk["click_count"] * 100
    ).fillna(0)

    return ip_risk, hourly


def risk_reason(row):
    reasons = []

    if row["click_count"] >= 30:
        reasons.append("Very high click volume")
    elif row["click_count"] >= 10:
        reasons.append("Elevated click volume")

    if row["conversions"] == 0 and row["click_count"] >= 5:
        reasons.append("No conversion")

    if row["unique_app_count"] <= 2 and row["click_count"] >= 5:
        reasons.append("Repeated activity across few apps")

    if row["unique_channel_count"] <= 2 and row["click_count"] >= 5:
        reasons.append("Repeated activity across few channels")

    return "; ".join(reasons) if reasons else "Low behavioral risk"


if not IP_RISK_FILE.exists() or not HOURLY_FILE.exists():
    st.error("Không tìm thấy output của Pig. Hãy chạy `03_real_data_risk.pig` trước.")
    st.stop()

ip_risk, hourly = load_data()
ip_risk["risk_reason"] = ip_risk.apply(risk_reason, axis=1)

total_ips = len(ip_risk)
total_clicks = int(ip_risk["click_count"].sum())
high_risk = int((ip_risk["risk_label"] == "HIGH_RISK").sum())
medium_risk = int((ip_risk["risk_label"] == "MEDIUM_RISK").sum())
risk_rate = (high_risk + medium_risk) / total_ips * 100

st.title("🛡️ Click Fraud Intelligence Dashboard")
st.caption(
    "Real data: TalkingData AdTracking Fraud Detection Challenge · "
    "Apache Pig + DataFu · Behavioral risk scoring"
)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Total clicks", f"{total_clicks:,}")
metric_2.metric("Unique IPs", f"{total_ips:,}")
metric_3.metric("High-risk IPs", f"{high_risk:,}")
metric_4.metric("Medium-risk IPs", f"{medium_risk:,}")
metric_5.metric("Flagged IP rate", f"{risk_rate:.2f}%")

st.divider()

left, right = st.columns(2)

with left:
    click_trend = px.line(
        hourly,
        x="click_hour",
        y="click_count",
        markers=True,
        title="Click volume by hour",
        labels={"click_hour": "Hour", "click_count": "Clicks"},
    )
    click_trend.update_traces(line_color="#3b82f6")
    st.plotly_chart(click_trend, width="stretch")

with right:
    risk_counts = (
        ip_risk["risk_label"]
        .value_counts()
        .rename_axis("risk_label")
        .reset_index(name="ip_count")
    )

    risk_chart = px.bar(
        risk_counts,
        x="risk_label",
        y="ip_count",
        color="risk_label",
        color_discrete_map=RISK_COLORS,
        title="IP risk classification",
        labels={"risk_label": "Risk level", "ip_count": "IP count"},
    )
    st.plotly_chart(risk_chart, width="stretch")

left, right = st.columns(2)

with left:
    score_chart = px.histogram(
        ip_risk,
        x="risk_score",
        nbins=20,
        color="risk_label",
        color_discrete_map=RISK_COLORS,
        title="Risk score distribution",
        labels={"risk_score": "Risk score", "count": "IP count"},
    )
    st.plotly_chart(score_chart, width="stretch")

with right:
    scatter_data = ip_risk[ip_risk["click_count"] >= 2]
    behavior_chart = px.scatter(
        scatter_data,
        x="click_count",
        y="conversion_rate",
        size="risk_score",
        color="risk_label",
        hover_name="ip",
        hover_data=[
            "unique_app_count",
            "unique_channel_count",
            "conversions",
            "risk_score",
        ],
        color_discrete_map=RISK_COLORS,
        title="Click volume vs conversion rate",
        labels={
            "click_count": "Click count",
            "conversion_rate": "Conversion rate (%)",
        },
        log_x=True,
    )
    st.plotly_chart(behavior_chart, width="stretch")

st.subheader("Top IPs requiring investigation")

top_risk = ip_risk.sort_values(
    ["risk_score", "click_count"],
    ascending=[False, False],
).head(15)

top_chart = px.bar(
    top_risk,
    x="ip",
    y="risk_score",
    color="risk_label",
    hover_data=["click_count", "conversions", "conversion_rate"],
    color_discrete_map=RISK_COLORS,
    title="Highest-risk IP addresses",
    labels={"risk_score": "Risk score", "ip": "IP address"},
)
st.plotly_chart(top_chart, width="stretch")

st.subheader("Investigation table")

selected_labels = st.multiselect(
    "Risk level",
    options=["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK"],
    default=["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK"],
)

minimum_score = st.slider("Minimum risk score", 0, 100, 0)

filtered = ip_risk[
    ip_risk["risk_label"].isin(selected_labels)
    & (ip_risk["risk_score"] >= minimum_score)
].sort_values(["risk_score", "click_count"], ascending=False)

st.dataframe(
    filtered[
        [
            "ip",
            "click_count",
            "unique_app_count",
            "unique_channel_count",
            "conversions",
            "conversion_rate",
            "risk_score",
            "risk_label",
            "risk_reason",
        ]
    ],
    column_config={
        "conversion_rate": st.column_config.NumberColumn(
            "Conversion rate (%)",
            format="%.3f%%",
        ),
    },
    width="stretch",
    hide_index=True,
)

st.info(
    "Risk labels are behavioral inferences, not confirmed fraud labels. "
    "`is_attributed` represents app-download conversion in the source dataset."
)
