import random
import duckdb
from faker import Faker
from datetime import date

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

# Display first 10 customers
for customer in customers[:5]:
    print(customer)

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
        "price": price,
        "is_active": is_active
    }

    products.append(product)

# Display first 5 products
print("\nFirst 5 products:")
for product in products[:5]:
    print(product)

