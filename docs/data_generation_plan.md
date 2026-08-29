### The table-by-table volume plan
customers: 800
products: 60
marketing_channels: 6(paid search, organic search, email, social media, direct, referral)
date_dim: every calendar date across your chosen time window (e.g., 12 months = 365 rows) — this one isn't "generated" randomly, it's mechanically produced from a date range
sessions: 3500
orders: 400
order_items: 840
payments: 480

### Finalized region list
Maharashtra	- Mumbai
Delhi -	New Delhi
Karnataka -	Bangalore
Tamil Nadu - Chennai
Gujarat - Surat
Madhya Pradesh - Indore

Anomaly target: Maharashtra / Mumbai

### Anomaly injection spec
Analysis window: 2025-01-01 to 2025-12-31 (full 12 months — governs date_dim, sessions, orders, order_items, and payments)
Anomaly window: June 10–14, 2025 (5 days), roughly mid-year so there's baseline data before and after
Segment: device = 'mobile', state = 'Maharashtra', city = 'Mumbai', payment_method = 'UPI'
Baseline UPI failure rate: 5%
Injected failure rate during the window: 38%

### Data-quality noise

customers.email missing: 2% (~16 of 800 customers)
Duplicate orders rows: 12 exact duplicates
Invalid dates: 5 sessions where session_end_date < session_start_date
Invalid numeric values: 8 order_items rows with quantity = 0

### Random seed: 42