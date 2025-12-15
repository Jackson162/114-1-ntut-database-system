import asyncio
from sqlalchemy import text
from app.db.db import engine
from app.db.models.base import Base
# 導入所有 Models 以便 Base.metadata 能夠識別所有表格
import app.db.models  # noqa
from app.core.config import settings

async def drop_all_tables():
    print(f"正在連線至資料庫: {settings.DATABASE_URI}")
    print("警告: 這將會刪除所有資料表與資料！")
    
    async with engine.begin() as conn:
        # 1. 刪除所有 SQLAlchemy 定義的表格
        print("正在刪除應用程式表格...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # 2. 額外刪除 alembic_version 表格 (重置 Migration 狀態)
        print("正在刪除 Migration 版本紀錄 (alembic_version)...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    
    print("所有表格已成功刪除。")

async def main():
    try:
        await drop_all_tables()
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        # 確保關閉 engine 釋放連線
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())