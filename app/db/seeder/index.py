import asyncio
import os
import uuid
from datetime import date, timedelta
from decimal import Decimal

# 從專案中導入設定和資料庫連線
from app.core.config import settings
from app.db.db import session_factory, engine

# 導入密碼雜湊工具
from app.util.auth import hash_password 

# 導入所有 ORM 模型
from app.db.models.admin import Admin
from app.db.models.customer import Customer
from app.db.models.staff import Staff
from app.db.models.bookstore import Bookstore
from app.db.models.book import Book
from app.db.models.book_bookstore_mapping import BookBookstoreMapping
from app.db.models.coupon import Coupon
from app.db.models.shopping_cart import ShoppingCart
from app.db.models.cart_item import CartItem
from app.db.models.order import Order
from app.db.models.order_item import OrderItem


# -----------------------------------------------------------
# 輔助函式：使用 uuid.uuid5 根據名稱生成固定的 UUID，確保每次運行結果一致
# -----------------------------------------------------------
def generate_deterministic_uuid(name: str) -> uuid.UUID:
    """Generates a reproducible UUID based on a namespace and a fixed name."""
    # 使用 uuid.NAMESPACE_DNS 作為命名空間，確保結果固定
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)
    
# -----------------------------------------------------------
# 定義範例資料的 ID (用於連結外鍵)
# -----------------------------------------------------------
ADMIN_ACCOUNT = "admin_001"
CUSTOMER_ACCOUNT = "customer_A"
STAFF_ACCOUNT = "staff_B"

# [新增] 第二個顧客與書店的識別常數
CUSTOMER_ACCOUNT_B = "customer_B"
BOOKSTORE_NAME_2 = "Second Page Bookstore"

# ... (現有的 UUID 定義)
BOOKSTORE_UUID = generate_deterministic_uuid("Bookworm Bookstore")

# [新增] 第二個書店的固定 UUID
BOOKSTORE_UUID_2 = generate_deterministic_uuid(BOOKSTORE_NAME_2)
# 為了讓新書店有書賣，我們也為它建立商品關聯 (BookBookstoreMapping) 的 UUID
BBM_UUID_3 = generate_deterministic_uuid("BBM_Python_SecondPage")
BBM_UUID_4 = generate_deterministic_uuid("BBM_SQLA_SecondPage")
# 為新顧客建立購物車 UUID
CART_UUID_B = generate_deterministic_uuid(CUSTOMER_ACCOUNT_B + "_cart")
# 安全性修正: 從環境變數讀取密碼，若未設定則使用預設值 (僅供開發用)
DEFAULT_PASSWORD = os.getenv("SEED_USER_PASSWORD", "123")

# 固定的 UUID 以便測試和重現
# 使用 generate_deterministic_uuid 函式根據名稱生成，確保 UUID 穩定不變
BOOKSTORE_UUID = generate_deterministic_uuid("Bookworm Bookstore")
BOOK_UUID_1 = generate_deterministic_uuid("Python Database Application Book")
BOOK_UUID_2 = generate_deterministic_uuid("Mastering SQLAlchemy Book")
BBM_UUID_1 = generate_deterministic_uuid("BBM_Python_Bookworm")
BBM_UUID_2 = generate_deterministic_uuid("BBM_SQLA_Bookworm")
COUPON_UUID = generate_deterministic_uuid("New Customer Discount")
CART_UUID = generate_deterministic_uuid(CUSTOMER_ACCOUNT + "_cart")
ORDER_UUID = generate_deterministic_uuid(CUSTOMER_ACCOUNT + "_order")


async def seed_data():
    """
    資料填充函式，用於 populate 數據庫表格。
    """
    # 預先雜湊密碼
    hashed_password = hash_password(DEFAULT_PASSWORD)
    
    # 1. 獲取一個新的非同步會話
    async with session_factory() as db:
        print("--- 開始資料填充程序 ---")

        # 2. 基礎資料: Admin, Customer, Bookstore, Staff, Book

        # Admin (db/models/admin.py)
        admin_user = Admin(
            account=ADMIN_ACCOUNT,
            name="系統管理員",
            password=hashed_password, 
        )

        # Customer (db/models/customer.py)
        customer = Customer(
            account=CUSTOMER_ACCOUNT,
            name="王小明",
            password=hashed_password,
            phone_number="0912345678",
            email="ming@example.com",
            address="台北市信義區忠孝東路一段1號",
        )

        # Bookstore (db/models/bookstore.py)
        bookstore = Bookstore(
            bookstore_id=BOOKSTORE_UUID,
            name="Bookworm 書店",
            phone_number="0212345678",
            email="bookworm@store.com",
            address="新北市板橋區文化路二段1號",
            shipping_fee=60,  # 運費
        )

        # Staff (db/models/staff.py) - 依賴 Bookstore
        staff_user = Staff(
            account=STAFF_ACCOUNT,
            name="陳店員",
            password=hashed_password,
            bookstore_id=BOOKSTORE_UUID,
        )

        # Book 1 (db/models/book.py)
        book_1 = Book(
            book_id=BOOK_UUID_1,
            title="Python 資料庫應用",
            author="李大偉",
            publisher="技術出版社",
            isbn="978-986-7798-00-1",
            category="程式設計",
            publish_date=date(2023, 10, 15),
        )

        # Book 2 (db/models/book.py)
        book_2 = Book(
            book_id=BOOK_UUID_2,
            title="精通SQLAlchemy",
            author="林小美",
            publisher="程式設計出版社",
            isbn="978-986-7798-00-2",
            category="程式設計",
            publish_date=date(2024, 1, 20),
        )

        # 效率優化: 移除此處的 db.add_all 與 db.flush()，改至最後統一處理

        # 3. 中繼資料: BookBookstoreMapping, Coupon

        # BookBookstoreMapping 1 (db/models/book_bookstore_mapping.py) - 依賴 Book, Bookstore
        bbm_1 = BookBookstoreMapping(
            book_bookstore_mapping_id=BBM_UUID_1,
            price=550,
            store_quantity=100,
            book_id=BOOK_UUID_1,
            bookstore_id=BOOKSTORE_UUID,
        )

        # BookBookstoreMapping 2
        bbm_2 = BookBookstoreMapping(
            book_bookstore_mapping_id=BBM_UUID_2,
            price=480,
            store_quantity=50,
            book_id=BOOK_UUID_2,
            bookstore_id=BOOKSTORE_UUID,
        )

        # Coupon (db/models/coupon.py) - 依賴 Admin
        coupon = Coupon(
            coupon_id=COUPON_UUID,
            type="新客折扣",
            discount_percentage=Decimal("0.10"),  # 10% 折扣
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            admin_account=ADMIN_ACCOUNT,
        )

        # 效率優化: 移除 flush

        # 4. 購物車資料: ShoppingCart, CartItem

        # ShoppingCart (db/models/shopping_cart.py) - 依賴 Customer
        shopping_cart = ShoppingCart(
            cart_id=CART_UUID,
            customer_account=CUSTOMER_ACCOUNT,
        )

        # 效率優化: 移除 flush

        # CartItem 1 (db/models/cart_item.py) - 依賴 ShoppingCart, BookBookstoreMapping
        cart_item_1 = CartItem(
            quantity=1,
            cart_id=CART_UUID,
            book_bookstore_mapping_id=BBM_UUID_1,
        )

        # CartItem 2
        cart_item_2 = CartItem(
            quantity=2,
            cart_id=CART_UUID,
            book_bookstore_mapping_id=BBM_UUID_2,
        )
        
        # [新增] Customer B (db/models/customer.py)
        customer_b = Customer(
            account=CUSTOMER_ACCOUNT_B,
            name="李小華",
            password=hashed_password,
            phone_number="0998765432",
            email="hua@example.com",
            address="台中市西屯區台灣大道三段99號",
        )

        # [新增] Bookstore 2 (db/models/bookstore.py)
        bookstore_2 = Bookstore(
            bookstore_id=BOOKSTORE_UUID_2,
            name="Second Page 書店",
            phone_number="0423456789",
            email="second@store.com",
            address="高雄市前鎮區三多三路213號",
            shipping_fee=50,
        )

        # ... (現有的 Staff, Book 建立程式碼)

        # [新增] 為新書店上架現有的書籍 (BookBookstoreMapping)
        # 讓這家書店的價格稍微不同，模擬真實情況
        bbm_3 = BookBookstoreMapping(
            book_bookstore_mapping_id=BBM_UUID_3,
            price=520, # 另一家賣 550
            store_quantity=30,
            book_id=BOOK_UUID_1, # Python 資料庫應用
            bookstore_id=BOOKSTORE_UUID_2,
        )

        bbm_4 = BookBookstoreMapping(
            book_bookstore_mapping_id=BBM_UUID_4,
            price=500, # 另一家賣 480
            store_quantity=20,
            book_id=BOOK_UUID_2, # 精通SQLAlchemy
            bookstore_id=BOOKSTORE_UUID_2,
        )

        # [新增] 為新顧客建立購物車
        shopping_cart_b = ShoppingCart(
            cart_id=CART_UUID_B,
            customer_account=CUSTOMER_ACCOUNT_B,
        )

        # 效率優化: 移除 flush

        # 5. 訂單資料: Order, OrderItem

        # 計算訂單總價 (含 10% 折扣和運費)
        # 正確性修正: 使用 round() 代替 int() 以避免精度問題
        total_price = round(
            (bbm_1.price * cart_item_1.quantity + bbm_2.price * cart_item_2.quantity)
            * (1 - coupon.discount_percentage)
            + bookstore.shipping_fee
        )

        # Order (db/models/order.py) - 依賴 Customer, Coupon
        order = Order(
            order_id=ORDER_UUID,
            order_time=date.today(),
            customer_name=customer.name,
            customer_phone_number=customer.phone_number,
            customer_email=customer.email,
            status="待出貨",
            total_price=total_price,
            shipping_address=customer.address,
            shipping_fee=bookstore.shipping_fee,
            recipient_name="王小明",
            coupon_id=COUPON_UUID,
            customer_account=CUSTOMER_ACCOUNT,
        )

        # 效率優化: 移除 flush

        # OrderItem 1 (db/models/order_item.py) - 依賴 Order, BookBookstoreMapping
        order_item_1 = OrderItem(
            quantity=cart_item_1.quantity,
            price=bbm_1.price,
            order_id=ORDER_UUID,
            book_bookstore_mapping_id=BBM_UUID_1,
        )

        # OrderItem 2
        order_item_2 = OrderItem(
            quantity=cart_item_2.quantity,
            price=bbm_2.price,
            order_id=ORDER_UUID,
            book_bookstore_mapping_id=BBM_UUID_2,
        )

        # 6. 提交事務
        # 效率優化: 將所有物件一次性加入 Session 並提交
        db.add_all([
            admin_user, customer, bookstore, staff_user, book_1, book_2,
            bbm_1, bbm_2, coupon,
            shopping_cart, cart_item_1, cart_item_2,
            order, order_item_1, order_item_2,
            customer_b, bookstore_2, bbm_3, bbm_4, shopping_cart_b
        ])
        
        await db.commit()
        print("--- 資料填充成功完成 ---")
        # 安全性修正: 移除在控制台中印出密碼的行為
        print(f"成功創建的管理員帳號: {ADMIN_ACCOUNT}")
        print(f"成功創建的客戶帳號: {CUSTOMER_ACCOUNT}")
        print(f"成功創建的員工帳號: {STAFF_ACCOUNT}")


if __name__ == "__main__":
    try:
        # Pydantic Settings 在這裡會載入 .env 檔案
        print(f"使用的資料庫 URI: {settings.DATABASE_URI}")
        print("請確保您的資料庫已啟動且表格已初始化（例如：運行 Alembic 遷移）後再執行此腳本。")
        asyncio.run(seed_data())
    except Exception as e:
        print(f"資料填充過程中發生錯誤: {e}")
        # 錯誤時釋放連線池
        asyncio.run(engine.dispose())
