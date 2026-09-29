SELECT COUNT(*) AS total_rows,
    COUNT(DISTINCT CustomerID) AS total_customers,
    MIN(InvoiceDate) AS min_date,
    MAX(InvoiceDate) AS max_date
FROM sales_data;