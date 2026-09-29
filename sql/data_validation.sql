-- 1. General Health Check & Data Profiling
SELECT COUNT(*) AS total_rows,
    COUNT(DISTINCT CustomerID) AS total_customers,
    COUNT(
        CASE
            WHEN CustomerID IS NULL THEN 1
        END
    ) AS null_customers,
    MIN(InvoiceDate) AS min_date,
    MAX(InvoiceDate) AS max_date
FROM sales_data;
-- 2. Validate Negative or Zero Quantities/Prices (Data Cleaning Check)
SELECT COUNT(
        CASE
            WHEN Quantity <= 0 THEN 1
        END
    ) AS invalid_quantity_rows,
    COUNT(
        CASE
            WHEN UnitPrice <= 0 THEN 1
        END
    ) AS invalid_price_rows
FROM sales_data;