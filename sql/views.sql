CREATE OR REPLACE VIEW vw_cleaned_sales AS
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
-- 
CREATE OR REPLACE VIEW vw_rfm_metrics AS WITH reference_date AS (
        SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) AS max_ref_date
        FROM vw_cleaned_sales
    )
    SELECT s.CustomerID,
    DATEDIFF(MAX(r.max_ref_date), MAX(s.InvoiceDate)) AS Recency,
    COUNT(DISTINCT s.Invoice) AS Frequency,
    ROUND(SUM(s.TotalPrice), 2) AS Monetary
    FROM vw_cleaned_sales s
    CROSS JOIN reference_date r
    GROUP BY s.CustomerID;
--
CREATE OR REPLACE VIEW vw_rfm_scores AS
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
--
CREATE OR REPLACE VIEW vw_rfm_final_segments AS
    SELECT CustomerID,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    CONCAT(R_Score, F_Score, M_Score) AS RFM_Cell,
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
--
-- SELECT 
--     Customer_Segment,
--     COUNT(*) AS Total_Customers,
--     ROUND(AVG(Monetary), 2) AS Avg_Spend,
--     ROUND(AVG(Recency), 0) AS Avg_Recency_Days
--     FROM vw_rfm_final_segments
--     GROUP BY Customer_Segment
--     ORDER BY Total_Customers DESC;
--
CREATE OR REPLACE VIEW vw_cohort_base AS
    WITH customer_first_purchase AS (
    -- Har customer ki pehli purchase date/month nikalna
    SELECT 
        CustomerID,
        MIN(InvoiceDate) AS first_purchase_date,
        DATE_FORMAT(MIN(InvoiceDate), '%Y-%m-01') AS cohort_month
    FROM vw_cleaned_sales
    GROUP BY CustomerID
    )
    SELECT 
    s.CustomerID,
    cfp.cohort_month,
    DATE_FORMAT(s.InvoiceDate, '%Y-%m-01') AS purchase_month,
    -- Cohort Index: Pehli purchase se kitne mahine baad order kiya (0, 1, 2, 3...)
    PERIOD_DIFF(
        DATE_FORMAT(s.InvoiceDate, '%Y%m'), 
        DATE_FORMAT(cfp.first_purchase_date, '%Y%m')
    ) AS cohort_index
    FROM vw_cleaned_sales s
    JOIN customer_first_purchase cfp ON s.CustomerID = cfp.CustomerID;
--
CREATE OR REPLACE VIEW vw_cohort_retention AS
    SELECT 
    cohort_month,
    cohort_index,
    COUNT(DISTINCT CustomerID) AS active_customers
    FROM vw_cohort_base
    GROUP BY cohort_month, cohort_index
    ORDER BY cohort_month, cohort_index;
--
SELECT 
    cohort_month,
    MAX(CASE WHEN cohort_index = 0 THEN active_customers END) AS Month_0,
    MAX(CASE WHEN cohort_index = 1 THEN active_customers END) AS Month_1,
    MAX(CASE WHEN cohort_index = 2 THEN active_customers END) AS Month_2,
    MAX(CASE WHEN cohort_index = 3 THEN active_customers END) AS Month_3,
    MAX(CASE WHEN cohort_index = 4 THEN active_customers END) AS Month_4,
    MAX(CASE WHEN cohort_index = 5 THEN active_customers END) AS Month_5
FROM vw_cohort_retention
GROUP BY cohort_month
ORDER BY cohort_month ASC;