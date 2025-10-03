# 🗄️ Database Schemas - E-commerce Platform

## Overview

Este documento detalha todos os schemas de banco de dados utilizados na plataforma.

---

## 📊 PostgreSQL Schemas

### 1. Auth Service Database

```sql
-- Database: ecommerce_auth

-- Users table (authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- Refresh tokens
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);

-- Login history (audit)
CREATE TABLE login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    email VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    location JSONB,
    failure_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_login_history_user ON login_history(user_id);
CREATE INDEX idx_login_history_created ON login_history(created_at);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_password_reset_token ON password_reset_tokens(token);
```

---

### 2. User Service Database

```sql
-- Database: ecommerce_users

-- User profiles (extended information)
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL, -- References auth.users.id
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user ON user_profiles(user_id);

-- Addresses
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    address_type VARCHAR(20) NOT NULL, -- 'shipping', 'billing'
    is_default BOOLEAN DEFAULT FALSE,
    recipient_name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(2) NOT NULL, -- ISO country code
    phone VARCHAR(20),
    coordinates POINT, -- Latitude, Longitude
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addresses_user ON addresses(user_id);
CREATE INDEX idx_addresses_default ON addresses(user_id, is_default) WHERE is_default = TRUE;

-- User preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    currency VARCHAR(3) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'UTC',
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    newsletter_subscribed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wishlists
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id VARCHAR(50) NOT NULL, -- MongoDB ObjectId
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_wishlists_unique ON wishlists(user_id, product_id);
CREATE INDEX idx_wishlists_user ON wishlists(user_id);
```

---

### 3. Order Service Database

```sql
-- Database: ecommerce_orders

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- Status: pending, confirmed, processing, shipped, delivered, cancelled, refunded

    -- Pricing
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    shipping_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,

    -- Payment
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    payment_id VARCHAR(255),

    -- Shipping
    shipping_address JSONB NOT NULL,
    billing_address JSONB,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    estimated_delivery DATE,

    -- Additional info
    notes TEXT,
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- Order Items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    product_snapshot JSONB, -- Full product details at time of purchase
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Order Status History
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    notes TEXT,
    changed_by INTEGER, -- User ID who made the change
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_status_history_order ON order_status_history(order_id);

-- Shopping Cart (persistent)
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    selected_options JSONB DEFAULT '{}',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_cart_items_unique ON cart_items(user_id, product_id);
CREATE INDEX idx_cart_items_user ON cart_items(user_id);

-- Coupons/Discounts
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL, -- 'percentage', 'fixed_amount'
    discount_value DECIMAL(10, 2) NOT NULL,
    min_purchase_amount DECIMAL(10, 2),
    max_discount_amount DECIMAL(10, 2),
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coupons_code ON coupons(code);

-- Coupon Usage
CREATE TABLE coupon_usage (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER NOT NULL REFERENCES coupons(id),
    order_id INTEGER NOT NULL REFERENCES orders(id),
    user_id INTEGER NOT NULL,
    discount_applied DECIMAL(10, 2) NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coupon_usage_coupon ON coupon_usage(coupon_id);
CREATE INDEX idx_coupon_usage_user ON coupon_usage(user_id);
```

---

### 4. Shipping Service Database

```sql
-- Database: ecommerce_shipping

-- Shipping Providers
CREATE TABLE shipping_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    api_endpoint TEXT,
    api_key_encrypted TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    supported_countries TEXT[], -- Array of country codes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipping Rates
CREATE TABLE shipping_rates (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES shipping_providers(id),
    service_name VARCHAR(100) NOT NULL,
    service_code VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL,
    min_weight_kg DECIMAL(10, 2),
    max_weight_kg DECIMAL(10, 2),
    base_cost DECIMAL(10, 2) NOT NULL,
    per_kg_cost DECIMAL(10, 2),
    estimated_days INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

-- Shipments
CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL,
    provider_id INTEGER REFERENCES shipping_providers(id),
    tracking_number VARCHAR(100) UNIQUE,
    service_code VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, picked_up, in_transit, out_for_delivery, delivered, failed

    -- Details
    weight_kg DECIMAL(10, 2),
    dimensions JSONB, -- {length, width, height}
    shipping_cost DECIMAL(10, 2),

    -- Addresses
    origin_address JSONB NOT NULL,
    destination_address JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    estimated_delivery TIMESTAMP
);

CREATE INDEX idx_shipments_order ON shipments(order_id);
CREATE INDEX idx_shipments_tracking ON shipments(tracking_number);

-- Tracking Events
CREATE TABLE tracking_events (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tracking_events_shipment ON tracking_events(shipment_id);
```

---

## 📦 MongoDB Schemas

### 1. Product Catalog (ecommerce_products)

```javascript
// Collection: products
{
    _id: ObjectId,
    sku: String,          // Unique product code
    name: String,
    slug: String,         // URL-friendly name
    description: String,
    short_description: String,

    // Categorization
    category: {
        id: String,
        name: String,
        path: String      // "Electronics > Computers > Laptops"
    },
    tags: [String],

    // Pricing
    pricing: {
        regular_price: Number,
        sale_price: Number,
        cost_price: Number,
        currency: String,
        tax_class: String
    },

    // Inventory
    inventory: {
        quantity: Number,
        track_inventory: Boolean,
        allow_backorder: Boolean,
        low_stock_threshold: Number,
        reserved_quantity: Number
    },

    // Media
    images: [{
        url: String,
        alt_text: String,
        is_primary: Boolean,
        order: Number
    }],
    videos: [{
        url: String,
        type: String,
        thumbnail: String
    }],

    // Specifications (flexible schema)
    specifications: {
        brand: String,
        model: String,
        color: String,
        size: String,
        weight: Number,
        dimensions: {
            length: Number,
            width: Number,
            height: Number,
            unit: String
        },
        // ... any other product-specific attributes
    },

    // Variants (for configurable products)
    variants: [{
        sku: String,
        attributes: {
            color: String,
            size: String
        },
        price: Number,
        quantity: Number,
        images: [String]
    }],

    // SEO
    seo: {
        meta_title: String,
        meta_description: String,
        meta_keywords: [String]
    },

    // Status
    is_active: Boolean,
    is_featured: Boolean,
    visibility: String,   // 'public', 'catalog', 'search', 'hidden'

    // Analytics
    views: Number,
    purchases: Number,
    rating: {
        average: Number,
        count: Number
    },

    // Timestamps
    created_at: ISODate,
    updated_at: ISODate,
    published_at: ISODate
}

// Indexes
db.products.createIndex({ "sku": 1 }, { unique: true });
db.products.createIndex({ "slug": 1 }, { unique: true });
db.products.createIndex({ "name": "text", "description": "text" });
db.products.createIndex({ "category.id": 1 });
db.products.createIndex({ "is_active": 1, "is_featured": 1 });
db.products.createIndex({ "pricing.regular_price": 1 });
db.products.createIndex({ "created_at": -1 });
```

```javascript
// Collection: categories
{
    _id: ObjectId,
    name: String,
    slug: String,
    description: String,
    parent_id: ObjectId,
    level: Number,
    path: String,         // Materialized path: "root/electronics/computers"
    image: String,
    icon: String,
    is_active: Boolean,
    display_order: Number,
    seo: {
        meta_title: String,
        meta_description: String
    },
    created_at: ISODate,
    updated_at: ISODate
}

db.categories.createIndex({ "slug": 1 }, { unique: true });
db.categories.createIndex({ "parent_id": 1 });
db.categories.createIndex({ "path": 1 });
```

```javascript
// Collection: reviews
{
    _id: ObjectId,
    product_id: String,
    user_id: Number,
    order_id: Number,     // Link to verified purchase
    rating: Number,       // 1-5
    title: String,
    comment: String,
    verified_purchase: Boolean,
    helpful_count: Number,
    reported_count: Number,
    status: String,       // 'pending', 'approved', 'rejected'
    moderator_notes: String,
    images: [String],
    created_at: ISODate,
    updated_at: ISODate
}

db.reviews.createIndex({ "product_id": 1, "status": 1 });
db.reviews.createIndex({ "user_id": 1 });
```

---

### 2. Payment Service (ecommerce_payments)

```javascript
// Collection: payments
{
    _id: ObjectId,
    payment_id: String,   // External payment gateway ID
    order_id: Number,
    user_id: Number,

    // Payment details
    amount: Number,
    currency: String,
    status: String,       // 'pending', 'processing', 'succeeded', 'failed', 'refunded'

    // Gateway
    gateway: String,      // 'stripe', 'paypal', 'blockchain'
    gateway_response: Object,

    // Method
    payment_method: {
        type: String,     // 'credit_card', 'debit_card', 'pix', 'boleto', 'crypto'
        details: {
            brand: String,
            last4: String,
            exp_month: Number,
            exp_year: Number
        }
    },

    // Billing
    billing_address: {
        name: String,
        street: String,
        city: String,
        state: String,
        postal_code: String,
        country: String
    },

    // Fraud detection
    risk_score: Number,
    risk_level: String,   // 'low', 'medium', 'high'
    fraud_checks: {
        ip_check: Boolean,
        cvv_check: Boolean,
        address_check: Boolean,
        velocity_check: Boolean
    },

    // Refund
    refund: {
        amount: Number,
        reason: String,
        refunded_at: ISODate
    },

    // Metadata
    metadata: Object,

    // Timestamps
    created_at: ISODate,
    updated_at: ISODate,
    succeeded_at: ISODate,
    failed_at: ISODate
}

db.payments.createIndex({ "payment_id": 1 }, { unique: true });
db.payments.createIndex({ "order_id": 1 });
db.payments.createIndex({ "user_id": 1 });
db.payments.createIndex({ "status": 1 });
db.payments.createIndex({ "created_at": -1 });
```

```javascript
// Collection: payment_logs (audit trail)
{
    _id: ObjectId,
    payment_id: String,
    event_type: String,
    request: Object,
    response: Object,
    error: Object,
    created_at: ISODate
}

db.payment_logs.createIndex({ "payment_id": 1, "created_at": -1 });
```

```javascript
// Collection: blockchain_transactions (optional)
{
    _id: ObjectId,
    payment_id: String,
    order_id: Number,
    blockchain: String,    // 'ethereum', 'bitcoin', 'polygon'
    transaction_hash: String,
    from_address: String,
    to_address: String,
    amount: Number,
    token: String,
    gas_fee: Number,
    confirmations: Number,
    status: String,
    block_number: Number,
    created_at: ISODate,
    confirmed_at: ISODate
}

db.blockchain_transactions.createIndex({ "transaction_hash": 1 }, { unique: true });
db.blockchain_transactions.createIndex({ "payment_id": 1 });
```

---

### 3. Analytics Service (ecommerce_analytics)

```javascript
// Collection: events
{
    _id: ObjectId,
    event_type: String,   // 'page_view', 'product_view', 'add_to_cart', 'purchase', etc.
    user_id: Number,
    session_id: String,

    // Event data
    data: {
        product_id: String,
        category: String,
        price: Number,
        quantity: Number,
        // ... flexible schema based on event type
    },

    // Context
    context: {
        ip_address: String,
        user_agent: String,
        referrer: String,
        utm_source: String,
        utm_medium: String,
        utm_campaign: String,
        device: {
            type: String,
            os: String,
            browser: String
        },
        location: {
            country: String,
            city: String,
            coordinates: [Number, Number]
        }
    },

    created_at: ISODate
}

// Time-series optimized indexes
db.events.createIndex({ "created_at": -1 });
db.events.createIndex({ "event_type": 1, "created_at": -1 });
db.events.createIndex({ "user_id": 1, "created_at": -1 });
db.events.createIndex({ "session_id": 1 });
```

---

## 🔴 Redis Data Structures

### Key Patterns

```
# Sessions
session:{session_id} → HASH
  - user_id
  - created_at
  - last_active
  - device_info

# Cart (temporary, 7 days TTL)
cart:{user_id} → HASH
  - {product_id}: quantity

# Rate Limiting
rate_limit:{ip}:{endpoint} → STRING (counter)
  TTL: 60 seconds

# Product Cache
product:{product_id} → STRING (JSON)
  TTL: 300 seconds

# Product List Cache
products:list:{page}:{filters_hash} → STRING (JSON)
  TTL: 60 seconds

# User token blacklist
token:blacklist:{token_jti} → STRING
  TTL: token expiration time

# Real-time inventory
inventory:{product_id} → STRING (quantity)
  No TTL, updated via events

# Trending products (sorted set)
trending:products → ZSET
  Score: view_count + purchase_count

# Search suggestions (autocomplete)
search:suggestions → ZSET
  Score: search frequency
```

---

## 🔐 Database Security

### Encryption

```sql
-- Sensitive data encryption (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypting credit card info
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    card_number_encrypted BYTEA,
    -- Encrypt before insert
    -- pgp_sym_encrypt('4111111111111111', 'encryption_key')
);
```

### Row-Level Security (RLS)

```sql
-- PostgreSQL RLS example
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_orders_policy ON orders
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::INTEGER);
```

### Backup Strategy

```
Daily:
  - Full PostgreSQL dump
  - MongoDB incremental backup
  - Redis snapshot

Weekly:
  - Full system backup
  - Off-site replication

Monthly:
  - Long-term archive
  - Compliance snapshot
```

---

## 📊 Database Performance Tuning

### PostgreSQL Configuration

```ini
# postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB
max_connections = 200
```

### Query Optimization

```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123
  AND status = 'delivered'
  AND created_at >= NOW() - INTERVAL '30 days';

-- Create appropriate indexes
CREATE INDEX idx_orders_user_status_created
ON orders(user_id, status, created_at DESC);
```

### MongoDB Optimization

```javascript
// Use aggregation pipeline for complex queries
db.products.aggregate([
    { $match: { is_active: true, "pricing.sale_price": { $lte: 100 } } },
    { $lookup: {
        from: "reviews",
        localField: "_id",
        foreignField: "product_id",
        as: "reviews"
    }},
    { $addFields: {
        avg_rating: { $avg: "$reviews.rating" }
    }},
    { $sort: { avg_rating: -1 } },
    { $limit: 20 }
]);

// Compound indexes for common queries
db.products.createIndex({
    "is_active": 1,
    "category.id": 1,
    "pricing.regular_price": 1
});
```

---

**Schema Version: 1.0**
**Last Updated: 2025-01-01**
