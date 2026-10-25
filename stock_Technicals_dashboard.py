#!/usr/bin/env python3
"""
Stock Technical Analysis Dashboard
TradingView-style Metrics Scoring + clean SuperTrend ribbon + rectangular markers.
Light theme. Supports multiple timeframes (5m → 1wk).
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from pathlib import Path
import warnings
import pandas_ta as ta
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Metrics Scoring Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────
# CUSTOM CSS – LIGHT THEME
# ──────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {display:none;}

    .stApp {
        background-color: #FFFFFF !important;
        color: #131722 !important;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown span,
    label, .stTextInput label, .stSelectbox label,
    div[data-testid="stMarkdownContainer"] {
        color: #131722 !important;
    }

    /* Top bar */
    .top-bar {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 8px 0 12px 0;
        border-bottom: 1px solid #e0e3eb;
        margin-bottom: 6px;
    }
    .ticker-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #131722 !important;
    }
    .price-up { color: #089981 !important; font-weight: 600; }
    .price-down { color: #f23645 !important; font-weight: 600; }

    /* Radio pills */
    div[role="radiogroup"] label {
        background: #f0f3fa !important;
        border: 1px solid #e0e3eb !important;
        border-radius: 4px !important;
        padding: 4px 11px !important;
        font-size: 0.78rem !important;
        color: #131722 !important;
        margin: 0 2px !important;
    }
    div[role="radiogroup"] label:has(input:checked) {
        background: #2962ff !important;
        color: #ffffff !important;
        border-color: #2962ff !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #131722 !important;
        border: 1px solid #e0e3eb !important;
        border-radius: 4px !important;
    }
    .stSelectbox [data-baseweb="select"] span {
        color: #131722 !important;
    }

    /* Metrics panel */
    .metrics-panel {
        background: #f8f9fd;
        border: 1px solid #e0e3eb;
        border-radius: 6px;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, Ubuntu, sans-serif;
    }
    .metrics-header {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        background: #f0f3fa;
        border-bottom: 1px solid #e0e3eb;
        font-size: 0.72rem;
        font-weight: 600;
        color: #787b86 !important;
        letter-spacing: 0.3px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 12px;
        font-size: 0.82rem;
        border-bottom: 1px solid #e0e3eb;
        background: #ffffff;
    }
    .metric-row:last-of-type { border-bottom: none; }
    .metric-name { color: #131722 !important; }
    .metric-bullish {
        background: #089981;
        color: #ffffff !important;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: 600;
        font-size: 0.78rem;
        min-width: 115px;
        text-align: center;
    }
    .metric-bearish {
        background: #f23645;
        color: #ffffff !important;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: 600;
        font-size: 0.78rem;
        min-width: 115px;
        text-align: center;
    }
    .metric-neutral {
        background: #e0e3eb;
        color: #131722 !important;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: 600;
        font-size: 0.78rem;
        min-width: 115px;
        text-align: center;
    }
    .overall-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 12px;
        background: #f0f3fa;
        border-top: 1px solid #e0e3eb;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .overall-label { color: #787b86 !important; }
    .overall-value {
        padding: 3px 10px;
        border-radius: 3px;
        font-weight: 700;
        font-size: 0.8rem;
        color: #ffffff !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e0e3eb;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# TICKER LIST
# ──────────────────────────────────────────────
TICKER_CSV = Path(__file__).parent / "nse_tickers.csv"

@st.cache_data
def load_ticker_list() -> pd.DataFrame:
    if TICKER_CSV.exists():
        df = pd.read_csv(TICKER_CSV)
        df["SYMBOL"] = df["SYMBOL"].astype(str).str.strip().str.upper()
        df["NAME"] = df["NAME"].astype(str).str.strip()
        df["LABEL"] = df["SYMBOL"] + "  —  " + df["NAME"]
        return df
    data = [
        ("NIFTY", "Nifty 50 Index"), ("BANKNIFTY", "Nifty Bank Index"),
        ("RELIANCE", "Reliance Industries"), ("TCS", "Tata Consultancy Services"),
        ("HDFCBANK", "HDFC Bank"), ("ICICIBANK", "ICICI Bank"),
        ("INFY", "Infosys"), ("SBIN", "State Bank of India"),
        ("BHARTIARTL", "Bharti Airtel"), ("ITC", "ITC Limited"), ("BSE", "BSE Limited"),
    ]
    df = pd.DataFrame(data, columns=["SYMBOL", "NAME"])
    df["LABEL"] = df["SYMBOL"] + "  —  " + df["NAME"]
    return df


# ──────────────────────────────────────────────
# DATA FETCH (supports multiple intervals)
# ──────────────────────────────────────────────
# yfinance limits: intraday (1m-1h) ≈ last 60 days; 1d/1wk = full history
INTERVAL_MAP = {
    "5m":  ("5m",  "60d"),
    "15m": ("15m", "60d"),
    "30m": ("30m", "60d"),
    "1H":  ("60m", "60d"),
    "3H":  ("60m", "60d"),   # will resample 1H → 3H
    "1D":  ("1d",  "5y"),
    "1W":  ("1wk", "5y"),
}

def _clip_to_latest_trading_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    For intraday data: keep only bars from the most recent trading day.
    - If today has data → from start of today until now.
    - If today is holiday / no data → full previous trading day.
    """
    if df.empty:
        return df
    # Normalize index to timezone-naive dates for grouping
    idx = df.index
    if getattr(idx, "tz", None) is not None:
        dates = idx.tz_convert("Asia/Kolkata").date
    else:
        dates = idx.date

    unique_dates = sorted(set(dates))
    if not unique_dates:
        return df

    latest_day = unique_dates[-1]
    mask = [d == latest_day for d in dates]
    return df.loc[mask]


@st.cache_data(ttl=900)
def fetch_stock_data(ticker: str, frequency: str = "1D") -> pd.DataFrame:
    original = ticker.upper().strip()
    index_map = {
        "NIFTY": "^NSEI", "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK", "NIFTYBANK": "^NSEBANK",
        "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
        "SENSEX": "^BSESN", "INDIAVIX": "^INDIAVIX",
    }
    if original in index_map:
        candidate = index_map[original]
    elif not original.endswith((".NS", ".BO")):
        candidate = original + ".NS"
    else:
        candidate = original

    yf_interval, yf_period = INTERVAL_MAP.get(frequency, ("1d", "5y"))
    is_intraday = frequency in ("5m", "15m", "30m", "1H", "3H")

    try:
        df = yf.download(candidate, period=yf_period, interval=yf_interval,
                         progress=False, auto_adjust=True)
        if df.empty and candidate != original:
            df = yf.download(original, period=yf_period, interval=yf_interval,
                             progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.columns = [str(c).title() for c in df.columns]
        df = df.dropna(subset=["Close"])

        # Resample 1H → 3H if needed
        if frequency == "3H" and not df.empty:
            df = df.resample("3h").agg({
                "Open": "first", "High": "max", "Low": "min",
                "Close": "last", "Volume": "sum"
            }).dropna()

        # Intraday → only the latest trading day (today, or previous if holiday)
        if is_intraday and not df.empty:
            df = _clip_to_latest_trading_day(df)

        return df
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return pd.DataFrame()


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 50:
        return df
    data = df.copy()
    c, h, l = data["Close"], data["High"], data["Low"]
    v = data["Volume"] if "Volume" in data.columns else pd.Series(0, index=data.index)

    macd = data.ta.macd(close=c, fast=12, slow=26, signal=9)
    if macd is not None:
        data = pd.concat([data, macd], axis=1)

    data["RSI"] = data.ta.rsi(close=c, length=14)

    stoch = data.ta.stoch(high=h, low=l, close=c, k=14, d=3, smooth_k=3)
    if stoch is not None:
        data = pd.concat([data, stoch], axis=1)

    vortex = data.ta.vortex(high=h, low=l, close=c, length=14)
    if vortex is not None:
        data = pd.concat([data, vortex], axis=1)

    data["MOM"] = data.ta.mom(close=c, length=10)

    psar = data.ta.psar(high=h, low=l, close=c)
    if psar is not None:
        data = pd.concat([data, psar], axis=1)

    fisher = data.ta.fisher(high=h, low=l, length=9)
    if fisher is not None:
        data = pd.concat([data, fisher], axis=1)

    adx = data.ta.adx(high=h, low=l, close=c, length=14)
    if adx is not None:
        data = pd.concat([data, adx], axis=1)

    mfi = data.ta.mfi(high=h, low=l, close=c, volume=v, length=14)
    if mfi is not None:
        data["MFI"] = mfi

    st_ = data.ta.supertrend(high=h, low=l, close=c, length=10, multiplier=3.0)
    if st_ is not None:
        data = pd.concat([data, st_], axis=1)

    data["TREND"] = data.ta.ema(close=c, length=10)
    return data


# ──────────────────────────────────────────────
# SCORING (regime-aware, stable across chart filters)
# ──────────────────────────────────────────────
def get_metrics(df: pd.DataFrame):
    if df.empty or len(df) < 30:
        return []

    latest = df.iloc[-1]
    rows = []

    def add(name, direction, score, weight):
        rows.append((name, direction, round(float(score), 1), weight))

    st_dir = latest.get("SUPERTd_10_3.0", np.nan)
    if np.isnan(st_dir):
        st_line = latest.get("SUPERT_10_3.0", np.nan)
        st_dir = 1.0 if latest["Close"] > st_line else -1.0
    regime_bearish = st_dir < 0

    # MACD
    macd_h = latest.get("MACDh_12_26_9", np.nan)
    macd_l = latest.get("MACD_12_26_9", np.nan)
    macd_s = latest.get("MACDs_12_26_9", np.nan)
    if not np.isnan(macd_h):
        if macd_h < 0 or (not np.isnan(macd_l) and not np.isnan(macd_s) and macd_l < macd_s):
            add("MACD", "Bearish", min(5.0, 3.5 + abs(macd_h)/15), 1.2)
        elif regime_bearish and macd_h < 40:
            add("MACD", "Bearish", 3.5, 1.2)
        elif macd_h > 0:
            add("MACD", "Bullish", min(5.0, 3.0 + abs(macd_h)/15), 1.2)
        else:
            add("MACD", "Neutral", 2.5, 0.9)
    else:
        add("MACD", "Neutral", 2.5, 0.9)

    # RSI
    rsi = latest.get("RSI", np.nan)
    if not np.isnan(rsi):
        if rsi >= 70:
            add("RSI", "Bearish", 4.8, 1.2)
        elif rsi <= 30:
            add("RSI", "Bullish", 4.8, 1.2)
        elif regime_bearish and rsi < 55:
            add("RSI", "Bearish", 3.5, 1.0)
        elif not regime_bearish and rsi > 45:
            add("RSI", "Bullish", 3.5, 1.0)
        elif rsi >= 55:
            add("RSI", "Bullish", 3.2, 1.0)
        elif rsi <= 45:
            add("RSI", "Bearish", 3.2, 1.0)
        else:
            add("RSI", "Neutral", 2.5, 0.9)
    else:
        add("RSI", "Neutral", 2.5, 0.9)

    # Stochastic
    stoch_k = latest.get("STOCHk_14_3_3", np.nan)
    if not np.isnan(stoch_k):
        if stoch_k >= 80:
            add("Stochastic", "Bearish", 4.0, 1.0)
        elif stoch_k <= 20:
            add("Stochastic", "Bullish", 4.0, 1.0)
        elif 45 <= stoch_k <= 55:
            add("Stochastic", "Neutral", 2.5, 0.9)
        elif stoch_k > 55:
            add("Stochastic", "Bullish", 3.0, 0.9)
        else:
            add("Stochastic", "Bearish", 3.0, 0.9)
    else:
        add("Stochastic", "Neutral", 2.5, 0.9)

    # Vortex
    vip = latest.get("VTXP_14", np.nan)
    vim = latest.get("VTXM_14", np.nan)
    if not (np.isnan(vip) or np.isnan(vim)):
        diff = vip - vim
        if diff > 0.1:
            add("Vortex", "Bullish", 3.5, 0.9)
        elif diff < -0.1:
            add("Vortex", "Bearish", 3.5, 0.9)
        else:
            add("Vortex", "Bearish" if regime_bearish else "Bullish", 2.3, 0.9)
    else:
        add("Vortex", "Neutral", 2.5, 0.9)

    # Momentum
    mom = latest.get("MOM", np.nan)
    if not np.isnan(mom):
        price = latest["Close"] or 1
        mom_pct = (mom / price) * 100
        if mom_pct > 2.0:
            add("Momentum", "Bullish", min(5.0, 2.5 + abs(mom_pct)/2), 1.2)
        elif mom_pct < -2.0:
            add("Momentum", "Bearish", min(5.0, 2.5 + abs(mom_pct)/2), 1.2)
        else:
            add("Momentum", "Bearish" if regime_bearish else "Bullish", 2.5, 1.0)
    else:
        add("Momentum", "Neutral", 2.0, 0.8)

    # PSAR
    psarl = latest.get("PSARl_0.02_0.2", np.nan)
    psars = latest.get("PSARs_0.02_0.2", np.nan)
    if not np.isnan(psars):
        add("PSAR", "Bearish", 5.0, 1.5)
    elif not np.isnan(psarl):
        if regime_bearish:
            add("PSAR", "Bearish", 3.0, 1.2)
        else:
            add("PSAR", "Bullish", 5.0, 1.5)
    else:
        add("PSAR", "Neutral", 2.0, 0.8)

    # DMI
    dmp = latest.get("DMP_14", np.nan)
    dmn = latest.get("DMN_14", np.nan)
    di_diff = None
    if not (np.isnan(dmp) or np.isnan(dmn)):
        di_diff = dmp - dmn
        if di_diff > 3:
            add("DMI", "Bullish", min(5.0, abs(di_diff)/3), 1.5)
        elif di_diff < -1.5:
            add("DMI", "Bearish", min(5.0, abs(di_diff)/2.5), 1.5)
        else:
            add("DMI", "Bearish" if regime_bearish else "Bullish", 2.0, 1.2)
    else:
        add("DMI", "Neutral", 2.0, 0.8)

    # MFI
    mfi = latest.get("MFI", latest.get("MFI_14", np.nan))
    if not np.isnan(mfi):
        if mfi >= 80:
            add("MFI", "Bearish", 5.0, 1.0)
        elif mfi <= 20:
            add("MFI", "Bullish", 5.0, 1.0)
        elif mfi >= 55:
            add("MFI", "Bullish", 3.8, 0.9)
        elif mfi <= 45:
            add("MFI", "Bearish", 3.8, 0.9)
        else:
            add("MFI", "Neutral", 2.5, 0.8)
    else:
        add("MFI", "Neutral", 2.5, 0.8)

    # Fisher
    fisher = latest.get("FISHERT_9_1", np.nan)
    if not np.isnan(fisher):
        if fisher > 0.6:
            add("Fisher", "Bullish", min(5.0, 2.5 + abs(fisher)), 1.0)
        elif fisher < -0.6:
            add("Fisher", "Bearish", min(5.0, 2.5 + abs(fisher)), 1.0)
        elif regime_bearish and fisher < 1.0:
            add("Fisher", "Bearish", 3.0, 1.0)
        elif not regime_bearish and fisher > -1.0:
            add("Fisher", "Bullish", 3.0, 1.0)
        else:
            add("Fisher", "Neutral", 2.5, 0.8)
    else:
        add("Fisher", "Neutral", 2.5, 0.8)

    # ADX
    adx_val = latest.get("ADX_14", np.nan)
    if not np.isnan(adx_val):
        strength = min(5.0, max(1.0, adx_val / 10))
        if di_diff is not None and di_diff < -1:
            add("ADX", "Bearish", strength, 1.2)
        elif di_diff is not None and di_diff > 1:
            add("ADX", "Bullish", strength, 1.2)
        else:
            add("ADX", "Bearish" if regime_bearish else "Bullish", strength * 0.8, 1.0)
    else:
        add("ADX", "Neutral", 2.0, 0.8)

    # SuperTrend
    if st_dir > 0:
        add("Supertrend", "Bullish", 5.0, 2.0)
    else:
        add("Supertrend", "Bearish", 5.0, 2.0)

    return rows


def overall_score(rows):
    if not rows:
        return 5.0, "Neutral/Mixed", "#787b86"
    total = weight_sum = 0.0
    for _, direction, score, weight in rows:
        sign = 1 if direction == "Bullish" else (-1 if direction == "Bearish" else 0)
        total += sign * score * weight
        weight_sum += weight
    avg = total / weight_sum if weight_sum else 0.0
    display = round(max(0.0, min(10.0, 5.0 + avg * 0.7)), 1)
    if avg <= -2.8:
        return display, "Strong Bearish", "#f23645"
    if avg <= -1.0:
        return display, "Bearish", "#f23645"
    if avg >= 2.8:
        return display, "Strong Bullish", "#089981"
    if avg >= 1.0:
        return display, "Bullish", "#089981"
    return display, "Neutral/Mixed", "#787b86"


# ──────────────────────────────────────────────
# CHART + RECTANGULAR MARKERS
# ──────────────────────────────────────────────
def find_inflections(df, window=8):
    if len(df) < window * 2 + 1:
        return pd.DataFrame(columns=["Date", "Price", "Type", "Score"])
    close = df["Close"].values
    idx = df.index
    records = []
    for i in range(window, len(close) - window):
        seg = close[i - window: i + window + 1]
        if close[i] == np.max(seg):
            # simple score = local strength (how much higher than neighbours)
            strength = (close[i] - np.mean(seg)) / (np.std(seg) + 1e-9)
            score = round(min(9.9, max(1.0, 3.0 + strength)), 1)
            records.append({"Date": idx[i], "Price": close[i], "Type": "Peak", "Score": score})
        if close[i] == np.min(seg):
            strength = (np.mean(seg) - close[i]) / (np.std(seg) + 1e-9)
            score = round(min(9.9, max(1.0, 3.0 + strength)), 1)
            records.append({"Date": idx[i], "Price": close[i], "Type": "Trough", "Score": score})
    return pd.DataFrame(records)


def build_chart(df: pd.DataFrame, infl_df: pd.DataFrame):
    fig = go.Figure()

    # Candles
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#089981",
        decreasing_line_color="#f23645",
        increasing_fillcolor="#089981",
        decreasing_fillcolor="#f23645",
        name="OHLC",
        showlegend=False,
    ))

    # SuperTrend ribbon (pink / green)
    if "SUPERTd_10_3.0" in df.columns and "SUPERT_10_3.0" in df.columns:
        st_line = df["SUPERT_10_3.0"]
        st_dir  = df["SUPERTd_10_3.0"]
        dirs = st_dir.ffill().fillna(1).values
        line = st_line.values
        dates = df.index

        bull_x, bull_y, bear_x, bear_y = [], [], [], []
        for i in range(len(dirs)):
            if dirs[i] > 0:
                bull_x.append(dates[i]); bull_y.append(line[i])
                bear_x.append(None);     bear_y.append(None)
            else:
                bear_x.append(dates[i]); bear_y.append(line[i])
                bull_x.append(None);     bull_y.append(None)

        fig.add_trace(go.Scatter(
            x=bull_x, y=bull_y, mode="lines",
            line=dict(color="#26a69a", width=2.5),
            showlegend=False, connectgaps=False,
        ))
        fig.add_trace(go.Scatter(
            x=bear_x, y=bear_y, mode="lines",
            line=dict(color="#e91e63", width=2.5),
            showlegend=False, connectgaps=False,
        ))

    # Rectangular block markers (last few only, like TradingView)
    if not infl_df.empty:
        recent = infl_df.tail(8)
        for _, row in recent.iterrows():
            is_peak = row["Type"] == "Peak"
            bg = "#f23645" if is_peak else "#089981"
            # Use annotation with arrow + rectangular background
            fig.add_annotation(
                x=row["Date"],
                y=row["Price"],
                text=f"<b>{row['Score']}</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1.2,
                arrowwidth=1.5,
                arrowcolor=bg,
                ax=0,
                ay=-28 if is_peak else 28,
                bgcolor=bg,
                bordercolor=bg,
                borderwidth=1,
                borderpad=4,
                font=dict(size=11, color="#ffffff", family="Arial Black"),
                opacity=0.95,
            )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=520,
        margin=dict(l=8, r=50, t=8, b=20),
        xaxis=dict(
            rangeslider_visible=False,
            showgrid=True, gridcolor="#e0e3eb",
            showspikes=True, spikemode="across",
            spikedash="solid", spikethickness=1, spikecolor="#787b86",
            tickfont=dict(size=11, color="#787b86"),
        ),
        yaxis=dict(
            side="right",
            showgrid=True, gridcolor="#e0e3eb",
            tickfont=dict(size=11, color="#787b86"),
        ),
        hovermode="x unified",
        dragmode="pan",
        font=dict(color="#131722", family="Arial"),
    )
    # Hide weekends only for daily+ data
    if len(df) > 0 and (df.index[-1] - df.index[0]).days > 5:
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig


def filter_period(df, period, frequency):
    """Period filter only makes sense for daily/weekly. For intraday we keep all."""
    if df.empty or period == "All" or frequency in ("5m", "15m", "30m", "1H", "3H"):
        return df
    days = {"7D": 7, "15D": 15, "1M": 30, "3M": 90, "6M": 180,
            "1Y": 365, "5Y": 365 * 5}.get(period, None)
    if days is None:
        return df
    return df[df.index >= df.index[-1] - timedelta(days=days)]


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    tickers_df = load_ticker_list()

    # ── Row 1: Ticker + Frequency ──
    c1, c2 = st.columns([1.8, 3.2])
    with c1:
        default_idx = 0
        if "NIFTY" in tickers_df["SYMBOL"].values:
            default_idx = int(tickers_df[tickers_df["SYMBOL"] == "NIFTY"].index[0])
        selected_label = st.selectbox(
            "Search ticker",
            options=tickers_df["LABEL"].tolist(),
            index=default_idx,
            placeholder="Type to search… e.g. nift, reli, bse",
            label_visibility="collapsed",
        )
        ticker = selected_label.split("—")[0].strip() if selected_label else "NIFTY"

    with c2:
        frequency = st.radio(
            "Frequency",
            options=["5m", "15m", "30m", "1H", "3H", "1D", "1W"],
            index=5,   # default 1D
            horizontal=True,
            label_visibility="collapsed",
            key="freq",
        )

    # ── Row 2: Horizon (only for 1D / 1W) ──
    is_intraday = frequency in ("5m", "15m", "30m", "1H", "3H")
    if not is_intraday:
        period = st.radio(
            "Horizon",
            options=["7D", "15D", "1M", "3M", "6M", "1Y", "5Y", "All"],
            index=5 if frequency == "1D" else 7,
            horizontal=True,
            label_visibility="collapsed",
            key="horizon",
        )
    else:
        period = "All"

    if not ticker:
        st.warning("Select a ticker")
        return

    with st.spinner(f"Loading {frequency} data…"):
        full = fetch_stock_data(ticker, frequency=frequency)
        if full.empty:
            st.error(f"No data for “{ticker}” at {frequency}. Try 1D or another symbol.")
            return
        full = compute_indicators(full)

    chart_df = filter_period(full, period, frequency)

    # Intraday caption: show which day is being displayed
    if is_intraday and not chart_df.empty:
        day_str = chart_df.index[0].strftime("%d %b %Y")
        if getattr(chart_df.index[0], "tz", None) is not None:
            day_str = chart_df.index[0].tz_convert("Asia/Kolkata").strftime("%d %b %Y")
        st.caption(f"Intraday ({frequency}) · showing **{day_str}** only "
                   f"(today if market is open, otherwise last trading day)")
    latest   = full.iloc[-1]
    prev     = full.iloc[-2]["Close"] if len(full) > 1 else latest["Close"]
    chg      = latest["Close"] - prev
    chg_pct  = chg / prev * 100 if prev else 0
    up       = chg >= 0

    # Header
    price_cls = "price-up" if up else "price-down"
    sign = "+" if up else ""
    name = ""
    match = tickers_df[tickers_df["SYMBOL"] == ticker]
    if not match.empty:
        name = match.iloc[0]["NAME"]

    st.markdown(
        f"""
        <div class="top-bar">
            <span class="ticker-title">{ticker}</span>
            <span style="color:#787b86;font-size:0.85rem;">{name}</span>
            <span class="{price_cls}" style="font-size:1.3rem;">
                {latest['Close']:,.2f}
            </span>
            <span class="{price_cls}" style="font-size:0.9rem;">
                {sign}{chg:,.2f} ({sign}{chg_pct:.2f}%)
            </span>
            <span style="color:#787b86;font-size:0.8rem;margin-left:10px;">
                O&nbsp;{latest['Open']:,.2f}&nbsp;&nbsp;
                H&nbsp;{latest['High']:,.2f}&nbsp;&nbsp;
                L&nbsp;{latest['Low']:,.2f}
            </span>
            <span style="color:#787b86;font-size:0.75rem;margin-left:auto;">
                {frequency}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chart + Metrics
    left, right = st.columns([2.15, 1])
    infl_all = find_inflections(chart_df, window=7)

    with left:
        fig = build_chart(chart_df, infl_all)
        st.plotly_chart(fig, use_container_width=True, config={
            "displayModeBar": False,
            "scrollZoom": True,
        })

    with right:
        rows = get_metrics(full)
        disp, judgement, color = overall_score(rows)

        html = ['<div class="metrics-panel">']
        html.append('<div class="metrics-header"><span>METRICS SCORING SYSTEM</span><span>Results</span></div>')
        for name_, direction, score, weight in rows:
            cls = {"Bullish": "metric-bullish", "Bearish": "metric-bearish",
                   "Neutral": "metric-neutral"}[direction]
            label = f"{direction} ({score:.1f} | {weight})"
            html.append(
                f'<div class="metric-row">'
                f'<span class="metric-name">{name_} {direction}</span>'
                f'<span class="{cls}">{label}</span>'
                f'</div>'
            )
        html.append(
            f'<div class="overall-row">'
            f'<span class="overall-label">OVERALL MARKET SCORE</span>'
            f'<span class="overall-value" style="background:{color};">'
            f'{judgement} ({disp}/10)</span>'
            f'</div>'
        )
        html.append('</div>')
        st.markdown("".join(html), unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin-top:10px;font-size:0.72rem;color:#787b86;'>"
            f"Data as of {full.index[-1].strftime('%d %b %Y %H:%M') if hasattr(full.index[-1], 'hour') else full.index[-1].strftime('%d %b %Y')} · Yahoo Finance</div>",
            unsafe_allow_html=True,
        )

    # Inflection table
    st.markdown("---")
    st.markdown("##### Inflection Points History")
    if not infl_all.empty:
        display = infl_all.sort_values("Date", ascending=False).copy()
        display["Date"] = display["Date"].astype(str).str.slice(0, 16)
        display["Price"] = display["Price"].round(2)
        display["Type"] = display["Type"].map({"Peak": "▼ Peak", "Trough": "▲ Trough"})
        display = display.rename(columns={"Score": "Strength"})
        st.dataframe(display, use_container_width=True, hide_index=True,
                     height=min(340, 40 + 28 * len(display)))
    else:
        st.info("No clear inflection points found in the selected period.")


if __name__ == "__main__":
    main()
