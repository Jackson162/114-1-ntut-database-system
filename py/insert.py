import psycopg2
from psycopg2 import OperationalError, ProgrammingError
from typing import List, Dict, Any

# --- 資料庫連線設定 ---
# --- 設定您的資料庫連線參數 ---
DB_SETTINGS = {
    "db_name": "Multi-bookstore e-commerce platform",       # 替換為您的資料庫名稱
    "db_user": "postgres",             # 替換為您的使用者名稱
    "db_password": "2147483647",         # 替換為您的密碼
    "db_host": "localhost",                 # 替換為您的主機位址 (或 IP)
    "db_port": "5432"                       # 替換為您的連接埠 (PostgreSQL 預設為 5432)
}

def execute_sql_file(db_config: Dict[str, str], sql_file_path: str) -> List[Dict[str, Any]]:
    """
    讀取單個 SQL 檔案內容並在 PostgreSQL 資料庫上執行指令，同時回傳執行結果。

    Args:
        db_config (dict): 包含 'db_name', 'db_user', 'db_password', 'db_host', 'db_port' 的字典。
        sql_file_path (str): 要執行的 SQL 檔案路徑。

    Returns:
        List[Dict[str, Any]]: 包含每個指令執行結果的列表。
    """
    conn = None
    results = [] # 用來儲存每個 SQL 指令的結果訊息或查詢資料
    
    db_name = db_config["db_name"]
    
    print(f"\n=======================================================")
    print(f"🚀 開始執行檔案: {sql_file_path}")
    print(f"=======================================================")

    try:
        # 1. 建立資料庫連線
        print(f"正在連線到 PostgreSQL 資料庫 '{db_name}'...")
        conn = psycopg2.connect(
            database=db_name,
            user=db_config["db_user"],
            password=db_config["db_password"],
            host=db_config["db_host"],
            port=db_config["db_port"]
        )
        conn.autocommit = False 
        cursor = conn.cursor()

        # 2. 讀取 SQL 檔案內容並以分號 (;) 分割成單個指令
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            # 過濾空行或註解行
            sql_commands = [
                cmd.strip() 
                for cmd in file.read().split(';') 
                if cmd.strip() and not cmd.strip().startswith('--')
            ]
        
        # 3. 逐一執行 SQL 指令
        for i, command in enumerate(sql_commands):
            print(f"\n--- 執行指令 {i+1} ---")
            
            # 執行指令
            cursor.execute(command)

            try:
                # 嘗試獲取查詢結果 (適用於 SELECT)
                fetched_data = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                
                result_message = f"✅ SELECT 查詢成功。共回傳 {len(fetched_data)} 筆資料。"
                print(result_message)
                
                results.append({
                    "file": sql_file_path,
                    "command_index": i + 1,
                    "type": "SELECT",
                    "message": result_message,
                    "rowcount": len(fetched_data),
                    "columns": column_names,
                    "data": fetched_data
                })

            except ProgrammingError:
                # DML/DDL 語句的處理
                row_count = cursor.rowcount
                
                if row_count > -1:
                    result_message = f"✅ 資料操作成功 (DML)。受影響行數: {row_count}。"
                else:
                    result_message = f"✅ 資料庫結構操作成功 (DDL)。Rowcount: {row_count}。"

                print(result_message)
                results.append({
                    "file": sql_file_path,
                    "command_index": i + 1,
                    "type": "DML/DDL",
                    "message": result_message,
                    "rowcount": row_count
                })
                
        # 4. 提交事務 (Commit)
        conn.commit()
        print(f"\n✅ 檔案 {sql_file_path} 中所有指令執行成功並已提交事務。")

    except OperationalError as e:
        print(f"\n❌ 資料庫連線或操作發生錯誤: {e}")
        if conn:
            conn.rollback() # 如果發生錯誤，回滾事務
            print("❗ 事務已回滾 (Rollback)。")
    except FileNotFoundError:
        print(f"\n❌ 找不到指定的 SQL 檔案: {sql_file_path}")
    except Exception as e:
        print(f"\n❌ 發生未知錯誤: {e}")
        if conn:
            conn.rollback()
            print("❗ 事務已回滾 (Rollback)。")
    finally:
        # 5. 關閉連線
        if conn:
            conn.close()
            print("資料庫連線已關閉。")
            
    return results

# --- 執行主程式 ---
if __name__ == "__main__":
    
    # 📝 步驟 1: 設定要依序執行的 SQL 檔案路徑列表
    # 請根據您的實際檔案名稱和路徑修改此列表。
    SQL_FILES_TO_EXECUTE = [
        "../sql/drop_all_table.sql",
        "../sql/create_table.sql",
        "../sql/select_admin.sql",
        "../sql/insert_admin.sql",
        "../sql/insert_bookstore.sql",
        # ...
        "../sql/select_admin.sql"
    ]
    
    all_execution_results = []
    
    # 📝 步驟 2: 依序執行列表中的每個 SQL 檔案
    for sql_file in SQL_FILES_TO_EXECUTE:
        
        # 檢查檔案是否存在，防止在迴圈一開始就因為檔案路徑錯誤而停止
        try:
            with open(sql_file, 'r'):
                pass
        except FileNotFoundError:
            print(f"\n⚠️ 跳過檔案: {sql_file} - 檔案不存在。請檢查路徑。")
            continue
            
        results = execute_sql_file(
            db_config=DB_SETTINGS,
            sql_file_path=sql_file
        )
        all_execution_results.extend(results)
    
    # 📝 步驟 3: 顯示所有檔案的總結
    print("\n\n=======================================================")
    print("✨ 所有 SQL 檔案執行任務完成 ✨")
    print("=======================================================")
    
    total_select_rows = 0
    
    for res in all_execution_results:
        # 顯示指令摘要
        if res['type'] == 'SELECT':
            print(f"檔案: {res['file']} - 指令 {res['command_index']}: {res['message']}")
            total_select_rows += res['rowcount']
            
            # 如果是查詢，顯示獲取的資料
            if res['data']:
                print(f"    - 查詢欄位: {res['columns']}")
                print(f"    - 查詢結果範例 (前3筆): {res['data'][:3]}")
                if len(res['data']) > 3:
                     print("    ...")
                     
        elif res['type'] == 'DML/DDL':
            print(f"檔案: {res['file']} - 指令 {res['command_index']}: {res['message']}")
            

    print("\n--- 總體統計 ---")
    print(f"🔍 總共查詢到資料筆數: {total_select_rows} 筆")