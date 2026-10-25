# Stock Technicals Dashboard

A TradingView-inspired, real-time and historical Technical Analysis & Metrics Scoring Dashboard tailored for Indian equities (NSE) and benchmark indices. Built with **Streamlit**, **Plotly**, **yfinance**, and **pandas-ta**.

---

## 🌟 Key Features

- **Interactive Ticker Search:**
  - Fast, auto-complete search across all National Stock Exchange (NSE) listed stocks and major indices (`NIFTY 50`, `BANKNIFTY`, `FINNIFTY`, `SENSEX`, `INDIAVIX`).
  - Powered by a local symbol directory (`nse_tickers.csv`) mapping ticker symbols to full company names.

- **Dynamic Timeframe & Horizon Control:**
  - **Intraday Timeframes:** `5m`, `15m`, `30m`, `1H`, `3H` (resampled).
  - **Swing Timeframes:** `1D`, `1W` (with up to 5 years of historical data).
  - **Smart Session Management for Intraday:** Automatically bounds intraday data to the latest active trading session (IST) — from market open to current time, or the full previous session if the market is closed or on a holiday.
  - **Horizon Filter for Daily/Weekly:** Quick lookback selection across `7D`, `15D`, `1M`, `3M`, `6M`, `1Y`, `5Y`, and `All`.

- **TradingView-Inspired Minimalist Charting:**
  - Clean, light-themed OHLC candlestick chart with crosshairs and right-aligned price scale.
  - **Dual-Colored SuperTrend Ribbon:** Smooth trendline indicating market regime (Teal `#26a69a` for Bullish, Magenta/Pink `#e91e63` for Bearish).
  - **Inflection Point Badges:** Clean rectangular badge markers with arrows pinpointing recent local swing peaks (red) and troughs (green) with local strength scores.
  - Automatic weekend gap removal for daily/weekly charts.

- **Regime-Aware Metrics Scoring Engine:**
  - Analyzes 10 key technical indicators under the context of the current SuperTrend market regime.
  - Evaluates signal direction (`Bullish`, `Bearish`, `Neutral`), individual strength scores (`1.0` – `5.0`), and assigned weights (`0.8` – `2.0`).
  - Aggregates an **Overall Market Score** out of 10 with clear visual classifications:
    - 🟢 **Strong Bullish** / **Bullish**
    - ⚪ **Neutral / Mixed**
    - 🔴 **Bearish** / **Strong Bearish**

- **Inflection Points History:**
  - Tabular log at the bottom tracking historical swing highs (▼ Peak) and lows (▲ Trough) along with their localized strength metrics.

---

## 📊 Technical Indicators & Scoring Breakdown

The metrics panel evaluates the following indicators in real time:

| Indicator | Default Settings | Weight | Description & Scoring Highlights |
| :--- | :--- | :---: | :--- |
| **SuperTrend** | Length: 10, Multiplier: 3.0 | `2.0` | Primary regime driver; sets baseline bias. |
| **MACD** | Fast: 12, Slow: 26, Signal: 9 | `1.2` | Evaluates histogram magnitude and signal crossovers. |
| **RSI** | Length: 14 | `1.0 - 1.2` | Overbought (≥70) / Oversold (≤30) with regime sensitivity. |
| **Stochastic** | %K: 14, %D: 3, Smooth: 3 | `0.9 - 1.0` | Overbought (≥80) / Oversold (≤20) threshold signals. |
| **DMI / ADX** | Length: 14 | `1.2 - 1.5` | Directional movement differential (`+DI` vs `-DI`) scaled by ADX strength. |
| **Parabolic SAR** | Step: 0.02, Max: 0.2 | `1.2 - 1.5` | Trend stop-and-reverse level comparison. |
| **Momentum (MOM)** | Length: 10 | `1.0 - 1.2` | Price percentage rate of change. |
| **Money Flow Index (MFI)** | Length: 14 | `0.8 - 1.0` | Volume-weighted overbought/oversold boundaries. |
| **Vortex Indicator** | Length: 14 | `0.9` | Positive (`+VI`) vs. Negative (`-VI`) trend direction. |
| **Fisher Transform** | Length: 9 | `0.8 - 1.0` | Gaussian normalized turning points. |

---

## 🛠️ Project Structure

```text
Equity_Trading/
├── stock_Technicals_dashboard.py   # Main Streamlit dashboard application
├── nse_tickers.csv                 # Master database of NSE tickers and company names
├── et_req.txt                      # Python library dependencies
├── .gitignore                      # Git ignore file (excludes ppt, pptx, caches, etc.)
└── README.md                       # Documentation and usage guide
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/GradientDescentMadness/Equity_Trading.git
cd Equity_Trading
```

### 3. Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r et_req.txt
```

*(Core dependencies: `streamlit`, `yfinance`, `pandas-ta`, `plotly`, `pandas`, `numpy`)*

### 4. Run the Dashboard
Launch the dashboard locally:
```bash
streamlit run stock_Technicals_dashboard.py
```
Open your browser at `http://localhost:8501`.

---

## ⚙️ Usage Guide

1. **Search a Stock/Index:** Type ticker symbol or company name in the search box (e.g. `nift`, `RELIANCE`, `HDFCBANK`).
2. **Choose Timeframe:** Select between intraday (`5m`, `15m`, `30m`, `1H`, `3H`) or swing horizons (`1D`, `1W`).
3. **Select Lookback Window:** For daily/weekly data, toggle between `7D`, `15D`, `1M`, `3M`, `6M`, `1Y`, `5Y`, or `All`.
4. **Inspect Metrics:** Review the live scoring breakdown on the right panel to assess market alignment across multiple indicators.
5. **View Inflection History:** Inspect the table at the bottom to check historical swing highs and lows with their relative strength.

---

## 📄 License
This project is for personal analysis and educational purposes. Market data provided by Yahoo Finance.
