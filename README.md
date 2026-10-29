# Equity Trading Tools & Analytics

A collection of quantitative, technical, and analytical tools for equity trading and market analysis, organized into dedicated modular subfolders.

---

## 📁 Repository Structure

```text
Equity_Trading/
├── Technical Dashboard for Trading/    # Multi-market technical metrics scoring & charting dashboard
│   ├── stock_Technicals_dashboard.py   # Main Streamlit application (INDIA & USA tabs)
│   ├── nse_tickers.csv                 # Database of NSE tickers, indices, and aliases
│   ├── us_tickers.csv                  # Verified database of US indices, ETFs, and equities
│   ├── et_req.txt                      # Module dependencies
│   └── README.md                       # Comprehensive tool documentation
├── .gitignore                          # Global gitignore (ignores ppt/pptx, caches, etc.)
└── README.md                           # Repository overview
```

> Additional trading tools, algorithmic strategies, and analytics dashboards will be added in their respective subfolders.

---

## 📈 Tools in this Repository

### 1. [Technical Dashboard for Trading](./Technical%20Dashboard%20for%20Trading/)

A TradingView-inspired, real-time and historical Technical Analysis & Metrics Scoring Dashboard supporting both **Indian Equities (NSE)** and **US Equities (NYSE / NASDAQ)**.

- **Dual Market Tabs:**
  - 🇮🇳 **INDIA:** Full support for Indian indices (`NIFTY 50`, `BANKNIFTY`, `FINNIFTY`, `MIDCPNIFTY`, `NIFTY IT`, etc.) and NSE equities, with `₹` currency and `Asia/Kolkata` market hours.
  - 🇺🇸 **USA:** Full support for US indices (`S&P 500`, `Dow Jones`, `NASDAQ`, `Russell 2000`, `VIX`), major ETFs (`SPY`, `QQQ`, `IWM`, sector SPDRs), and leading stocks (`AAPL`, `NVDA`, `MSFT`, `TSLA`, etc.), with `$` currency and `America/New_York` market hours.
- **Resilient Direct Feed:** High-speed crumb-free API with custom User-Agent to prevent Yahoo Finance HTTP 429 rate limits, plus automatic BSE fallback (`.BO`) and alias resolution for renamed/demerged tickers (`TATAMOTORS`, `ZOMATO`, `AMARAJABAT`, etc.).
- **Multi-Timeframe Analysis:** Intraday (`5m`, `15m`, `30m`, `1H`, `3H`) with single-day session isolation, and swing horizons (`1D`, `1W`) with selectable lookback periods (`7D` to `All`).
- **Clean TradingView Aesthetics:** High-contrast light UI, dual-colored SuperTrend ribbon (Teal for Bullish, Pink for Bearish), and rectangular badge markers for local swing peaks and troughs.
- **Regime-Aware Metrics Scoring:** 10 core technical indicators evaluated under the prevailing SuperTrend regime to produce individual scores (1–5), weights, and an aggregate **Market Score** out of 10 (`Strong Bullish` to `Strong Bearish`).
- **Inflection Points History:** Tabular history logging historical peaks and troughs with relative strength scores.

#### Quickstart:
```bash
cd "Technical Dashboard for Trading"
pip install -r et_req.txt
streamlit run stock_Technicals_dashboard.py
```

*For complete details, scoring formulas, and indicator breakdown, see the [Technical Dashboard Documentation](./Technical%20Dashboard%20for%20Trading/README.md).*

---

## 📄 License
This repository is for research and educational purposes. Market data provided by Yahoo Finance.
