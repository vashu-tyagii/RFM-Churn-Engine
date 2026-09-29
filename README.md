# 🛒 E-Commerce RFM Customer Segmentation & Churn Engine

An end-to-end data analytics and business intelligence system built using **MySQL, Power BI, Python, and Streamlit**. This project cleans raw e-commerce transactional data, dynamically calculates Recency, Frequency, and Monetary (RFM) scores using SQL window functions, segmenting customers into actionable behavioral cohorts, and provides an executive churn-risk monitoring web app.

---

## 🎯 Business Problem & Objective
E-Commerce platforms suffer high customer acquisition costs (CAC) while losing existing high-value customers due to lack of early churn detection. 

**Key Objectives:**
- Segment customer base using RFM behavioral analytics.
- Identify "At-Risk" and "Lost" customer cohorts before complete churn.
- Provide executive leadership with interactive KPIs and automated churn warnings.

---

## 🛠️ Tech Stack & Skills
- **Database & Query Engineering:** MySQL Workbench (Window Functions, `NTILE`, Views, CTEs)
- **Data Processing & Scripting:** Python 3.10+, Pandas, NumPy, SQLAlchemy
- **Data Visualization & BI:** Power BI (DAX Modeling, Star Schema, Time Intelligence), Plotly Express
- **Web App & Deployment:** Streamlit, Streamlit Community Cloud, GitHub

---

## 📐 Analytics Architecture

1. **Database Processing (`MySQL`):**
   - Extracted transactional metrics (`Recency`, `Frequency`, `Monetary`).
   - Calculated percentile ranks via `NTILE(5) OVER(...)`.
   - Assigned dynamic segment tags (`Champions`, `Loyal`, `At-Risk`, `Lost`).

2. **Executive Reporting (`Power BI`):**
   - Constructed Star Schema linking RFM views with date & dimension tables.
   - Built DAX measures for Revenue Loss Risk, Churn Rate %, and Customer Lifetime Value.

3. **Web Application (`Streamlit`):**
   - Interactive filtering by customer segment.
   - Live revenue distribution visualizations using Plotly.

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repository
git clone [https://github.com/vashu-tyagii/project-1-rfm-churn-engine.git](https://github.com/vashu-tyagii/project-1-rfm-churn-engine.git)
cd project-1-rfm-churn-engine/streamlit_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Streamlit App
streamlit run app.py
