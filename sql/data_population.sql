-- 1. 插入系統管理員
INSERT INTO admin (account, name, password) 
VALUES ('admin_001', '系統管理員', '$2b$12$8sjxkp0Fzp0rapvyTt7jNu.f8wyOQf45ttTOxesZg.HthNKOJIBmO');

-- 2. 插入書籍資料
INSERT INTO book (book_id, title, author, publisher, isbn, category, series, publish_date) VALUES 
('ed85817c-a15d-5afa-a661-5b9c93354f9d', 'Python 資料庫應用', '李大偉', '技術出版社', '978-986-7798-00-1', '程式設計', NULL, '2023-10-15'),
('a4239eb6-4fcd-513b-9fb4-75edb78e4f23', '精通SQLAlchemy', '林小美', '程式設計出版社', '978-986-7798-00-2', '程式設計', NULL, '2024-01-20');

-- 3. 插入實體書店
INSERT INTO bookstore (bookstore_id, name, phone_number, email, address, shipping_fee) VALUES 
('0cb29776-6efd-5c14-a791-36213574a4ee', 'Bookworm 書店', '0212345678', 'bookworm@store.com', '新北市板橋區文化路二段1號', 60),('034efc4b-d098-5463-9158-bc4af1cd2204', 'Second Page 書店', '0423456789', 'second@store.com', '高雄市前鎮區三多三路213號', 50);

-- 4. 插入顧客資料
INSERT INTO customer (account, name, password, email, phone_number, address) VALUES 
('customer_A', '王小明', '$2b$12$8sjxkp0Fzp0rapvyTt7jNu.f8wyOQf45ttTOxesZg.HthNKOJIBmO', 'ming@example.com', '0912345678', '台北市信義區忠孝東路一段1號'),
('customer_B', '李小華', '$2b$12$8sjxkp0Fzp0rapvyTt7jNu.f8wyOQf45ttTOxesZg.HthNKOJIBmO', 'hua@example.com', '0998765432', '台中市西屯區台灣大道三段99號');

-- 5. 建立購物車
INSERT INTO shopping_cart (cart_id, customer_account) VALUES 
('27345c8e-f941-54e9-8c99-7f9c3df74f3a', 'customer_A'),
('5abdbd77-186f-5976-9e29-dc719d8fd21d', 'customer_B');

-- 6. 設定書籍與書店的映射關係 (庫存/價格)
INSERT INTO book_bookstore_mapping (book_bookstore_mapping_id, price, store_quantity, book_id, bookstore_id) VALUES 
('f189281d-4b6c-5b7d-9ce2-08d9a0817efe', 550, 100, 'ed85817c-a15d-5afa-a661-5b9c93354f9d', '0cb29776-6efd-5c14-a791-36213574a4ee'),
('15c70f39-26c7-569f-8834-050f62baf832', 480, 50, 'a4239eb6-4fcd-513b-9fb4-75edb78e4f23', '0cb29776-6efd-5c14-a791-36213574a4ee');

-- 7. 插入員工資料
INSERT INTO staff (account, name, password, bookstore_id) 
VALUES ('staff_B', '陳店員', '$2b$12$8sjxkp0Fzp0rapvyTt7jNu.f8wyOQf45ttTOxesZg.HthNKOJIBmO', '0cb29776-6efd-5c14-a791-36213574a4ee');

-- 8. 插入優惠券
INSERT INTO coupon (coupon_id, name, type, discount_percentage, start_date, end_date, admin_account, staff_account) 
VALUES ('fdd70d58-b781-5f04-bad1-5ad62be858a6', '新客折扣', 'special_event', 0.10, '2025-12-25', '2026-01-24', 'admin_001', NULL);

-- 9. 建立訂單
INSERT INTO order_ (order_id, order_time, customer_name, customer_phone_number, customer_email, status, total_price, shipping_address, shipping_fee, recipient_name, coupon_id, customer_account) 
VALUES ('c7cda87b-a10c-53f6-92d0-3ee937e438f7', '2025-12-25', '王小明', '0912345678', 'ming@example.com', 'received', 1419, '台北市信義區忠孝東路一段1號', 60, '王小明', 'fdd70d58-b781-5f04-bad1-5ad62be858a6', 'customer_A');

-- 10. 建立訂單明細
INSERT INTO order_item (order_item_id, quantity, price, order_id, book_bookstore_mapping_id) 
VALUES (gen_random_uuid(), 1, 550, 'c7cda87b-a10c-53f6-92d0-3ee937e438f7', 'f189281d-4b6c-5b7d-9ce2-08d9a0817efe');
