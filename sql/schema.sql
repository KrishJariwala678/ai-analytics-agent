CREATE TABLE IF NOT EXISTS date_dim(
    date_id INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL   
);

CREATE TABLE IF NOT EXISTS marketing_channels(
    marketing_channel_id INTEGER PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(100) NOT NULL,
    source VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS customers(
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL,
    region VARCHAR(30) NOT NULL,
    city VARCHAR(30) NOT NULL,
    created_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    category VARCHAR(30) NOT NULL,
    brand VARCHAR(30) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN NOT NULL
);


CREATE TABLE IF NOT EXISTS orders(
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    device VARCHAR(30) NOT NULL,
    region VARCHAR(30) NOT NULL,
    city VARCHAR(30) NOT NULL,
    attributed_channel_id INTEGER,
    order_status VARCHAR(20) NOT NULL,
    order_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (attributed_channel_id) REFERENCES marketing_channels(marketing_channel_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS payments(
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    payment_timestamp TIMESTAMP NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    failure_reason VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL,
    gateway VARCHAR(50) NOT NULL,
    attempt_number INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS sessions(
    session_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    session_start_date DATE NOT NULL,
    session_end_date DATE NOT NULL,
    device VARCHAR(30) NOT NULL,
    region VARCHAR(30) NOT NULL,
    city VARCHAR(30) NOT NULL,
    marketing_channel_id INTEGER,
    converted_order_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (marketing_channel_id) REFERENCES marketing_channels(marketing_channel_id),
    FOREIGN KEY (converted_order_id) REFERENCES orders(order_id)
);