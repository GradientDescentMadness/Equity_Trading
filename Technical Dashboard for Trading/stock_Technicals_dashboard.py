#!/usr/bin/env python3
"""
Stock Technical Analysis Dashboard
TradingView-style Metrics Scoring + clean SuperTrend ribbon + rectangular markers.
Light theme. Supports multiple timeframes (5m → 1wk) and dual markets: INDIA & USA.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import timedelta
from pathlib import Path
import warnings
import pandas_ta as ta

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Technical Metrics Scoring Dashboard",
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

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e0e3eb;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        border-radius: 4px 4px 0 0 !important;
        color: #787b86 !important;
        background-color: #f8f9fd !important;
        border: 1px solid #e0e3eb !important;
        border-bottom: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2962ff !important;
        color: #ffffff !important;
        border-color: #2962ff !important;
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
        font-size: 1.25rem;
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
# TICKER MAPPINGS & ALIASES
# ──────────────────────────────────────────────
INDEX_MAP_IN = {
    "NIFTY": "^NSEI", "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK", "NIFTYBANK": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCPNIFTY": "^NSEMDCP50",
    "NIFTYIT": "^CNXIT",
    "NIFTYPHARMA": "^CNXPHARMA",
    "NIFTYAUTO": "^CNXAUTO",
    "NIFTYMETAL": "^CNXMETAL",
    "NIFTYFMCG": "^CNXFMCG",
    "NIFTYREALTY": "^CNXREALTY",
    "NIFTYPSE": "^CNXPSE",
    "NIFTYENERGY": "^CNXENERGY",
    "NIFTYINFRA": "^CNXINFRA",
    "NIFTYMEDIA": "^CNXMEDIA",
    "NIFTYPVTBANK": "NIFTY_PVT_BANK.NS",
    "NIFTYPSUBANK": "^CNXPSUBANK",
    "SENSEX": "^BSESN", "INDIAVIX": "^INDIAVIX",
}

# Corporate action & rebranding aliases
RENAMED_MAP_IN = {
    "TATAMOTORS": "TMPV.NS",
    "ZOMATO": "ETERNAL.NS",
    "AMARAJABAT": "ARE&M.NS",
    "AEGISCHEM": "AEGISLOG.NS",
    "ATFL": "SUNDROP.NS",
    "MOTHERSUMI": "MOTHERSON.NS",
    "CADILAHC": "ZYDUSLIFE.NS",
    "L&TFH": "LTF.NS",
    "HDFC": "HDFCBANK.NS",
}

INDEX_MAP_US = {
    "SPX": "^GSPC", "S&P 500": "^GSPC", "^GSPC": "^GSPC",
    "DJI": "^DJI", "DOW": "^DJI", "^DJI": "^DJI",
    "COMP": "^IXIC", "NASDAQ": "^IXIC", "^IXIC": "^IXIC",
    "NDX": "^NDX", "^NDX": "^NDX",
    "RUT": "^RUT", "RUSSELL": "^RUT", "^RUT": "^RUT",
    "VIX": "^VIX", "^VIX": "^VIX",
}

BASE_DIR = Path(__file__).parent
TICKER_CSV_IN = BASE_DIR / "nse_tickers.csv"
TICKER_CSV_US = BASE_DIR / "us_tickers.csv"


@st.cache_data
def load_ticker_list(market: str = "IN") -> pd.DataFrame:
    """Load and normalize ticker database for India or USA."""
    csv_path = TICKER_CSV_IN if market == "IN" else TICKER_CSV_US
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df["SYMBOL"] = df["SYMBOL"].astype(str).str.strip().str.upper()
        df["NAME"] = df["NAME"].astype(str).str.strip()
        df["LABEL"] = df["SYMBOL"] + "  —  " + df["NAME"]
        return df

    # Fallback datasets if CSV is missing
    if market == "IN":
        data = [
            ("NIFTY", "Nifty 50 Index"), ("BANKNIFTY", "Nifty Bank Index"),
            ("FINNIFTY", "Nifty Financial Services"), ("MIDCPNIFTY", "Nifty Midcap Select"),
            ("NIFTYIT", "Nifty IT Index"), ("SENSEX", "BSE Sensex Index"),
            ("RELIANCE", "Reliance Industries"), ("TCS", "Tata Consultancy Services"),
            ("HDFCBANK", "HDFC Bank"), ("ICICIBANK", "ICICI Bank"),
            ("INFY", "Infosys"), ("SBIN", "State Bank of India"),
            ("BHARTIARTL", "Bharti Airtel"), ("ITC", "ITC Limited"), ("BSE", "BSE Limited"),
        ]
    else:
        data = [
            ("^GSPC", "S&P 500 Index"), ("^DJI", "Dow Jones Industrial Average"),
            ("^IXIC", "NASDAQ Composite"), ("^NDX", "NASDAQ 100 Index"),
            ("^RUT", "Russell 2000 Index"), ("^VIX", "CBOE Volatility Index"),
            ("SPY", "SPDR S&P 500 ETF Trust"), ("QQQ", "Invesco QQQ Trust"),
            ("AAPL", "Apple Inc."), ("MSFT", "Microsoft Corporation"),
            ("NVDA", "NVIDIA Corporation"), ("GOOGL", "Alphabet Inc."),
            ("AMZN", "Amazon.com Inc."), ("META", "Meta Platforms Inc."),
            ("TSLA", "Tesla Inc."), ("JPM", "JPMorgan Chase & Co."),
        ]
    df = pd.DataFrame(data, columns=["SYMBOL", "NAME"])
    df["LABEL"] = df["SYMBOL"] + "  —  " + df["NAME"]
    return df


# ──────────────────────────────────────────────
# DATA FETCHING (Resilient Direct API + yfinance)
# ──────────────────────────────────────────────
INTERVAL_MAP = {
    "5m":  ("5m",  "60d"),
    "15m": ("15m", "60d"),
    "30m": ("30m", "60d"),
    "1H":  ("60m", "60d"),
    "3H":  ("60m", "60d"),   # Resampled 1H → 3H
    "1D":  ("1d",  "5y"),
    "1W":  ("1wk", "5y"),
}


def resolve_candidate_symbol(ticker: str, market: str = "IN") -> str:
    raw = ticker.upper().strip()
    if market == "IN":
        if raw in INDEX_MAP_IN:
            return INDEX_MAP_IN[raw]
        if raw in RENAMED_MAP_IN:
            return RENAMED_MAP_IN[raw]
        if not raw.endswith((".NS", ".BO")):
            return raw + ".NS"
        return raw
    else:  # US
        if raw in INDEX_MAP_US:
            return INDEX_MAP_US[raw]
        return raw


def _direct_yahoo_chart_fetch(symbol: str, range_: str, interval: str) -> pd.DataFrame:
    """Fast, crumb-free direct query to Yahoo Finance chart API."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_}&interval={interval}&includePrePost=false"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            # Fallback to query2
            url2 = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_}&interval={interval}&includePrePost=false"
            r = requests.get(url2, headers=headers, timeout=10)

        if r.status_code == 200:
            data = r.json()
            result = data.get("chart", {}).get("result")
            if result and result[0].get("timestamp"):
                res = result[0]
                timestamps = res["timestamp"]
                indicators = res.get("indicators", {})
                quote = indicators.get("quote", [{}])[0]

                # Prefer adjusted close if available
                adj_close = quote.get("close", [])
                if "adjclose" in indicators and indicators["adjclose"] and "adjclose" in indicators["adjclose"][0]:
                    adj_close = indicators["adjclose"][0]["adjclose"]

                df = pd.DataFrame({
                    "Open": quote.get("open", []),
                    "High": quote.get("high", []),
                    "Low": quote.get("low", []),
                    "Close": adj_close,
                    "Volume": quote.get("volume", [0] * len(timestamps))
                }, index=pd.to_datetime(timestamps, unit="s"))

                # Convert to local exchange timezone
                tz_name = res.get("meta", {}).get("exchangeTimezoneName")
                if tz_name:
                    try:
                        df.index = df.index.tz_localize("UTC").tz_convert(tz_name)
                    except Exception:
                        pass
                return df.dropna(subset=["Close"])
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=900)
def fetch_stock_data(ticker: str, frequency: str = "1D", market: str = "IN") -> pd.DataFrame:
    """
    Fetches full historical OHLCV data using direct resilient chart API
    with automatic fallbacks (BSE fallback for India, yfinance fallback).
    NOTE: Returns the FULL historical series so technical indicators receive
    adequate warm-up bars.
    """
    candidate = resolve_candidate_symbol(ticker, market)
    yf_interval, yf_period = INTERVAL_MAP.get(frequency, ("1d", "5y"))
    req_interval = "60m" if frequency == "3H" else yf_interval

    # 1. Primary Direct API Fetch
    df = _direct_yahoo_chart_fetch(candidate, yf_period, req_interval)

    # 2. BSE Fallback for Indian equities if NSE data is empty
    if df.empty and market == "IN" and candidate.endswith(".NS"):
        bse_candidate = candidate.replace(".NS", ".BO")
        df = _direct_yahoo_chart_fetch(bse_candidate, yf_period, req_interval)

    # 3. yfinance download fallback
    if df.empty:
        try:
            df = yf.download(candidate, period=yf_period, interval=req_interval,
                             progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                if "Close" in df.columns.get_level_values(0):
                    df.columns = df.columns.get_level_values(0)
                else:
                    df.columns = df.columns.get_level_values(1)
            df.columns = [str(c).title() for c in df.columns]
            df = df.dropna(subset=["Close"])
        except Exception:
            pass

    # Resample 1H → 3H if requested
    if frequency == "3H" and not df.empty:
        df = df.resample("3h").agg({
            "Open": "first", "High": "max", "Low": "min",
            "Close": "last", "Volume": "sum"
        }).dropna()

    return df


# ──────────────────────────────────────────────
# TECHNICAL INDICATORS ENGINE
# ──────────────────────────────────────────────
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Computes full suite of 10+ technical indicators using pandas_ta."""
    if df.empty or len(df) < 20:
        return df

    data = df.copy()
    c, h, l = data["Close"], data["High"], data["Low"]
    v = data["Volume"] if "Volume" in data.columns else pd.Series(0, index=data.index)

    # MACD (12, 26, 9)
    try:
        macd = data.ta.macd(close=c, fast=12, slow=26, signal=9)
        if macd is not None:
            data = pd.concat([data, macd], axis=1)
    except Exception:
        pass

    # RSI (14)
    try:
        data["RSI"] = data.ta.rsi(close=c, length=14)
    except Exception:
        pass

    # Stochastic (14, 3, 3)
    try:
        stoch = data.ta.stoch(high=h, low=l, close=c, k=14, d=3, smooth_k=3)
        if stoch is not None:
            data = pd.concat([data, stoch], axis=1)
    except Exception:
        pass

    # Vortex (14)
    try:
        vortex = data.ta.vortex(high=h, low=l, close=c, length=14)
        if vortex is not None:
            data = pd.concat([data, vortex], axis=1)
    except Exception:
        pass

    # Momentum (10)
    try:
        data["MOM"] = data.ta.mom(close=c, length=10)
    except Exception:
        pass

    # PSAR
    try:
        psar = data.ta.psar(high=h, low=l, close=c)
        if psar is not None:
            data = pd.concat([data, psar], axis=1)
    except Exception:
        pass

    # Fisher Transform (9)
    try:
        fisher = data.ta.fisher(high=h, low=l, length=9)
        if fisher is not None:
            data = pd.concat([data, fisher], axis=1)
    except Exception:
        pass

    # ADX & DMI (14)
    try:
        adx = data.ta.adx(high=h, low=l, close=c, length=14)
        if adx is not None:
            data = pd.concat([data, adx], axis=1)
    except Exception:
        pass

    # MFI (14)
    try:
        mfi = data.ta.mfi(high=h, low=l, close=c, volume=v, length=14)
        if mfi is not None:
            data["MFI"] = mfi
    except Exception:
        pass

    # SuperTrend (10, 3.0)
    try:
        st_ = data.ta.supertrend(high=h, low=l, close=c, length=10, multiplier=3.0)
        if st_ is not None:
            data = pd.concat([data, st_], axis=1)
    except Exception:
        pass

    # Trend EMA (10)
    try:
        data["TREND"] = data.ta.ema(close=c, length=10)
    except Exception:
        pass

    return data


# ──────────────────────────────────────────────
# REGIME-AWARE METRICS SCORING
# ──────────────────────────────────────────────
def get_metrics(df: pd.DataFrame):
    """Evaluates 10 core indicators against the prevailing SuperTrend regime."""
    if df.empty or len(df) < 15:
        return []

    latest = df.iloc[-1]
    rows = []

    def add(name, direction, score, weight):
        rows.append((name, direction, round(float(score), 1), weight))

    # Determine Macro Regime via SuperTrend
    st_dir = latest.get("SUPERTd_10_3.0", np.nan)
    if np.isnan(st_dir):
        st_line = latest.get("SUPERT_10_3.0", np.nan)
        if not np.isnan(st_line):
            st_dir = 1.0 if latest["Close"] > st_line else -1.0
        else:
            st_dir = 1.0
    regime_bearish = st_dir < 0

    # 1. MACD
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

    # 2. RSI
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

    # 3. Stochastic
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

    # 4. Vortex
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

    # 5. Momentum
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

    # 6. PSAR
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

    # 7. DMI / Directional Movement
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

    # 8. MFI (Money Flow Index)
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

    # 9. Fisher Transform
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

    # 10. ADX Trend Strength
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

    # 11. SuperTrend Anchor
    if st_dir > 0:
        add("Supertrend", "Bullish", 5.0, 2.0)
    else:
        add("Supertrend", "Bearish", 5.0, 2.0)

    return rows


def overall_score(rows):
    """Calculates weighted directional score normalized to 0.0 – 10.0 scale."""
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
# INFLECTIONS & CHART BUILDER
# ──────────────────────────────────────────────
def find_inflections(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """Detects local peaks and troughs with relative strength scores."""
    if len(df) < window * 2 + 1:
        return pd.DataFrame(columns=["Date", "Price", "Type", "Score"])

    close = df["Close"].values
    idx = df.index
    records = []

    for i in range(window, len(close) - window):
        seg = close[i - window: i + window + 1]
        std = np.std(seg) + 1e-9
        if close[i] == np.max(seg):
            strength = (close[i] - np.mean(seg)) / std
            score = round(min(9.9, max(1.0, 3.0 + strength)), 1)
            records.append({"Date": idx[i], "Price": close[i], "Type": "Peak", "Score": score})
        if close[i] == np.min(seg):
            strength = (np.mean(seg) - close[i]) / std
            score = round(min(9.9, max(1.0, 3.0 + strength)), 1)
            records.append({"Date": idx[i], "Price": close[i], "Type": "Trough", "Score": score})

    return pd.DataFrame(records)


def build_chart(df: pd.DataFrame, infl_df: pd.DataFrame):
    """Builds interactive TradingView-style candlestick chart with SuperTrend ribbon."""
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

    # SuperTrend ribbon (dual-color Teal / Magenta)
    if "SUPERTd_10_3.0" in df.columns and "SUPERT_10_3.0" in df.columns:
        st_line = df["SUPERT_10_3.0"]
        st_dir = df["SUPERTd_10_3.0"]
        dirs = st_dir.ffill().fillna(1).values
        line = st_line.values
        dates = df.index

        bull_x, bull_y, bear_x, bear_y = [], [], [], []
        for i in range(len(dirs)):
            if dirs[i] > 0:
                bull_x.append(dates[i]); bull_y.append(line[i])
                bear_x.append(None); bear_y.append(None)
            else:
                bear_x.append(dates[i]); bear_y.append(line[i])
                bull_x.append(None); bull_y.append(None)

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

    # Rectangular block markers on recent swing peaks and troughs
    if not infl_df.empty:
        recent = infl_df.tail(8)
        for _, row in recent.iterrows():
            is_peak = row["Type"] == "Peak"
            bg = "#f23645" if is_peak else "#089981"
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

    # Hide weekend gaps for daily/weekly charts
    if len(df) > 0 and (df.index[-1] - df.index[0]).days > 5:
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

    return fig


def filter_period(df: pd.DataFrame, period: str, frequency: str, market: str = "IN") -> pd.DataFrame:
    """
    Filters chart dataframe for display:
    - For Intraday (< 1D): clips to the most recent active trading day in the market timezone.
    - For Daily/Weekly: filters by selected horizon period (7D, 1M, 1Y, 5Y, All).
    """
    if df.empty:
        return df

    is_intraday = frequency in ("5m", "15m", "30m", "1H", "3H")
    if is_intraday:
        # Market timezone normalization
        tz_target = "Asia/Kolkata" if market == "IN" else "America/New_York"
        idx = df.index
        if getattr(idx, "tz", None) is not None:
            dates = idx.tz_convert(tz_target).date
        else:
            dates = idx.date

        unique_dates = sorted(set(dates))
        if not unique_dates:
            return df
        latest_day = unique_dates[-1]
        return df.loc[[d == latest_day for d in dates]]

    if period == "All":
        return df

    days_map = {
        "7D": 7, "15D": 15, "1M": 30, "3M": 90, "6M": 180,
        "1Y": 365, "5Y": 365 * 5
    }
    days = days_map.get(period, None)
    if days is None:
        return df
    return df[df.index >= df.index[-1] - timedelta(days=days)]


# ──────────────────────────────────────────────
# DASHBOARD TAB RENDERER
# ──────────────────────────────────────────────
def render_market_dashboard(market: str = "IN"):
    """Renders self-contained dashboard view for INDIA or USA."""
    tickers_df = load_ticker_list(market)
    market_key = market.lower()
    currency_symbol = "₹" if market == "IN" else "$"

    # Default ticker selection
    default_symbol = "NIFTY" if market == "IN" else "^GSPC"
    default_idx = 0
    if default_symbol in tickers_df["SYMBOL"].values:
        default_idx = int(tickers_df[tickers_df["SYMBOL"] == default_symbol].index[0])

    # ── Control Row 1: Ticker Search & Frequency ──
    c1, c2 = st.columns([1.8, 3.2])
    with c1:
        search_label = "Search NSE ticker or index" if market == "IN" else "Search US ticker, index, or ETF"
        selected_label = st.selectbox(
            search_label,
            options=tickers_df["LABEL"].tolist(),
            index=default_idx,
            placeholder="Type to search… e.g. nift, reliance, aapl, spy",
            label_visibility="collapsed",
            key=f"ticker_select_{market_key}",
        )
        ticker = selected_label.split("—")[0].strip() if selected_label else default_symbol

    with c2:
        frequency = st.radio(
            "Frequency",
            options=["5m", "15m", "30m", "1H", "3H", "1D", "1W"],
            index=5,   # default 1D
            horizontal=True,
            label_visibility="collapsed",
            key=f"freq_{market_key}",
        )

    # ── Control Row 2: Horizon Filter (Daily / Weekly only) ──
    is_intraday = frequency in ("5m", "15m", "30m", "1H", "3H")
    if not is_intraday:
        period = st.radio(
            "Horizon",
            options=["7D", "15D", "1M", "3M", "6M", "1Y", "5Y", "All"],
            index=5 if frequency == "1D" else 7,
            horizontal=True,
            label_visibility="collapsed",
            key=f"horizon_{market_key}",
        )
    else:
        period = "All"

    if not ticker:
        st.warning("Please select a ticker.")
        return

    # Data Fetching & Full Indicator Computation
    with st.spinner(f"Loading {ticker} ({frequency})…"):
        full = fetch_stock_data(ticker, frequency=frequency, market=market)
        if full.empty:
            st.error(f"No price data found for '{ticker}' at {frequency}. Try 1D or another symbol.")
            return
        # Compute indicators across full warm-up history
        full = compute_indicators(full)

    # Chart dataset filtering
    chart_df = filter_period(full, period, frequency, market=market)

    # Intraday banner
    if is_intraday and not chart_df.empty:
        tz_target = "Asia/Kolkata" if market == "IN" else "America/New_York"
        day_str = chart_df.index[0].strftime("%d %b %Y")
        if getattr(chart_df.index[0], "tz", None) is not None:
            day_str = chart_df.index[0].tz_convert(tz_target).strftime("%d %b %Y")
        st.caption(f"Intraday ({frequency}) · Active trading day: **{day_str}** "
                   f"(market open to current time, or last session if closed)")

    # Latest Bar Metrics
    latest = full.iloc[-1]
    prev = full.iloc[-2]["Close"] if len(full) > 1 else latest["Close"]
    chg = latest["Close"] - prev
    chg_pct = (chg / prev * 100) if prev else 0.0
    up = chg >= 0

    price_cls = "price-up" if up else "price-down"
    sign = "+" if up else ""
    company_name = ""
    match = tickers_df[tickers_df["SYMBOL"] == ticker]
    if not match.empty:
        company_name = match.iloc[0]["NAME"]

    # Top Price Bar
    st.markdown(
        f"""
        <div class="top-bar">
            <span class="ticker-title">{ticker}</span>
            <span style="color:#787b86;font-size:0.85rem;">{company_name}</span>
            <span class="{price_cls}" style="font-size:1.3rem;">
                {currency_symbol}{latest['Close']:,.2f}
            </span>
            <span class="{price_cls}" style="font-size:0.9rem;">
                {sign}{currency_symbol}{abs(chg):,.2f} ({sign}{chg_pct:.2f}%)
            </span>
            <span style="color:#787b86;font-size:0.8rem;margin-left:10px;">
                O&nbsp;{latest['Open']:,.2f}&nbsp;&nbsp;
                H&nbsp;{latest['High']:,.2f}&nbsp;&nbsp;
                L&nbsp;{latest['Low']:,.2f}
            </span>
            <span style="color:#787b86;font-size:0.75rem;margin-left:auto;">
                {frequency} · {market}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Layout: Chart (Left) + Metrics Scoring (Right)
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

        data_time_str = full.index[-1].strftime('%d %b %Y %H:%M') if hasattr(full.index[-1], 'hour') else full.index[-1].strftime('%d %b %Y')
        st.markdown(
            f"<div style='margin-top:10px;font-size:0.72rem;color:#787b86;'>"
            f"Data as of {data_time_str} · Market: {market} · Real-time Feed</div>",
            unsafe_allow_html=True,
        )

    # Inflection Points Table
    st.markdown("---")
    st.markdown("##### Inflection Points History")
    if not infl_all.empty:
        display_tbl = infl_all.sort_values("Date", ascending=False).copy()
        display_tbl["Date"] = display_tbl["Date"].astype(str).str.slice(0, 16)
        display_tbl["Price"] = display_tbl["Price"].round(2)
        display_tbl["Type"] = display_tbl["Type"].map({"Peak": "▼ Peak", "Trough": "▲ Trough"})
        display_tbl = display_tbl.rename(columns={"Score": "Strength"})
        st.dataframe(display_tbl, use_container_width=True, hide_index=True,
                     height=min(340, 40 + 28 * len(display_tbl)))
    else:
        st.info("No clear inflection points found in the selected period.")


# ──────────────────────────────────────────────
# MAIN APPLICATION ROUTER
# ──────────────────────────────────────────────
def main():
    tab_in, tab_us = st.tabs(["🇮🇳 INDIA (NSE)", "🇺🇸 USA (NYSE / NASDAQ)"])

    with tab_in:
        render_market_dashboard(market="IN")

    with tab_us:
        render_market_dashboard(market="US")


if __name__ == "__main__":
    main()
