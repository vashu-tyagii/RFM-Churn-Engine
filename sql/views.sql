-- 1. CLEANED SALES VIEW
DROP VIEW IF EXISTS vw_cleaned_sales;
CREATE VIEW vw_cleaned_sales AS
SELECT Invoice,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    Price,
    CustomerID,
    Country,
    (Quantity * Price) AS TotalPrice
FROM sales_data
WHERE CustomerID IS NOT NULL
    AND CustomerID != ''
    AND Quantity > 0
    AND Price > 0;
-- 2. RFM METRICS VIEW
DROP VIEW IF EXISTS vw_rfm_metrics;
CREATE VIEW vw_rfm_metrics AS WITH reference_date AS (
    SELECT date(MAX(InvoiceDate), '+1 day') AS max_ref_date
    FROM vw_cleaned_sales
)
SELECT s.CustomerID,
    CAST(
        ROUND(
            julianday(r.max_ref_date) - julianday(MAX(s.InvoiceDate))
        ) AS INTEGER
    ) AS Recency,
    COUNT(DISTINCT s.Invoice) AS Frequency,
    ROUND(SUM(s.TotalPrice), 2) AS Monetary
FROM vw_cleaned_sales s
    CROSS JOIN reference_date r
GROUP BY s.CustomerID;
-- 3. RFM SCORES VIEW
DROP VIEW IF EXISTS vw_rfm_scores;
CREATE VIEW vw_rfm_scores AS
SELECT CustomerID,
    Recency,
    Frequency,
    Monetary,
    NTILE(5) OVER (
        ORDER BY Recency DESC
    ) AS R_Score,
    NTILE(5) OVER (
        ORDER BY Frequency ASC
    ) AS F_Score,
    NTILE(5) OVER (
        ORDER BY Monetary ASC
    ) AS M_Score
FROM vw_rfm_metrics;
-- 4. RFM FINAL SEGMENTS VIEW
DROP VIEW IF EXISTS vw_rfm_final_segments;
CREATE VIEW vw_rfm_final_segments AS
SELECT CustomerID,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    CAST(R_Score AS TEXT) || CAST(F_Score AS TEXT) || CAST(M_Score AS TEXT) AS RFM_Cell,
    CASE
        WHEN R_Score >= 4
        AND F_Score >= 4
        AND M_Score >= 4 THEN 'Champions'
        WHEN F_Score >= 4 THEN 'Loyal Customers'
        WHEN R_Score >= 4
        AND F_Score >= 2 THEN 'Potential Loyalists'
        WHEN R_Score >= 4
        AND F_Score = 1 THEN 'New Customers'
        WHEN R_Score <= 2
        AND F_Score >= 3 THEN 'At Risk (Churn Warning)'
        WHEN R_Score <= 2
        AND F_Score <= 2 THEN 'Lost / Hibernating'
        ELSE 'Needs Attention'
    END AS Customer_Segment
FROM vw_rfm_scores;
-- 5. COHORT BASE VIEW
DROP VIEW IF EXISTS vw_cohort_base;
CREATE VIEW vw_cohort_base AS WITH customer_first_purchase AS (
    SELECT CustomerID,
        MIN(InvoiceDate) AS first_purchase_date,
        strftime('%Y-%m-01', MIN(InvoiceDate)) AS cohort_month
    FROM vw_cleaned_sales
    GROUP BY CustomerID
)
SELECT s.CustomerID,
    cfp.cohort_month,
    strftime('%Y-%m-01', s.InvoiceDate) AS purchase_month,
    (
        (
            CAST(strftime('%Y', s.InvoiceDate) AS INTEGER) - CAST(
                strftime('%Y', cfp.first_purchase_date) AS INTEGER
            )
        ) * 12
    ) + (
        CAST(strftime('%m', s.InvoiceDate) AS INTEGER) - CAST(
            strftime('%m', cfp.first_purchase_date) AS INTEGER
        )
    ) AS cohort_index
FROM vw_cleaned_sales s
    JOIN customer_first_purchase cfp ON s.CustomerID = cfp.CustomerID;
-- 6. COHORT RETENTION VIEW
DROP VIEW IF EXISTS vw_cohort_retention;
CREATE VIEW vw_cohort_retention AS
SELECT cohort_month,
    cohort_index,
    COUNT(DISTINCT CustomerID) AS active_customers
FROM vw_cohort_base
GROUP BY cohort_month,
    cohort_index
ORDER BY cohort_month,
    cohort_index;