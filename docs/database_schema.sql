-- ============================================
-- G2G Technical Assessment Database Schema
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS g2g_system;
USE g2g_system;

-- Customers table
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status ENUM('Active', 'Delivered') NOT NULL DEFAULT 'Active',
    delivered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_number (order_number),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Reward points table
CREATE TABLE reward_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_id INT NULL,
    points DECIMAL(10, 2) NOT NULL,
    transaction_type ENUM('Credit', 'Debit') NOT NULL,
    expiry_date DATE NOT NULL,
    is_expired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    INDEX idx_customer_id (customer_id),
    INDEX idx_expiry_date (expiry_date),
    INDEX idx_is_expired (is_expired)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Customer points balance view
CREATE VIEW customer_points_balance AS
SELECT
    c.id as customer_id,
    c.name,
    c.email,
    COALESCE(SUM(CASE
        WHEN rp.transaction_type = 'Credit' AND rp.is_expired = FALSE AND rp.expiry_date >= CURDATE()
        THEN rp.points
        ELSE 0
    END), 0) as total_credits,
    COALESCE(SUM(CASE
        WHEN rp.transaction_type = 'Debit'
        THEN rp.points
        ELSE 0
    END), 0) as total_debits,
    COALESCE(SUM(CASE
        WHEN rp.transaction_type = 'Credit' AND rp.is_expired = FALSE AND rp.expiry_date >= CURDATE()
        THEN rp.points
        WHEN rp.transaction_type = 'Debit'
        THEN -rp.points
        ELSE 0
    END), 0) as available_balance
FROM customers c
LEFT JOIN reward_points rp ON c.id = rp.customer_id
GROUP BY c.id, c.name, c.email;

-- Currency exchange rates table
CREATE TABLE exchange_rates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    rate DECIMAL(10, 6) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_currency_pair (from_currency, to_currency),
    INDEX idx_from_currency (from_currency)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default exchange rates
INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES
('USD', 'USD', 1.000000),
('MYR', 'USD', 0.230000),
('EUR', 'USD', 1.100000),
('GBP', 'USD', 1.270000),
('JPY', 'USD', 0.009000),
('CNY', 'USD', 0.140000),
('SGD', 'USD', 0.740000);
