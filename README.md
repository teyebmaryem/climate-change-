# 🌱 ClimateIQ — Climate Change & CO₂ Dashboard

**Scientific question:**
> *How have global CO₂ emissions evolved since 1980 — and what are their measurable consequences on temperature, sea level rise, and climate equity?*

---

## 📁 Project Structure

```
climate-dashboard/
├── streamlit_app.py          # Main dashboard
├── requirements.txt          # Python dependencies
├── 01_preprocessing.ipynb    # Data cleaning & preparation
├── 02_analysis.ipynb         # Static analysis & visualizations
├── qualite_donnees.md        # Data quality report
├── data/                     # Clean CSV files (exported from Kaggle)
│   ├── owid_clean.csv
│   ├── nasa_clean.csv
│   ├── sea_clean.csv
│   ├── disasters_clean.csv
│   └── global_merged.csv
└── README.md
```

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`

---

## 🌐 Live Dashboard

Deployed on Streamlit Cloud:
👉 **[your-app-url.streamlit.app]** ← replace after deployment

---

## 📦 Data Sources

| Dataset | Source | Period |
|---|---|---|
| OWID CO₂ Data | Our World in Data / Global Carbon Project | 1750–2022 |
| NASA GISS Temperature | NASA Goddard Institute | 1880–2023 |
| EPA Sea Level Rise | CSIRO + NOAA | 1880–2013 |
| EMDAT Natural Disasters | EM-DAT / OWID | 1900–2019 |
| IEA Data Centers | International Energy Agency | 2020–2035 |

---

## 👩‍💻 Author
Maryem Teyeb — Projet Python 2025/2026
