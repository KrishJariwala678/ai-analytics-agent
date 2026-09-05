import random
import duckdb
from faker import Faker
from datetime import date,timedelta

con = duckdb.connect("data/analytics.duckdb")

con.execute("DELETE FROM sessions")

# Reproducible randomness
random.seed(42)

# Faker instance
fake = Faker("en_IN")
fake.seed_instance(42)

# Region / City / Weight distribution
locations = [
    ("Maharashtra", "Mumbai", 30),
    ("Delhi", "New Delhi", 20),
    ("Karnataka", "Bangalore", 20),
    ("Tamil Nadu", "Chennai", 15),
    ("Gujarat", "Surat", 10),
    ("Madhya Pradesh", "Indore", 5),
]

# Generate 800 customers
customers = []

for customer_id in range(1, 801):

    region, city, _ = random.choices(
        locations,
        weights=[location[2] for location in locations],
        k=1
    )[0]

    customer = {
        "customer_id": customer_id,
        "name": fake.name(),
        "email": fake.email(),
        "region": region,
        "city": city,
        "created_date": fake.date_between(
            start_date=date(2024, 11, 1),
            end_date=date(2024, 12, 31)
        )
    }

    customers.append(customer)
 

product_categories = {
    "Formal Wear": [
        "Shirt",
        "Trousers",
        "Blazer",
        "Tie"
    ],
    "Footwear": [
        "Sneakers",
        "Sandals",
        "Boots",
        "Running Shoes"
    ],
    "Summer Wear": [
        "T-Shirt",
        "Shorts",
        "Cap",
        "Sundress"
    ],
    "Winter Wear": [
        "Jacket",
        "Sweater",
        "Muffler",
        "Thermal Set"
    ],
    "Swimwear": [
        "Swim Trunks",
        "Swimsuit",
        "Rash Guard",
        "Beach Shorts"
    ],
    "Fragrance": [
        "Eau de Parfum",
        "Body Mist",
        "Cologne",
        "Deodorant Spray"
    ]
}

# Price range per category
price_ranges = {
    "Formal Wear": (1500, 6000),
    "Footwear": (800, 4000),
    "Summer Wear": (400, 2000),
    "Winter Wear": (1200, 5000),
    "Swimwear": (600, 2500),
    "Fragrance": (500, 3000)
}

# Brand list
brands = [
    "Nike",
    "Adidas",
    "Puma",
    "Levi's",
    "Allen Solly",
    "Peter England",
    "Van Heusen",
    "Woodland"
]

# Generate 60 products
products = []

categories = list(product_categories.keys())

for product_id in range(1, 61):

    # Pick a category uniformly
    category = random.choice(categories)

    # Pick a brand
    brand = random.choice(brands)

    # Pick a category-appropriate product noun
    noun = random.choice(product_categories[category])

    # Construct product name
    product_name = f"{brand} {noun}"

    # Generate price based on category
    min_price, max_price = price_ranges[category]
    price = round(random.uniform(min_price, max_price), 2)

    # 90% active, 10% inactive
    is_active = random.random() < 0.9

    product = {
        "product_id": product_id,
        "product_name": product_name,
        "category": category,
        "brand": brand,
        "unit_price": price,
        "is_active": is_active
    }

    products.append(product)


marketing_channels = [
    {
        "marketing_channel_id" : 1,
        "channel_name" : "Paid Search",
        "channel_type" : "Paid",
        "source" : "Google ads"
    },
    {
        "marketing_channel_id" : 2,
        "channel_name" : "Organic Search",
        "channel_type" : "Organic",
        "source" : None
    },
    {
        "marketing_channel_id" : 3,
        "channel_name" : "Email",
        "channel_type" : "Owned",
        "source" : "Mailchimp"
    },
    {
        "marketing_channel_id" : 4,
        "channel_name" : "Social Media",
        "channel_type" : "Paid",
        "source" : "Instagram"
    },
    {
        "marketing_channel_id" : 5,
        "channel_name" : "Direct",
        "channel_type" : "Direct",
        "source" : None
    },
    {
        "marketing_channel_id" : 6,
        "channel_name" : "Referral",
        "channel_type" : "Referral",
        "source" : "Partner Site"
    }
]

## INSERTING VALUES IN MARKETING_CHANNEL TABLE
con.execute("DELETE FROM marketing_channels")
query3 = """
INSERT INTO marketing_channels (marketing_channel_id, channel_name, channel_type, source)
VALUES (?, ?, ?, ?)
"""

for row in marketing_channels:
    con.execute(query3, [
        row["marketing_channel_id"],
        row["channel_name"],
        row["channel_type"],
        row["source"]
    ])

print("marketing_channels inserted successfully.")

## INSERTING VALUES IN CUSTOMERS TABLE

con.execute("DELETE FROM customers")
query1 = """
INSERT INTO customers(customer_id,name,email,region,city,created_date)
VALUES(?,?,?,?,?,?)
"""
for row in customers:
    con.execute(query1,[
        row["customer_id"],
        row["name"],
        row["email"],
        row["region"],
        row["city"],
        row["created_date"]
    ])
print("customers inserted successfully.")

## INSERTING VALUES IN PRODUCTS TABLE
con.execute("DELETE FROM products")
query2 = """
INSERT INTO products(product_id,product_name, category,brand,unit_price,is_active)
VALUES(?,?,?,?,?,?)
"""
for row in products:
    con.execute(query2,[
        row["product_id"],
        row["product_name"],
        row["category"],
        row["brand"],
        row["unit_price"],
        row["is_active"]
    ])
print("products inserted successfully.")

## generating date_dim

end_date = date(2025,12,31)
start_date = date(2025,1,1)
date_dim = []
current_date = start_date
while current_date <= end_date:
    row = {
        "date_id": int(current_date.strftime("%Y%m%d")),
        "calendar_date":current_date,
        "year":current_date.year,
        "quarter":(current_date.month - 1) // 3 + 1,
        "month":current_date.month,
        "month_name" : current_date.strftime("%B"),
        "week" : current_date.isocalendar().week, 
        "day_of_week" : current_date.weekday(),
        "day_name" : current_date.strftime("%A")
    }  
    date_dim.append(row)
    current_date += timedelta(days=1)

con.execute("DELETE FROM date_dim")

query4 = """
INSERT INTO date_dim(date_id,calendar_date,year,quarter,month,month_name,week,day_of_week,day_name)
VALUES(?,?,?,?,?,?,?,?,?)
"""

for row in date_dim:
    con.execute(query4,[
        row["date_id"],
        row["calendar_date"],
        row["year"],
        row["quarter"],
        row["month"],
        row["month_name"],
        row["week"],
        row["day_of_week"],
        row["day_name"],
    ])

print("date_dim inserted successfully.")

## Sessions data

session_counts = [1,2,3,4,5,6,7,8]
session_count_weights = [20,20,18,15,10,8,5,4]

devices = ["Mobile","Desktop"]
device_weights = [60,40]

channel_ids = [1,2,3,4,5,6]
channel_weights = [25,30,10,15,15,5]

months = list(range(1,13))
month_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1.5]

sessions = []
session_id = 1

for cust in customers:
    num_sessions = random.choices(session_counts, weights = session_count_weights, k=1)[0]

    for _ in range(num_sessions):
        is_anonymous = random.random() < 0.15  # 15% anonymous

        if is_anonymous:
            customer_id = None
            region = random.choice(["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Madhya Pradesh", "West Bengal"])
            city = "Unknown"
        else:
            customer_id = cust["customer_id"]
            region = cust["region"]
            city = cust["city"]

        device = random.choices(devices, weights=device_weights, k=1)[0]
        marketing_channel_id = random.choices(channel_ids, weights=channel_weights, k=1)[0]

        # Pick a random month (weighted), then a random day within that month
        month = random.choices(months, weights=month_weights, k=1)[0]
        import calendar
        days_in_month = calendar.monthrange(2025, month)[1]
        day = random.randint(1, days_in_month)
        session_start_date = date(2025, month, day)
        session_end_date = session_start_date  # same day, for simplicity

        row = {
            "session_id": session_id,
            "customer_id": customer_id,
            "session_start_date": session_start_date,
            "session_end_date": session_end_date,
            "device": device,
            "region": region,
            "city": city,
            "marketing_channel_id": marketing_channel_id,
            "converted_order_id": None
        }
        sessions.append(row)
        session_id += 1

print(len(sessions))
print(sessions[0])
print(sessions[-1])


query = """
INSERT INTO sessions (session_id, customer_id, session_start_date, session_end_date, device, region, city, marketing_channel_id, converted_order_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

for row in sessions:
    con.execute(query, [
        row["session_id"],
        row["customer_id"],
        row["session_start_date"],
        row["session_end_date"],
        row["device"],
        row["region"],
        row["city"],
        row["marketing_channel_id"],
        row["converted_order_id"]
    ])

print("sessions inserted successfully.")

from collections import Counter
print(Counter(row["device"] for row in sessions))
print(Counter(row["customer_id"] is None for row in sessions))