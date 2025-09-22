多書店電子商務平台 (Multi-Bookstore e-Commerce Platform)
系統需求規格書
Software Requirements Specification (SRS)
版本：1.0

謝華殷 學號：隨班附讀 電子郵件：jackson97042@gmail.com

國立臺北科技大學
資訊工程系
Department of Computer Science & Information Engineering
National Taipei University of Technology

日期：________________

================================================================================

目錄 (Table of Contents)

Section 1 簡介 (Introduction)
1.1 目的 (Purpose)
1.2 系統名稱 (Identification)
1.3 概觀 (Overview)
1.4 符號描述 (Notation Description)

Section 2 系統 (System)
2.1 系統描述 (System Description)
2.1.1 系統架構圖 (System Architecture Diagram)
2.2 操作概念 (Operational Concepts or User Stories)
2.3 功能性需求 (Functional Requirements)
2.4 資料需求 (Data Requirements)
2.5 非功能性需求 (Non-Functional Requirements)
2.5.1 效能需求 (Performance Requirements)
2.5.2 資安需求 (Security Requirements)
2.6 介面需求 (Interface Requirements)
2.6.1 使用者介面需求 (User Interfaces Requirements)
2.6.2 外部介面需求 (External Interface Requirements)
2.6.3 內部介面需求 (Internal Interface Requirements)
2.7 其他需求 (Other Requirements)
2.7.1 環境需求 (Environmental Requirement)
2.7.2 安裝需求 (Installation Requirement)
2.7.3 測試需求 (Test Requirements)
2.8 商業規則與限制 (Business Rules and Integrity Constrains)

Glossary 詞彙表
References 參考資料
Appendix 附錄

================================================================================

Section 1 簡介 (Introduction)

1.1 目的 (Purpose)

近年來線上書店的普及，使得多書店電商模式逐漸興起，讀者可以在同一平台上找到來自不同書店的書籍。然而，我們通常是以「使用者」的身分使用這些系統，而較少站在「開發者」的角度思考。本課程將透過開發一個多書店電子商務平台，讓我們有機會從「開發者」的角度來建構資料庫系統。藉由此專案，我們不僅能學習課堂知識，還能更深入了解資料庫系統的建構、運作及應用。

1.2 系統名稱 (Identification)

本專案將實作一個多書店電子商務平台系統，名為「Multi-Bookstore Platform」，允許多個書店在平台上開設線上書店、管理書籍庫存，而讀者可以在平台上瀏覽、搜尋和購買來自不同書店的書籍。使用者將分為三種不同的身分：顧客、員工及系統管理員。每個書店都有自己的員工來管理書店，每個書店類似一個獨立的店家工作區（workspace for store），擁有自己的書籍管理空間。這三種身分在系統中擁有不同的權限與功能，每種身分也會有不同的資料表來儲存對應的資訊。不同身分間的資訊交換將透過關聯式資料庫來執行。

1.3 概觀 (Overview)

此系統由一個主系統和數個子系統組成：

主系統：
多書店電子商務平台 (Multi-Bookstore e-Commerce Platform, MBCP)

子系統：
• 使用者管理子系統 (User Management Subsystem, UMS)
• 書店管理子系統 (Bookstore Management Subsystem, BMS)
• 書籍管理子系統 (Book Management Subsystem, BKS)
• 訂單處理子系統 (Order Processing Subsystem, OPS)
• 折扣管理子系統 (Discount Management Subsystem, DMS)
報表子系統 (Reporting Subsystem, RS)
資料庫子系統(Databas Subsystem, DS)

1.4 符號描述 (Notation Description)

符號                    描述
MBCP1.0.0              多書店電商平台版本號為1.0.0
UMS 1.1.n              使用者管理子系統元件編號為1.1.n
BMS 1.2.n              書店管理子系統元件編號為1.2.n
BKS 1.3.n              書籍管理子系統元件編號為1.3.n
OPS 1.4.n              訂單處理子系統元件編號為1.4.n
DMS 1.5.n              折扣管理子系統元件編號為1.5.n
RS 1.6.n               報表子系統元件編號為1.6.n

符號                    描述
MBCP-I-n               MBCP 介面需求
MBCP-F-n               MBCP 功能性需求
MBCP-D-n               MBCP 資料需求
MBCP-N-n               MBCP 非功能性需求
MBCP-O-n               MBCP 其他需求
MBCP-R-n               MBCP 商業規則或限制

================================================================================

Section 2 系統 (System)

2.1 系統描述 (System Description)

此專案將開發一個多書店電子商務平台 (Multi-Bookstore Platform)，該系統將分為一個主系統和多個子系統。在主系統中有使用者管理子系統(UMS)、書店管理子系統(BMS)、書籍管理子系統(BKS)、訂單處理子系統(OPS)、折扣管理子系統(DMS)及報表子系統(RS)。系統將使用FastAPI框架進行後端API開發，搭配PostgreSQL資料庫進行資料管理。

2.1.1 系統架構圖 (System Architecture Diagram)

多書店電子商務平台 (Multi-Bookstore e-Commerce Platform)
├── 使用者管理子系統 (User Management Subsystem)
├── 書店管理子系統 (Bookstore Management Subsystem)
├── 書籍管理子系統 (Book Management Subsystem)
├── 訂單處理子系統 (Order Processing Subsystem)
├── 折扣管理子系統 (Discount Management Subsystem)
├── 報表子系統 (Reporting Subsystem)
└── 資料庫子系統(Databas Subsystem, DS)

2.2 操作概念 (Operational Concepts or User Stories)

當使用者進入系統時，使用者管理子系統(UMS)將使用帳戶 (account) 和密碼（password） 進行身分驗證，提供使用者登入和登出系統，並提供使用者註冊為顧客的功能。系統有三種使用者類型：顧客 (customer)、員工(staff)和系統管理員(system admin)，每種類型具有不同的權限：

• 顧客可以搜尋和購買來自不同書店的書籍，管理購物車，查看訂單歷史
• 員工屬於特定書店，可以管理該書店的店家工作區（workspace for store），包括書籍上架、庫存管理、訂單處理、書店設定等。每個書店都有自己的員工團隊
• 系統管理員可以管理整個平台、使用者帳號、系統設定、審核書店申請

2.3 功能性需求 (Functional Requirements)

編號                    描述
MBCP-F-01              系統應允許驗證和授權使用者
MBCP-F-01.1            系統應具有三種使用者類型：顧客、員工和系統管理員，每種使用者類型具有不同權限
MBCP-F-01.2            系統應允許使用者登入和登出系統
MBCP-F-01.3            系統應使用 帳戶(account) 和密碼（password） 驗證使用者身分
MBCP-F-01.4            員工必須關聯到特定的書店，只能管理該書店的資料
MBCP-F-01.5            系統應允許使用者註冊成為顧客

MBCP-F-02              系統應允許顧客搜尋書籍、訂購書籍及查看訂單歷史記錄
MBCP-F-02.1            系統應允許顧客跨書店搜尋書籍
MBCP-F-02.2            系統應具有購物車功能，允許顧客加入來自不同書店的書籍
MBCP-F-02.3            系統應在顧客結帳時按書店分別計算訂單金額
MBCP-F-02.4            系統應允許顧客查詢其訂單歷史記錄，包括來自不同書店的訂單
MBCP-F-02.5            系統應在顧客下訂單後自動發送訂單確認電子郵件給顧客 (選擇性功能)

MBCP-F-03              系統應允許員工管理所屬書店的書籍和營運
MBCP-F-03.1            系統應為每個書店的員工提供該書店的店家工作區（workspace for store）管理介面
MBCP-F-03.2            系統應允許員工管理所屬書店的書籍，包括新增、更新、查詢和刪除書籍
MBCP-F-03.3            系統應允許員工管理所屬書店的資訊，包括書店名稱、描述、聯絡資訊
MBCP-F-03.4            系統應允許員工查看和處理所屬書店的訂單
MBCP-F-03.5            系統應確保員工只能存取所屬書店的資料，無法存取其他書店的資料

MBCP-F-04              系統應允許系統管理員管理平台運營
MBCP-F-04.1            系統應允許系統管理員審核書店申請


MBCP-F-04.2          系統應允許系統管理員管理所有使用者帳號

MBCP-F-05              系統應允許員工和系統管理員為書籍定義各種折扣政策
MBCP-F-05.1            系統應允許員工管理所屬書店的折扣政策
MBCP-F-05.2            系統應允許系統管理員設定全平台的折扣活動
MBCP-F-05.3            系統應支援三種類型的折扣政策：運費折扣(shipping)、季節性折扣(seasonings)和特別活動折扣(special event)

MBCP-F-06              系統應允許生成相應的報表或統計資料
MBCP-F-06.1            系統應為員工提供所屬書店的銷售報表        

MBCP-F-07              系統應持續追蹤訂單狀態 (選擇性功能)
MBCP-F-07.1            系統應在訂單提交後自動追蹤訂單狀態（已接收、處理中、配送中或已完成）
MBCP-F-07.2            系統應允許員工更新所屬書店訂單的配送狀態

MBCP-F-08              其他期望功能
MBCP-F-08.1            系統應提供RESTful API介面供前端使用
MBCP-F-08.2            系統應支援對書店進行評分和/或撰寫評論意見 (選擇性功能)
MBCP-F-08.3            系統應支援「購買此書籍的顧客也購買了」功能 (選擇性功能)


2.4 資料需求 (Data Requirements)

編號                    描述
MBCP-D-01              系統應包含使用者資訊：帳戶、姓名、密碼、電子郵件、地址、使用者類型
MBCP-D-01.1            假設所有員工跟系統管理員的資訊都是資料庫的初始狀態
MBCP-D-01.2            員工必須關聯到特定的書店ID，表示其工作的書店

MBCP-D-02              系統應包含書店資訊：bookstoreID、書店名稱、電子郵件、營業地址、電話

MBCP-D-03              系統應包含員工與書店關聯資訊
MBCP-D-03.1            每個員工必須關聯到特定書店

MBCP-D-04              系統應包含書籍資訊：bookID、bookstoreID、書名、作者、ISBN、出版社、出版日期、價格、庫存數量、書籍分類、書籍描述
MBCP-D-04.1            每本書籍必須關聯到特定的書店
MBCP-D-04.2            書籍應支援多張圖片和詳細資訊

MBCP-D-05              系統應包含訂單資訊，並反正規化儲存所有資料，確保訂單資訊不會改變
MBCP-D-05.1            訂單應按書店分別處理，一個購物車可能產生多個訂單
MBCP-D-05.2            訂單狀態包括：已接收、處理中、配送中、已完成、已取消

MBCP-D-06              帳戶(account)、及其他資料的 ID 均為唯一值

MBCP-D-07              銷售報表可包含日期、書店名稱、訂單數量、銷售總金額、書籍分類統計

2.5 非功能性需求 (Non-Functional Requirements)

2.5.1 效能需求 (Performance Requirements)

編號                    描述
MBCP-N-01              正常負載下API回應時間應少於3秒

2.5.2 資安需求 (Security Requirements)

編號                    描述
MBCP-N-02              所有API端點必須經過身分驗證，且資料存取必須限制於經授權的使用者
MBCP-N-03              員工只能透過API存取所屬書店的店家工作區（workspace for store）資料，不能存取其他書店的資料
MBCP-N-4            API應使用JWT令牌進行身分驗證
MBCP-N-5             系統必須驗證員工與書店的關聯關係

2.6 介面需求 (Interface Requirements)

2.6.1 使用者介面需求 (User Interfaces Requirements)

編號                    描述
MBCP-I-01              系統應提供RESTful API供前端介面使用
MBCP-I-03              不同使用者角色應根據其權限存取適當的API端點
MBCP-I-04              員工應有特定書店店家工作區（workspace for store）的API端點
MBCP-I-05              API回應應包含適當的HTTP狀態碼和錯誤訊息

2.6.2 外部介面需求 (External Interface Requirements)

編號                    描述
MBCP-I-06              系統應支援SMTP協定發送電子郵件通知（選擇性功能）
MBCP-I-07              所有API通訊應使用HTTPS進行安全傳輸選擇性功能）
MBCP-I-08              系統應支援第三方付款服務API整合選擇性功能）
MBCP-I-09              系統應支援第三方物流服務API整合選擇性功能）


2.6.3 內部介面需求 (Internal Interface Requirements)

編號                    描述
MBCP-I-10              UMS應管理所有其他子系統的JWT令牌驗證
MBCP-I-11              BMS應與BKS整合，確保員工只能透過API管理所屬書店的書籍
MBCP-I-12              OPS應從BKS和BMS取得書店和書籍資訊並反正規化記錄下來
MBCP-I-13              DMS應支援書店級別和平台級別的折扣管理API
MBCP-I-14              RS應能透過API提供書店級別和平台級別的報表

2.7 其他需求 (Other Requirements)

2.7.1 環境需求 (Environmental Requirement)

編號                    描述
MBCP-O-01              伺服器需64位元四核心處理器2.5GHz以上
MBCP-O-02              資料庫伺服器最少需要2 GB記憶體
MBCP-O-03              至少需要1TB儲存空間供PostgreSQL資料庫及媒體檔案使用 （這個你們查一下寫多少比較好）


2.7.2 安裝需求 (Installation Requirement)

編號                    描述
MBCP-O-05              PostgreSQL 14.0或更高版本進行資料庫管理
MBCP-O-06              Python 3.9+執行環境
MBCP-O-07              FastAPI框架進行後端API開發
MBCP-O-08              Uvicorn ASGI伺服器
MBCP-O-09              SQLAlchemy ORM進行資料庫操作
MBCP-O-10              Pydantic進行資料驗證和序列化
MBCP-O-11             Alembic進行資料庫遷移管理

2.7.3 測試需求 (Test Requirements)

編號                    描述
MBCP-O-13              系統必須通過人工QA測試確保功能正常

2.8 商業規則與限制 (Business Rules and Integrity Constrains)

編號                    描述
MBCP-R-01              員工只能透過API管理所屬書店店家工作區（workspace for store）內的書籍和訂單
MBCP-R-02              一本書籍只能屬於一個書店
MBCP-R-03              一個員工只能屬於一個書店
MBCP-R-04              訂單必須按書店分別處理，即使來自同一個購物車
MBCP-R-05              三種類型的折扣可以同時應用於同一筆購買
MBCP-R-06              書店特別活動折扣期間不能重疊
MBCP-R-07              每本已購買書籍的數量必須是大於零的整數
MBCP-R-08              全部人購買書籍的數量必須小於或等於該書籍的當前庫存數量
MBCP-R-09              所有資料庫操作必須在事務(Transaction)中進行確保資料的一致性
MBCP-R-10              API回應時間超過5秒應視為逾時
MBCP-R-15              書籍的ISBN必須符合國際標準格式


================================================================================

Glossary 詞彙表

MBCP - 多書店電子商務平台 (Multi-Bookstore e-Commerce Platform)
UMS - 使用者管理子系統 (User Management Subsystem)
BMS - 書店管理子系統 (Bookstore Management Subsystem)
BKS - 書籍管理子系統 (Book Management Subsystem)
OPS - 訂單處理子系統 (Order Processing Subsystem)
DMS - 折扣管理子系統 (Discount Management Subsystem)
RS - 報表子系統 (Reporting Subsystem)
SRS - 系統需求規格書 (Software Requirements Specification)
API - 應用程式介面 (Application Programming Interface)
JWT - JSON Web Token，用於API身分驗證
ORM - 物件關聯映射 (Object-Relational Mapping)
ASGI - 異步伺服器閘道介面 (Asynchronous Server Gateway Interface)
店家工作區（Workspace for Store）- 書店工作空間，每個書店的獨立管理環境
Bookstore - 書店，在平台上開設線上書店的商家
Multi-Bookstore - 多書店，支援多個書店在同一平台販售的模式
Staff - 員工，屬於特定書店的工作人員
ISBN - 國際標準書號 (International Standard Book Number)
帳戶(Account) - 使用者的登入識別碼

================================================================================

References 參考資料
補連結！！！！！！！！！
Alembic
Pydantic
Fastapi
Postgresql 


================================================================================

Appendix 附錄

