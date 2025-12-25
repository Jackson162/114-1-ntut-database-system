drop table if exists coupon ,order_ ,order_item ,customer,shopping_cart,cart_item,admin,staff,bookstore,book,book_bookstore_mapping;

CREATE TABLE admin (
    account TEXT NOT NULL, 
    name TEXT NOT NULL, 
    password TEXT NOT NULL, 
    PRIMARY KEY (account)
);

CREATE TABLE book (
    book_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    title TEXT NOT NULL, 
    author TEXT NOT NULL, 
    publisher TEXT NOT NULL, 
    isbn VARCHAR(17) NOT NULL, 
    category TEXT, 
    series TEXT, 
    publish_date DATE, 
    PRIMARY KEY (book_id), 
    UNIQUE (isbn), 
    CONSTRAINT uc_isbn UNIQUE (isbn)
);

CREATE TABLE bookstore (
    bookstore_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    name TEXT NOT NULL, 
    phone_number CHAR(10) NOT NULL, 
    email TEXT, 
    address TEXT, 
    shipping_fee INTEGER NOT NULL, 
    PRIMARY KEY (bookstore_id), 
    CONSTRAINT shipping_fee_non_negative CHECK (shipping_fee >= 0)
);

CREATE TABLE customer (
    account TEXT NOT NULL, 
    name TEXT NOT NULL, 
    password TEXT NOT NULL, 
    email TEXT, 
    phone_number CHAR(10) NOT NULL, 
    address TEXT, 
    PRIMARY KEY (account)
);

CREATE TABLE book_bookstore_mapping (
    book_bookstore_mapping_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    price INTEGER NOT NULL, 
    store_quantity INTEGER NOT NULL, 
    book_id UUID NOT NULL, 
    bookstore_id UUID NOT NULL, 
    PRIMARY KEY (book_bookstore_mapping_id), 
    CONSTRAINT price_non_negative CHECK (price >= 0), 
    CONSTRAINT store_quantity_non_negative CHECK (store_quantity >= 0), 
    FOREIGN KEY(book_id) REFERENCES book (book_id), 
    FOREIGN KEY(bookstore_id) REFERENCES bookstore (bookstore_id)
);

CREATE TABLE shopping_cart (
    cart_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    customer_account TEXT NOT NULL, 
    PRIMARY KEY (cart_id), 
    FOREIGN KEY(customer_account) REFERENCES customer (account)
);

CREATE TABLE staff (
    account TEXT NOT NULL, 
    name TEXT NOT NULL, 
    password TEXT NOT NULL, 
    bookstore_id UUID, 
    PRIMARY KEY (account), 
    FOREIGN KEY(bookstore_id) REFERENCES bookstore (bookstore_id)
);

CREATE TABLE cart_item (
    cart_item_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    quantity INTEGER NOT NULL, 
    cart_id UUID NOT NULL, 
    book_bookstore_mapping_id UUID NOT NULL, 
    PRIMARY KEY (cart_item_id), 
    CONSTRAINT quantity_non_negative CHECK (quantity >= 0), 
    FOREIGN KEY(book_bookstore_mapping_id) REFERENCES book_bookstore_mapping (book_bookstore_mapping_id), 
    FOREIGN KEY(cart_id) REFERENCES shopping_cart (cart_id)
);

CREATE TABLE coupon (
    coupon_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    name TEXT, 
    type TEXT NOT NULL, 
    discount_percentage NUMERIC NOT NULL, 
    start_date DATE NOT NULL, 
    end_date DATE, 
    admin_account TEXT, 
    staff_account TEXT, 
    PRIMARY KEY (coupon_id), 
    CONSTRAINT discount_percentage_check CHECK (discount_percentage >= 0 AND discount_percentage <= 1), 
    FOREIGN KEY(admin_account) REFERENCES admin (account), 
    FOREIGN KEY(staff_account) REFERENCES staff (account)
);

CREATE TABLE order_ (
    order_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    order_time DATE NOT NULL, 
    customer_name TEXT NOT NULL, 
    customer_phone_number CHAR(10) NOT NULL, 
    customer_email TEXT, 
    status TEXT NOT NULL, 
    total_price INTEGER NOT NULL, 
    shipping_address TEXT NOT NULL, 
    shipping_fee INTEGER NOT NULL, 
    recipient_name TEXT NOT NULL, 
    coupon_id UUID, 
    customer_account TEXT NOT NULL, 
    PRIMARY KEY (order_id), 
    CONSTRAINT shipping_fee_non_negative CHECK (shipping_fee >= 0), 
    CONSTRAINT total_price_non_negative CHECK (total_price >= 0), 
    FOREIGN KEY(coupon_id) REFERENCES coupon (coupon_id), 
    FOREIGN KEY(customer_account) REFERENCES customer (account)
);

CREATE TABLE order_item (
    order_item_id UUID DEFAULT gen_random_uuid() NOT NULL, 
    quantity INTEGER NOT NULL, 
    price INTEGER NOT NULL, 
    order_id UUID NOT NULL, 
    book_bookstore_mapping_id UUID NOT NULL, 
    PRIMARY KEY (order_item_id), 
    CONSTRAINT price_non_negative CHECK (price >= 0), 
    CONSTRAINT quantity_non_negative CHECK (quantity >= 0), 
    FOREIGN KEY(book_bookstore_mapping_id) REFERENCES book_bookstore_mapping (book_bookstore_mapping_id), 
    FOREIGN KEY(order_id) REFERENCES order_ (order_id)
);





