CREATE DATABASE IF NOT EXISTS dbs;
USE dbs;

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE restaurants (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone_number VARCHAR(15),
    email VARCHAR(255),
    rating DECIMAL(2,1) DEFAULT 0.0,
    total_ratings INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
);

CREATE TABLE restaurant_locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    address VARCHAR(255) NOT NULL,
    opening_hours VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE menu_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    item_count INT DEFAULT 0,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    category_id INT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (category_id) REFERENCES menu_categories(category_id)
);

CREATE TABLE cart_items (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2),
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    order_type ENUM('dine_in', 'takeaway', 'delivery'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    user_id INT NOT NULL,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE deleted_orders (
    deleted_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_date DATETIME,
    deletion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    items_json TEXT,
    deletion_type TEXT DEFAULT 'manual'
);

USE dbs;
-- Adding new users
INSERT INTO users (username, password, email, phone_number) VALUES
('customer1', 'hashed_password_here', 'customer1@example.com', '1234567890'),
('customer2', 'hashed_password_here', 'customer2@example.com', '2345678901'),
('customer3', 'hashed_password_here', 'customer3@example.com', '3456789012');

-- Adding new restaurants
INSERT INTO restaurants (admin_id, name, address, phone_number, email) VALUES
(7, 'Thai Delight', '123 Spice Avenue, Bangkok', '9876543210', 'thai@example.com'),
(1, 'Italian Corner', '456 Pasta Street, Rome', '8765432109', 'italian@example.com');

-- Adding new menu categories
INSERT INTO menu_categories (restaurant_id, name, item_count) VALUES
(7, 'Thai Curries', 0),
(7, 'Thai Noodles', 0),
(7, 'Thai Desserts', 0);

-- Adding new menu items
INSERT INTO menu_items (restaurant_id, category_id, name, description, price) VALUES
(7, 19, 'Green Curry', 'Spicy Thai green curry with coconut milk', 220),
(7, 19, 'Pad Thai', 'Traditional Thai stir-fried noodles', 180),
(7, 20, 'Tom Yum Noodle Soup', 'Spicy and sour noodle soup', 190),
(7, 21, 'Mango Sticky Rice', 'Sweet sticky rice with fresh mango', 120);

-- Update item count in categories
UPDATE menu_categories SET item_count = 2 WHERE category_id = 19;
UPDATE menu_categories SET item_count = 1 WHERE category_id = 20;
UPDATE menu_categories SET item_count = 1 WHERE category_id = 21;

-- Adding new orders
INSERT INTO orders (user_id, restaurant_id, total_amount, shipping_cost, order_type, status) VALUES
(1, 7, 400, 50, 'delivery', 'processing'),
(2, 7, 310, 30, 'takeaway', 'pending'),
(3, 5, 460, 0, 'dine_in', 'delivered');

-- Adding order items for the new orders
INSERT INTO order_items (order_id, item_id, quantity, price) VALUES
(4, 25, 1, 220),
(4, 26, 1, 180),
(5, 27, 1, 190),
(5, 28, 1, 120),
(6, 17, 2, 180),
(6, 20, 1, 70);

-- Adding payments for the new orders
INSERT INTO payments (order_id, payment_method, transaction_id, amount, status) VALUES
(4, 'credit_card', 'TXN123456789', 450, 'completed'),
(5, 'cash', 'TXN987654321', 340, 'pending'),
(6, 'upi', 'TXN567891234', 460, 'completed');

-- Adding ratings
INSERT INTO ratings (restaurant_id, user_id, rating_value, review) VALUES
(7, 1, 5, 'Excellent Thai food, very authentic!'),
(7, 2, 4, 'Good food but delivery was a bit late'),
(5, 3, 5, 'Best vegetarian options in town');

select * from users;


DELIMITER $$

CREATE PROCEDURE reconcile_order_payments()
BEGIN
    DECLARE v_count INT;
    DECLARE v_missing_count INT DEFAULT 0;
    DECLARE v_order_id INT;
    DECLARE v_total_amount DECIMAL(10,2);
    DECLARE done INT DEFAULT FALSE;
    
    -- Cursor for orders without payments
    DECLARE c_missing_payments CURSOR FOR
        SELECT o.order_id, o.total_amount
        FROM orders o
        LEFT JOIN payments p ON o.order_id = p.order_id
        WHERE p.payment_id IS NULL;
    
    -- Declare handler for cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Log start of reconciliation
    SELECT CONCAT('Starting payment reconciliation process at ', NOW()) AS log_message;
    
    -- Check for orders without payments
    SELECT COUNT(*) INTO v_count
    FROM orders o
    LEFT JOIN payments p ON o.order_id = p.order_id
    WHERE p.payment_id IS NULL;
    
    SELECT CONCAT('Found ', v_count, ' orders without payment records') AS log_message;
    
    -- Create payment records for orders without payments
    OPEN c_missing_payments;
    
    read_loop: LOOP
        FETCH c_missing_payments INTO v_order_id, v_total_amount;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Insert a pending payment record
        INSERT INTO payments (
            order_id, 
            payment_method, 
            transaction_id, 
            amount, 
            status, 
            created_at
        ) VALUES (
            v_order_id, 
            'RECONCILIATION', 
            CONCAT('AUTO-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), '-', v_order_id), 
            v_total_amount, 
            'pending', 
            NOW()
        );
        
        SET v_missing_count = v_missing_count + 1;
        SELECT CONCAT('Created payment record for order ID: ', v_order_id) AS log_message;
    END LOOP;
    
    CLOSE c_missing_payments;
    
    -- Check for payments with incorrect amounts
    UPDATE payments p
    JOIN orders o ON p.order_id = o.order_id
    SET p.amount = o.total_amount
    WHERE p.amount != o.total_amount;
    
    SELECT CONCAT('Updated ', ROW_COUNT(), ' payment records with incorrect amounts') AS log_message;
    
    -- Final summary
    SELECT CONCAT('Payment reconciliation completed. Created ', v_missing_count, ' new payment records') AS log_message;
END$$

CREATE FUNCTION verify_data_integrity() RETURNS INT
BEGIN
    DECLARE v_error_count INT DEFAULT 0;
    DECLARE v_orphaned_orders INT;
    DECLARE v_orphaned_order_items INT;
    DECLARE v_orphaned_payments INT;
    DECLARE v_orphaned_cart_items INT;
    DECLARE v_orphaned_menu_items INT;
    DECLARE v_orphaned_menu_categories INT;
    DECLARE v_inconsistent_payments INT;
    
    -- Check for orphaned orders (orders with non-existent users or restaurants)
    SELECT COUNT(*) INTO v_orphaned_orders
    FROM orders o
    LEFT JOIN users u ON o.user_id = u.user_id
    LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE u.user_id IS NULL OR r.restaurant_id IS NULL;
    
    IF v_orphaned_orders > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_orders, ' orphaned orders') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_orders;
    END IF;
    
    -- Check for orphaned order items (items with non-existent orders or menu items)
    SELECT COUNT(*) INTO v_orphaned_order_items
    FROM order_items oi
    LEFT JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
    WHERE o.order_id IS NULL OR mi.item_id IS NULL;
    
    IF v_orphaned_order_items > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_order_items, ' orphaned order items') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_order_items;
    END IF;
    
    -- Check for orphaned payments (payments with non-existent orders)
    SELECT COUNT(*) INTO v_orphaned_payments
    FROM payments p
    LEFT JOIN orders o ON p.order_id = o.order_id
    WHERE o.order_id IS NULL;
    
    IF v_orphaned_payments > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_payments, ' orphaned payments') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_payments;
    END IF;
    
    -- Check for orphaned cart items
    SELECT COUNT(*) INTO v_orphaned_cart_items
    FROM cart_items ci
    LEFT JOIN users u ON ci.user_id = u.user_id
    LEFT JOIN menu_items mi ON ci.item_id = mi.item_id
    LEFT JOIN restaurants r ON ci.restaurant_id = r.restaurant_id
    WHERE u.user_id IS NULL OR mi.item_id IS NULL OR r.restaurant_id IS NULL;
    
    IF v_orphaned_cart_items > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_cart_items, ' orphaned cart items') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_cart_items;
    END IF;
    
    -- Check for orphaned menu items
    SELECT COUNT(*) INTO v_orphaned_menu_items
    FROM menu_items mi
    LEFT JOIN restaurants r ON mi.restaurant_id = r.restaurant_id
    LEFT JOIN menu_categories mc ON mi.category_id = mc.category_id
    WHERE r.restaurant_id IS NULL OR (mi.category_id IS NOT NULL AND mc.category_id IS NULL);
    
    IF v_orphaned_menu_items > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_menu_items, ' orphaned menu items') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_menu_items;
    END IF;
    
    -- Check for orphaned menu categories
    SELECT COUNT(*) INTO v_orphaned_menu_categories
    FROM menu_categories mc
    LEFT JOIN restaurants r ON mc.restaurant_id = r.restaurant_id
    WHERE r.restaurant_id IS NULL;
    
    IF v_orphaned_menu_categories > 0 THEN
        SELECT CONCAT('Found ', v_orphaned_menu_categories, ' orphaned menu categories') AS log_message;
        SET v_error_count = v_error_count + v_orphaned_menu_categories;
    END IF;
    
    -- Check for inconsistent payment amounts
    SELECT COUNT(*) INTO v_inconsistent_payments
    FROM payments p
    JOIN orders o ON p.order_id = o.order_id
    WHERE p.amount != o.total_amount;
    
    IF v_inconsistent_payments > 0 THEN
        SELECT CONCAT('Found ', v_inconsistent_payments, ' payments with inconsistent amounts') AS log_message;
        SET v_error_count = v_error_count + v_inconsistent_payments;
    END IF;
    
    -- Return total number of integrity issues found
    IF v_error_count = 0 THEN
        SELECT 'Data integrity verification completed. No issues found.' AS log_message;
    ELSE
        SELECT CONCAT('Data integrity verification completed. Found ', v_error_count, ' total issues.') AS log_message;
    END IF;
    
    RETURN v_error_count;
END$$

DELIMITER ;
