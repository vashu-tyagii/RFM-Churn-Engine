-- SQLite Table Creation for Sales Data
CREATE TABLE IF NOT EXISTS sales_data (
    Invoice TEXT,
    StockCode TEXT,
    Description TEXT,
    Quantity INTEGER,
    InvoiceDate TEXT,
    -- SQLite me Datetime TEXT format (YYYY-MM-DD HH:MM:SS) me store hota hai
    Price REAL,
    -- DECIMAL ki jagah REAL (Floating point)
    CustomerID TEXT,
    -- Space hata kar CustomerID kar diya (Avoid space issue)
    Country TEXT,
    TotalPrice REAL,
    Year INTEGER,
    Month INTEGER,
    MonthYear TEXT
);
-- Queries fast chalane ke liye Indexes create kar lete hain
CREATE INDEX IF NOT EXISTS idx_customer ON sales_data(CustomerID);
CREATE INDEX IF NOT EXISTS idx_invoicedate ON sales_data(InvoiceDate);