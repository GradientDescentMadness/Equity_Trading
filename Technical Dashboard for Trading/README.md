# Stock Technicals Dashboard (India & USA)

A TradingView-inspired, real-time and historical Technical Analysis & Metrics Scoring Dashboard supporting both **Indian Equities (NSE)** and **US Equities (NYSE / NASDAQ)**. Built with **Streamlit**, **Plotly**, and **pandas-ta**.

---

## 🌟 Key Features

- **Multi-Market Support via Dedicated Tabs:**
  - 🇮🇳 **INDIA (NSE):** Dedicated tab for Indian benchmark indices (`NIFTY 50`, `BANKNIFTY`, `FINNIFTY`, `MIDCPNIFTY`, `NIFTY IT`, etc.) and all NSE-listed stocks, with currency formatting in `₹` and `Asia/Kolkata` market hours.
  - 🇺🇸 **USA (NYSE / NASDAQ):** Dedicated tab for US benchmark indices (`S&P 500`, `Dow Jones`, `NASDAQ`, `Russell 2000`, `VIX`), major ETFs (`SPY`, `QQQ`, `IWM`, sector SPDRs), and top US equities (`AAPL`, `NVDA`, `MSFT`, `AMZN`, `TSLA`, etc.), formatted in `$` and `America/New_York` market hours.

- **Resilient Direct Feed Architecture:**
  - Integrated high-speed, crumb-free direct chart API with User-Agent management to bypass Yahoo Finance rate-limiting (HTTP 429) and cookie crumb errors.
  - Automatic BSE fallback (`.BO`) for Indian stocks and alias resolution for demerged/renamed tickers (e.g. `TATAMOTORS` → `TMPV`, `ZOMATO` → `ETERNAL`, `AMARAJABAT` → `ARE&M`).

- **Dynamic Timeframe & Horizon Control:**
  - **Intraday Intervals:** `5m`, `15m`, `30m`, `1H`, `3H` (resampled).
  - **Swing Intervals:** `1D`, `1W` (with up to 5 years of historical data).
  - **Intraday Session Isolation:** For intraday frequencies (< 1D), indicators are computed on full historical warm-up data, while the chart display is cleanly bounded to the latest active trading session.
  - **Selectable Lookback Horizons:** When analyzing daily or weekly data, choose across `7D`, `15D`, `1M`, `3M`, `6M`, `1Y`, `5Y`, or `All`.

- **TradingView-Inspired Minimalist Charting:**
  - High-contrast, clean light-mode candlestick chart with crosshairs and right-aligned price scale.
  - **Dual-Colored SuperTrend Ribbon:** Smooth trendline indicating market regime (Teal `#26a69a` for Bullish, Magenta `#e91e63` for Bearish).
  - **Inflection Point Badges:** Clean rectangular badge markers with directional arrows pinpointing recent local swing peaks (red) and troughs (green) with local strength scores.
  - Automatic weekend gap removal for daily/weekly charts.

- **Regime-Aware Metrics Scoring Engine:**
  - Evaluates 10 core technical indicators against the prevailing SuperTrend regime.
  - Calculates signal direction (`Bullish`, `Bearish`, `Neutral`), individual strength scores (`1.0` – `5.0`), and assigned weights (`0.8` – `2.0`).
  - Aggregates an **Overall Market Score** out of 10 with colored classifications:
    - 🟢 **Strong Bullish** / **Bullish**
    - ⚪ **Neutral / Mixed**
    - 🔴 **Bearish** / **Strong Bearish**

- **Inflection Points History:**
  - Tabular log at the bottom tracking historical swing highs (▼ Peak) and lows (▲ Trough) along with their localized strength metrics.

---

## 📊 Technical Indicators & Scoring Breakdown

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
Technical Dashboard for Trading/
├── stock_Technicals_dashboard.py   # Multi-market Streamlit dashboard application
├── nse_tickers.csv                 # Master database of NSE tickers, indices, and aliases
├── us_tickers.csv                  # 100% verified database of US indices, ETFs, and stocks
├── et_req.txt                      # Python library dependencies
└── README.md                       # Comprehensive documentation and usage guide
```

---

## 🚀 Installation & Setup

```bash
cd "Technical Dashboard for Trading"
pip install -r et_req.txt
streamlit run stock_Technicals_dashboard.py
```
Open your browser at `http://localhost:8501`.
