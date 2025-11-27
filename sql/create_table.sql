create table if not exists admin(
	account text primary key,
	name text not null,
	password text not null
);


create table if not exists bookstore(
	bookstore_id uuid primary key,
	name text not null,
	phone_number char(10) not null,
	email text,
	address text,
	shipping_fee int not null check (shipping_fee >= 0)
);

create table if not exists staff(
	account text primary key,
	name text not null,
	password text not null,
	bookstore_id uuid not null,
	constraint fk_bookstore_id
		foreign key (bookstore_id)
		references bookstore(bookstore_id)
);

create table if not exists coupon(
	coupon_id uuid primary key,
	type text not null,
	discount_percentage decimal check (discount_percentage >= 0 and discount_percentage <=1),
	start_date date not null,
	end_date date,
	admin_account text,
	staff_account text,
	constraint fk_admin_account
		foreign key (admin_account)
		references admin(account),
	constraint fk_staff_account
		foreign key (staff_account)
		references staff(account)
);

create table if not exists customer(
	account text primary key,
	name text not null,
	password text not null,
	email text,
	phone_number char(10) not null,
	address text
);

create table if not exists order_ (
    order_id uuid primary key,
    order_time date not null,
    customer_account text not null,
    customer_name text not null,
    customer_phone_number char(10) not null,
    customer_email text,
    status text not null,
    total_price int not null check (total_price >= 0),
    shipping_address text not null,
    shipping_fee int not null check (shipping_fee >= 0),
    recipient_name text not null,
    coupon_id uuid, 
    constraint fk_coupon_id
        foreign key (coupon_id) 
        references coupon(coupon_id),
    constraint fk_customer_account
      foreign key (customer_account)
      references customer(account)
);

create table if not exists shopping_cart(
	cart_id uuid primary key,
	customer_account text,
	constraint fk_customer_account
		foreign key (customer_account)
		references customer(account)
);

create table if not exists book(
	book_id uuid primary key,
	title text not null,
	author text not null,
	publisher text not null,
	isbn char(13) not null unique,
	category text,
	series text,
	publish_date date
);

create table if not exists book_bookstore_mapping(
	book_bookstore_mapping_id uuid primary key,
	price int not null check (price >= 0),
  store_quantity int not null check (store_quantity >= 0),
  book_id uuid,
	bookstore_id uuid,
	constraint f_book_id
		foreign key (book_id)
		references book(book_id),
	constraint fk_bookstore_id
		foreign key (bookstore_id)
		references bookstore(bookstore_id)
);

create table if not exists cart_item(
	cart_item_id uuid primary key,
	cart_id uuid not null,
	quantity int not null check (quantity >= 0),
	book_bookstore_mapping_id uuid,
	constraint fk_cart_id
		foreign key (cart_id)
		references shopping_cart(cart_id),
	constraint fk_book_bookstore_mapping_id
		foreign key (book_bookstore_mapping_id)
		references book_bookstore_mapping(book_bookstore_mapping_id)
);

create table if not exists order_item (
	order_item_id uuid primary key,
	quantity int not null check (quantity >= 0),
	price int check (price >= 0),
	order_id uuid,
	book_bookstore_mapping_id uuid,
	constraint fk_order
		foreign key (order_id)
		references order_(order_id),
	constraint fk_book_bookstore_mapping_id
		foreign key (book_bookstore_mapping_id)
		references book_bookstore_mapping(book_bookstore_mapping_id)
);