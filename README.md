# Equity Trading Tools & Analytics

A collection of quantitative, technical, and analytical tools for equity trading and market analysis, organized into dedicated modular subfolders.

---

## 📁 Repository Structure

```text
Equity_Trading/
├── Technical Dashboard for Trading/    # Multi-timeframe technical metrics scoring & charting dashboard
│   ├── stock_Technicals_dashboard.py   # Main Streamlit application
│   ├── nse_tickers.csv                 # Database of NSE tickers and company names
│   ├── et_req.txt                      # Module dependencies
│   └── README.md                       # Comprehensive tool documentation
├── .gitignore                          # Global gitignore (ignores ppt/pptx, caches, etc.)
└── README.md                           # Repository overview
```

> Additional trading tools, algorithmic strategies, and analytics dashboards will be added in their respective subfolders.

---

## 📈 Tools in this Repository

### 1. [Technical Dashboard for Trading](./Technical%20Dashboard%20for%20Trading/)

A TradingView-inspired, real-time and historical Technical Analysis & Metrics Scoring Dashboard tailored for Indian equities (NSE) and benchmark indices.

- **Interactive Search:** Auto-complete across all NSE stocks and benchmark indices (`NIFTY 50`, `BANKNIFTY`, `FINNIFTY`, etc.).
- **Multi-Timeframe Support:** Intraday (`5m`, `15m`, `30m`, `1H`, `3H`) with smart 1-day session clipping (market open to current time, or previous full session on holidays/closed hours), and swing horizons (`1D`, `1W`) with selectable lookback periods (`7D` to `All`).
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
