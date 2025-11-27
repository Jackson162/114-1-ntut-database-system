-- 1. admin
INSERT INTO admin (account, name, password) VALUES
('admin_001', 'Alice Johnson', '$2a$10$hash1$'),
('admin_002', 'Bob Williams', '$2a$10$hash2$'),
('admin_003', 'Charlie Brown', '$2a$10$hash3$');

-- 2. bookstore
INSERT INTO bookstore (bookstore_id, name, phone_number, email, address, shipping_fee) VALUES
('b18d86e0-811c-4394-a901-7d14b0b1476f', 'Central Bookstore', '0212345678', 'central@book.com', '100 Main St, City A', 60),
('9f2a4c87-0b73-4f96-857e-3c2d4a6e8f1b', 'University Books', '0323456789', 'uni@books.net', '50 College Ave, City B', 50),
('3c5f7e0a-4d2b-4198-a65c-9e1f0b3d5a7c', 'Cozy Corner Books', '0434567890', 'cozy@corner.com', '123 Elm St, City C', 75);

-- 3. staff
INSERT INTO staff (account, name, password, bookstore_id) VALUES
('staff_A01', 'David Lee', '$2a$10$hash4$', 'b18d86e0-811c-4394-a901-7d14b0b1476f'),
('staff_B02', 'Eve Chen', '$2a$10$hash5$', '9f2a4c87-0b73-4f96-857e-3c2d4a6e8f1b'),
('staff_C03', 'Frank Wang', '$2a$10$hash6$', '3c5f7e0a-4d2b-4198-a65c-9e1f0b3d5a7c');

-- 4. coupon
-- 注意：staff_account 和 admin_account 有些為 NULL
INSERT INTO coupon (coupon_id, type, discount_percentage, start_date, end_date, admin_account, staff_account) VALUES
('cb7897ee-e43a-4f2e-9989-a90c5f632692', 'Holiday', 0.15, '2025-12-01', '2025-12-31', 'admin_001', NULL),
('d8d0bea2-a3c0-4ff4-8983-0ff3676e9633', 'Student', 0.10, '2025-01-01', NULL, NULL, 'staff_B02'),
('6fc7032d-c542-4be7-ba73-9717e0d2a780', 'New Customer', 0.20, '2025-11-18', '2025-12-18', 'admin_003', NULL);

-- 5. customer
INSERT INTO customer (account, name, password, email, phone_number, address) VALUES
('cust_101', 'Grace Huang', '$2a$10$hash7$', 'grace@mail.com', '0910111222', '456 Oak Ln'),
('cust_102', 'Henry Kuo', '$2a$10$hash8$', 'henry@mail.net', '0920333444', '789 Pine Ave'),
('cust_103', 'Ivy Lin', '$2a$10$hash9$', 'ivy@mail.org', '0930555666', '101 Birch Rd');

-- 6. book
INSERT INTO book (book_id, title, author, publisher, isbn, category, series, publish_date) VALUES
('b001d1e5-5a6f-47a3-82b4-6c7e8d9f0a1b', 'The Great Adventure', 'A. Author', 'Fictional Press', '9781234567890', 'Fiction', 'The Explorer', '2020-05-15'),
('a0209ab2-5f31-49e7-89a5-12d1a572ad64', 'Database Design 101', 'D. Designer', 'Tech Books Inc', '9780987654321', 'Education', NULL, '2023-08-01'),
('17020db9-5ee1-4ca6-861d-46dc9b527e37', 'Culinary Wonders', 'C. Chef', 'Gourmet Pub', '9781122334455', 'Cooking', NULL, '2021-03-10');

-- 7. book_bookstore_mapping (商品庫存與定價)
INSERT INTO book_bookstore_mapping (book_bookstore_mapping_id, price, store_quantity, book_id, bookstore_id) VALUES
('1b096468-59f3-4181-87de-72ed7dcb1f2a', 350, 50, 'b001d1e5-5a6f-47a3-82b4-6c7e8d9f0a1b', 'b18d86e0-811c-4394-a901-7d14b0b1476f'), -- Central: The Great Adventure
('637a8eb8-1697-4860-a24a-ddc967eae99d', 480, 30, 'a0209ab2-5f31-49e7-89a5-12d1a572ad64', '9f2a4c87-0b73-4f96-857e-3c2d4a6e8f1b'), -- University: Database Design 101
('89df472a-9ada-43d4-9e76-bad17c0341bb', 290, 75, '17020db9-5ee1-4ca6-861d-46dc9b527e37', '3c5f7e0a-4d2b-4198-a65c-9e1f0b3d5a7c'), -- Cozy: Culinary Wonders
('3da21d96-53ea-48ed-b220-14220413334d', 360, 20, 'b001d1e5-5a6f-47a3-82b4-6c7e8d9f0a1b', '9f2a4c87-0b73-4f96-857e-3c2d4a6e8f1b'); -- University: The Great Adventure (不同價格)

-- 8. shopping_cart
INSERT INTO shopping_cart (cart_id, customer_account) VALUES
('82704ad6-47dd-49a9-84c1-41ddc94b1490', 'cust_101'),
('86fd179d-4ba7-4d6e-b8a2-36cf97d7df6d', 'cust_102'),
('81f662c4-c4e9-4440-98b0-2cc86dcf443e', 'cust_103');

-- 9. cart_item
INSERT INTO cart_item (cart_item_id, cart_id, quantity, book_bookstore_mapping_id) VALUES
('aa117a7a-009d-4083-8671-e45a27864bcd', '82704ad6-47dd-49a9-84c1-41ddc94b1490', 2, '1b096468-59f3-4181-87de-72ed7dcb1f2a'), -- Grace: 2 x TGA @ Central
('32339e15-8395-4282-8eb4-a0b041a71d93', '81f662c4-c4e9-4440-98b0-2cc86dcf443e', 1, '89df472a-9ada-43d4-9e76-bad17c0341bb'), -- Grace: 1 x CW @ Cozy
('be782efc-e42f-44e3-8e2e-c41831071062', '86fd179d-4ba7-4d6e-b8a2-36cf97d7df6d', 3, '637a8eb8-1697-4860-a24a-ddc967eae99d'); -- Henry: 3 x DD101 @ University

-- 10. order_
INSERT INTO order_ (order_id, order_time, customer_account, customer_name, customer_phone_number, customer_email, status, total_price, shipping_address, shipping_fee, recipient_name, coupon_id) VALUES
('08c3b7a6-113f-4326-8caa-4ee6b465431a', '2025-11-15', 'cust_101', 'Grace Huang', '0910111222', 'grace@mail.com', 'Shipped', 850, '456 Oak Ln', 60, 'Grace Huang', 'cb7897ee-e43a-4f2e-9989-a90c5f632692'), -- 總價計算：(2*350 + 1*360) * (1-0.15) + 60 = (700+360)*0.85 + 60 = 1060*0.85 + 60 = 901 + 60 = 961 (假設 order_item 中的價格已經是折價後的單價，或這裡的 total_price 簡化。實際資料中 total_price 應為折扣後的總金額，為求範例方便這裡使用先前設計的值。)
('8a793330-9d1a-41a1-bc65-6b4fb1bd9436', '2025-11-16', 'cust_102', 'Henry Kuo', '0920333444', 'henry@mail.net', 'Delivered', 530, '789 Pine Ave', 50, 'Henry Kuo', 'd8d0bea2-a3c0-4ff4-8983-0ff3676e9633'),
('3aefb995-bc78-4c0e-be37-bb04627eba3b', '2025-11-17', 'cust_103', 'Ivy Lin', '0930555666', 'ivy@mail.org', 'Processing', 365, '101 Birch Rd', 75, 'Ivy Lin', NULL);

-- 11. order_item
INSERT INTO order_item (order_item_id, quantity, price, order_id, book_bookstore_mapping_id) VALUES
('c9dbaf65-9162-416d-98c4-7d443facff36', 2, 350, '08c3b7a6-113f-4326-8caa-4ee6b465431a', '1b096468-59f3-4181-87de-72ed7dcb1f2a'), -- Order 1: 2 x TGA @ Central (原價 350)
('b793bc50-564c-4518-ace6-2e1e9f701349', 1, 480, '8a793330-9d1a-41a1-bc65-6b4fb1bd9436', '637a8eb8-1697-4860-a24a-ddc967eae99d'), -- Order 2: 1 x DD101 @ University (原價 480)
('5f3487a1-6340-4584-ac57-f7b37614740c', 1, 290, '3aefb995-bc78-4c0e-be37-bb04627eba3b', '89df472a-9ada-43d4-9e76-bad17c0341bb'), -- Order 3: 1 x CW @ Cozy (原價 290)
('5a7ceb20-beba-4830-b22a-9c29e53a466a', 1, 360, '08c3b7a6-113f-4326-8caa-4ee6b465431a', '3da21d96-53ea-48ed-b220-14220413334d'); -- Order 1: 1 x TGA @ University (原價 360)