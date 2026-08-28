# Schema Design

This schema uses a star-schema-friendly design: transactional events live in fact-like tables, while reusable descriptive entities live in dimension tables.

## Table list

| Table | Decision | Justification |
|---|---|---|
| `customers` | Keep | Customer attributes belong in one reusable entity table and can be referenced by orders and sessions. |
| `products` | Keep | Product attributes should be stored once rather than repeated on every order line. |
| `orders` | Keep | An order is the business-level transaction/header and needs its own identity, purchase-time context, and lifecycle. |
| `order_items` | Keep | An order can contain multiple products, so line-level facts need a separate grain. |
| `payments` | Keep | Payment attempts are separate events from placing an order and can occur later or be retried. |
| `sessions` | Keep | A session represents a user visit/interaction period and has a different grain from orders. |
| `marketing_channels` | Keep | Marketing-channel attributes should be stored once and referenced rather than repeated as free text. |
| `date_dim` | Keep | A shared date dimension supports consistent time-based analysis and calendar attributes. |

## Grain and primary key

### `customers`

- **Grain:** One row represents one customer.
- **Primary key:** `customer_id`

### `products`

- **Grain:** One row represents one product/SKU.
- **Primary key:** `product_id`

### `orders`

- **Grain:** One row represents one customer order (order header), regardless of how many products are in it.
- **Primary key:** `order_id`

### `order_items`

- **Grain:** One row represents one product line within one order.
- **Primary key:** `order_item_id`

### `payments`

- **Grain:** One row represents one payment attempt/transaction associated with an order.
- **Primary key:** `payment_id`

### `sessions`

- **Grain:** One row represents one customer/user session.
- **Primary key:** `session_id`

### `marketing_channels`

- **Grain:** One row represents one marketing channel.
- **Primary key:** `marketing_channel_id`

### `date_dim`

- **Grain:** One row represents one calendar date.
- **Primary key:** `date_id`

## Full column list

Types are intentionally rough at this design stage; exact SQL types will be selected during DDL.

### `customers`

| Column | Type | Description |
|---|---|---|
| `customer_id` | number | Unique identifier for the customer. |
| `name` | text | Customer's name. |
| `email` | text | Customer's email address. |
| `region` | text | Customer's current region/state/market. |
| `city` | text | Customer's current city. |
| `created_date` | date | Date the customer account was created. |

**Design note:** `region` and `city` here describe the customer's **current** location, not necessarily their location when an order happened.

### `products`

| Column | Type | Description |
|---|---|---|
| `product_id` | number | Unique identifier for the product/SKU. |
| `product_name` | text | Product name. |
| `category` | text | Product category. |
| `brand` | text | Product brand. |
| `unit_price` | number | Current/list price of the product. |
| `is_active` | boolean | Whether the product is currently active. |

### `orders`

| Column | Type | Description |
|---|---|---|
| `order_id` | number | Unique identifier for the order. |
| `customer_id` | number | Customer who placed the order. |
| `order_date` | date | Date the order was placed. |
| `device` | text | Device used at purchase, such as mobile or desktop. |
| `region` | text | Region/state at the time of purchase. |
| `city` | text | City at the time of purchase. |
| `attributed_channel_id` | number | Marketing channel attributed to the order under the chosen attribution rule. |
| `order_status` | text | Overall order state, such as placed, cancelled, or completed. |
| `order_total` | number | Total monetary value of the order. |

**Design decisions:**
- `device` lives on `orders` because the RCA use case needs the device associated with the purchase itself. It also lives on `sessions` because browsing/device behavior is useful independently.
- `region` and `city` are intentionally **snapshotted on `orders`**. This preserves the customer's location at purchase time even if the customer's current location later changes.
- `attributed_channel_id` gives us an order-level channel for analysis. The simplifying assumption is **last-touch attribution**: attribute the order to the most recent marketing session that led to the purchase, when such a session is available.
- `order_total` **stays stored** on `orders` rather than being dropped in favor of a `SUM(order_items.line_total)` query. This keeps order-level aggregate queries (average order value, revenue trends) cheap and avoids a join through `order_items` for the most common analytical question. `order_items.line_total` remains the **source of truth**: `order_total` must always equal the sum of its order's `line_total` values. See "Keeping `order_total` consistent" below for how that invariant is maintained.

### `order_items`

| Column | Type | Description |
|---|---|---|
| `order_item_id` | number | Unique identifier for the order line. |
| `order_id` | number | Parent order containing this line. |
| `product_id` | number | Product/SKU purchased on this line. |
| `quantity` | number | Number of units purchased. |
| `unit_price` | number | Price per unit at the time of purchase. |
| `line_total` | number | Total value of this order line. |

**Date decision:** No `date_id` is stored here. The line item is part of the parent order and does not represent an independent event in this model, so its order date can be obtained through `order_id → orders.order_date → date_dim`. This avoids a redundant FK that could disagree with the parent order.

**Keeping `order_total` consistent:** rather than enforcing the `orders.order_total = SUM(order_items.line_total)` invariant with a database trigger or a post-load reconciliation step, the ingestion/generation script keeps the two **consistent by construction**: it generates each order's `order_items` rows first, computes `order_total` as the sum of their `line_total` values, and only then writes the `orders` row using that computed sum. Because `order_total` is never independently authored, it cannot drift out of sync with its line items.

### `payments`

| Column | Type | Description |
|---|---|---|
| `payment_id` | number | Unique identifier for the payment attempt. |
| `order_id` | number | Order associated with the payment attempt. |
| `payment_timestamp` | timestamp | Date and time of the payment attempt. |
| `payment_method` | text | Method used, such as UPI, card, or net banking. |
| `payment_status` | text | Result/state such as success, failed, pending, or refunded. |
| `failure_reason` | text | Reason/category recorded when a payment fails. |
| `amount` | number | Amount attempted or processed. |
| `gateway` | text | Payment gateway/provider handling the attempt. |
| `attempt_number` | number | Retry/attempt sequence for the order payment. |

**Date decision:** `payments` genuinely needs its own date because payment attempts can happen after the order is placed, and retries/failures can occur on later dates. A payment attempt is therefore an independent event.

**Why `payment_timestamp` and not `payment_date`:** a single order's payment retries frequently happen on the **same calendar day** (e.g. a failed attempt followed by a successful retry minutes later). A date-only column can't distinguish those attempts' ordering or measure time-to-retry, so the column stores full timestamp precision instead. `date_dim` is still reachable for calendar-level analysis by deriving the calendar date from `payment_timestamp` (e.g. `DATE(payment_timestamp) → date_dim.calendar_date`); it just isn't a direct date-typed FK column anymore.

### `sessions`

| Column | Type | Description |
|---|---|---|
| `session_id` | number | Unique identifier for the browsing/session period. |
| `customer_id` | number | Customer/user associated with the session, when known. |
| `session_start_date` | date | Date/time when the session started. |
| `session_end_date` | date | Date/time when the session ended. |
| `device` | text | Device used during the session, such as mobile or desktop. |
| `region` | text | Region associated with the session. |
| `city` | text | City associated with the session. |
| `marketing_channel_id` | number | Marketing channel that generated the session. |
| `converted_order_id` | number | Order generated by this session, when applicable. |

**Date decision:** `sessions` needs its own date because a browsing session is an independent event and may occur on a different date from any order it eventually influences.

### `marketing_channels`

| Column | Type | Description |
|---|---|---|
| `marketing_channel_id` | number | Unique identifier for the marketing channel. |
| `channel_name` | text | Channel name, such as paid search, organic, email, or social. |
| `channel_type` | text | Broader grouping of the channel. |
| `source` | text | Traffic/source platform when available. |

### `date_dim`

| Column | Type | Description |
|---|---|---|
| `date_id` | number | Surrogate identifier for the calendar date. |
| `calendar_date` | date | Actual calendar date. |
| `year` | number | Calendar year. |
| `quarter` | number | Calendar quarter. |
| `month` | number | Calendar month. |
| `month_name` | text | Human-readable month name. |
| `week` | number | Calendar week number. |
| `day_of_week` | number | Numeric day of week. |
| `day_name` | text | Human-readable day name. |

## Foreign key relationships

```text
customers
    │
    ├──< orders
    │      │
    │      ├──< order_items >── products
    │      │
    │      ├──< payments
    │      │
    │      └──> marketing_channels
    │
    └──< sessions >── marketing_channels
              │
              └──> orders (converted_order_id)

date_dim
    ├──< orders.order_date
    ├──< payments.payment_timestamp (via DATE(payment_timestamp))
    └──< sessions.session_start_date

order_items do NOT directly reference date_dim.
Their date is inherited through:
order_items → orders → date_dim
```

More explicitly:

- `orders.customer_id` → `customers.customer_id`
- `order_items.order_id` → `orders.order_id`
- `order_items.product_id` → `products.product_id`
- `payments.order_id` → `orders.order_id`
- `sessions.customer_id` → `customers.customer_id`
- `sessions.marketing_channel_id` → `marketing_channels.marketing_channel_id`
- `orders.attributed_channel_id` → `marketing_channels.marketing_channel_id`
- `sessions.converted_order_id` → `orders.order_id`
- `orders.order_date` → `date_dim.calendar_date`
- `payments.payment_timestamp` (date part) → `date_dim.calendar_date`
- `sessions.session_start_date` → `date_dim.calendar_date`

## Which tables genuinely need their own date?

The rule is: **give a table its own date when its row represents an independent event that can occur on a different date from its parent.**

| Table | Own date? | Reason |
|---|---|---|
| `orders` | Yes | The order itself is a business event with an order/placement date. |
| `order_items` | No | In this model, an order item is a component of the order, not an independent dated event. |
| `payments` | Yes (as timestamp) | Payment attempts, failures, and retries can occur after the order date, and retries often occur on the *same* date, so `payment_timestamp` stores full time precision rather than a plain date. |
| `sessions` | Yes | A browsing session is an independent event and can happen before, after, or without an order. |
| `customers` | No date dimension FK | Customer creation is an entity lifecycle attribute, not an analytical event requiring the shared date dimension. |
| `products` | No date dimension FK | Product attributes describe the product rather than a transaction event. |
| `marketing_channels` | No date dimension FK | Channel definitions are descriptive reference data. |
| `date_dim` | N/A | This is the shared calendar dimension itself. |

## Why split `orders` and `order_items`?

An order can contain multiple products, so `orders` uses **order grain** (one row = one order), while `order_items` uses **order-line grain** (one row = one product within one order).

For example, if order `1001` contains three products:

```text
orders
+----------+-------------+-------------+
| order_id | customer_id | order_total |
+----------+-------------+-------------+
| 1001     | 42          | 1500        |
+----------+-------------+-------------+

order_items
+---------------+----------+------------+----------+
| order_item_id | order_id | product_id | quantity |
+---------------+----------+------------+----------+
| 1             | 1001     | P10        | 1        |
| 2             | 1001     | P20        | 2        |
| 3             | 1001     | P30        | 1        |
+---------------+----------+------------+----------+
```

If everything were stored in one flat `orders` table, the order-level values would have to be repeated for all three products, or the table would need awkward columns such as `product_1`, `product_2`, and `product_3`.

That creates a **grain problem**: the same order would appear three times, so summing an order-level measure such as `order_total` could count the same ₹1,500 order three times.

Keeping separate grains solves this:

```text
orders       → 1 row per order
order_items  → N rows per order, one per product
```

This lets us safely answer both:

- **Order-level questions:** How many orders? What is the average order value?
- **Line/product-level questions:** How many units of each product were sold? Which products generate the most revenue?

The key rule is:

> **Always define the grain before deciding what columns belong in a table or how tables should be joined.**

## RCA-critical dimensions

The schema deliberately places the fields needed for the Phase 0 RCA example:

```text
Mobile AOV ↓ 21%
        ↓
India mobile users affected most
        ↓
UPI transactions show abnormal failure behavior
```

The supporting columns are:

```text
orders
  ├── device
  ├── region
  ├── city
  └── attributed_channel_id

payments
  ├── payment_method
  ├── payment_status
  └── failure_reason

customers
  ├── region
  └── city        ← current customer location only

sessions
  ├── device
  ├── region
  ├── city
  └── marketing_channel_id
```

This means the RCA can segment purchase behavior by **device + purchase-time geography**, then investigate payment behavior by **payment method + status + failure reason**, while retaining session-level marketing context.

## Ingestion order

Because `sessions.converted_order_id` and `orders` reference each other (a session can convert into an order, and an order can be attributed back to a session), the tables can't all be generated independently in one pass without one side pointing at IDs that don't exist yet. The generation/ingestion script resolves this with a fixed order:

```text
1. sessions           — generated first, without converted_order_id populated
2. orders              — generated next; order_items generated alongside each
                         order so order_total can be computed by construction
                         (see "Keeping order_total consistent" above)
3. backfill            — sessions.converted_order_id is updated for any
                         session that led to an order created in step 2
```

This mirrors the real-world causal order (a session happens, then may convert into an order) and avoids ever writing a foreign key that points at a row which doesn't exist yet.

