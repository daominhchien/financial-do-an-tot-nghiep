# 📊 Hệ Thống Hỗ Trợ Đầu Tư - Phân Tích Cơ Bản Cổ Phiếu Việt Nam

## 🏗️ Kiến Trúc Hệ Thống

```
┌──────────────────┐     ┌────────────────┐     ┌──────────────────┐
│  ETL Pipeline    │     │  Backend API   │     │    Frontend      │
│  (Python)        │────►│  (Spring Boot) │────►│    (React)       │
│                  │ CSV │                │ JSON│                  │
│  vnstock API     │     │  MySQL DB      │     │  localhost:5173   │
│  → CSV output    │     │  localhost:8080 │     │                  │
└──────────────────┘     └────────────────┘     └──────────────────┘
```

---

## 📋 Yêu Cầu Hệ Thống

| Phần mềm           | Phiên bản  | Ghi chú                     |
| ------------------- | ---------- | --------------------------- |
| **Java JDK**        | 21+        | Cần cho Spring Boot         |
| **MySQL**           | 8.0+       | Database                    |
| **Python**          | 3.10+      | ETL pipeline                |
| **Node.js**         | 18+        | Frontend React              |
| **Maven**           | 3.9+       | Build backend               |
| **IntelliJ IDEA**   | Bất kỳ     | IDE chạy backend (khuyến nghị) |

---

## 🚀 Hướng Dẫn Chạy Từng Bước

### Bước 1️⃣: Chuẩn bị MySQL

Đảm bảo MySQL đang chạy, database `investment_db` sẽ tự tạo khi backend khởi động.

Kiểm tra:
```bash
mysql -u root -p
# Nhập password: chien1207
```

---

### Bước 2️⃣: Chạy ETL Pipeline (lấy dữ liệu tài chính)

```bash
cd C:\Users\admin\Downloads\doantotnghiep\financial-etl-pipeline

# Cài dependencies (lần đầu)
pip install -r requirements.txt

# Chạy ETL
py main.py --symbols VNM FPT VIC HPG
```

#### Các cách chạy ETL:

| Lệnh | Mô tả |
| ----- | ----- |
| `py main.py --symbols VNM FPT VIC` | Lấy dữ liệu các mã cụ thể |
| `py main.py --sector vn30` | Lấy 30 mã VN30 (blue-chip) |
| `py main.py --sector banking` | Lấy mã ngành ngân hàng |
| `py main.py --sector real_estate` | Lấy mã ngành bất động sản |
| `py main.py --sector technology` | Lấy mã ngành công nghệ |
| `py main.py --symbols VNM --quick` | Chạy nhanh (chỉ ratios + balance sheet) |
| `py main.py --list` | Xem danh sách các sector có sẵn |

📁 **Kết quả:** File CSV được lưu tại `./output/` và `./output/combined/`

---

### Bước 3️⃣: Chạy Backend Spring Boot

**Cách 1: Chạy bằng IntelliJ (khuyến nghị)**
1. Mở IntelliJ → Open folder `doantotnghiep/backend`
2. Chờ Maven tải dependencies
3. Run file `src/main/java/com/investment/InvestmentApplication.java`

**Cách 2: Chạy bằng Maven CLI**
```bash
cd C:\Users\admin\Downloads\doantotnghiep\backend
mvn spring-boot:run
```

✅ Backend chạy tại: `http://localhost:8080`

---

### Bước 4️⃣: Import dữ liệu CSV vào MySQL

Sau khi backend chạy, import dữ liệu bằng 1 trong 2 cách:

**Cách 1: PowerShell**
```powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:8080/api/admin/import?path=../financial-etl-pipeline/output"
```

**Cách 2: Mở browser gõ trực tiếp** (dùng Postman hoặc curl)
```
POST http://localhost:8080/api/admin/import?path=../financial-etl-pipeline/output
```

**Kết quả mong đợi:**
```json
{
    "success": true,
    "stocksImported": 4,
    "balanceSheetsImported": 211,
    "incomeStatementsImported": 211,
    "ratiosImported": 212
}
```

---

### Bước 5️⃣: Chạy Frontend React

```bash
cd C:\Users\admin\Downloads\doantotnghiep\frontend

# Cài dependencies (lần đầu)
npm install

# Chạy dev server
npm run dev
```

✅ Frontend chạy tại: `http://localhost:5173`

---

## 📡 Danh Sách API Endpoints

### Admin API

| Method | URL | Mô tả | Ví dụ |
| ------ | --- | ----- | ----- |
| `GET` | `/api/admin/health` | Kiểm tra server hoạt động | Trả về `{"status":"UP"}` |
| `POST` | `/api/admin/import?path=...` | Import CSV vào MySQL | `?path=../financial-etl-pipeline/output` |

### Stock API

| Method | URL | Mô tả | Ví dụ Response |
| ------ | --- | ----- | -------------- |
| `GET` | `/api/stocks` | Danh sách tất cả cổ phiếu | `[{"symbol":"VNM","companyName":"VNM",...}]` |
| `GET` | `/api/stocks/{symbol}` | Chi tiết 1 cổ phiếu | `/api/stocks/VNM` |
| `GET` | `/api/stocks/search?q=keyword` | Tìm kiếm cổ phiếu | `/api/stocks/search?q=vin` |
| `GET` | `/api/stocks/exchange/{exchange}` | Lọc theo sàn | `/api/stocks/exchange/HOSE` |
| `GET` | `/api/stocks/industries` | Danh sách ngành | `["Thực phẩm","Ngân hàng",...]` |

### Financial Data API

| Method | URL | Mô tả | Ví dụ |
| ------ | --- | ----- | ----- |
| `GET` | `/api/stocks/{symbol}/balance-sheet` | Bảng cân đối kế toán | `/api/stocks/VNM/balance-sheet` |
| `GET` | `/api/stocks/{symbol}/income-statement` | Báo cáo kết quả kinh doanh | `/api/stocks/VNM/income-statement` |
| `GET` | `/api/stocks/{symbol}/ratios` | Chỉ số tài chính | `/api/stocks/VNM/ratios` |
| `GET` | `/api/stocks/{symbol}/overview` | Tổng quan tài chính mới nhất | `/api/stocks/VNM/overview` |

### So Sánh API

| Method | URL | Mô tả | Ví dụ |
| ------ | --- | ----- | ----- |
| `GET` | `/api/stocks/compare?symbols=X,Y,Z` | So sánh nhiều mã | `/api/stocks/compare?symbols=VNM,FPT,VIC` |

### 🧪 Test API nhanh (mở browser):

```
http://localhost:8080/api/admin/health
http://localhost:8080/api/stocks
http://localhost:8080/api/stocks/VNM
http://localhost:8080/api/stocks/VNM/balance-sheet
http://localhost:8080/api/stocks/VNM/income-statement
http://localhost:8080/api/stocks/VNM/ratios
http://localhost:8080/api/stocks/VNM/overview
http://localhost:8080/api/stocks/compare?symbols=VNM,FPT
```

---

## ⏰ Cập Nhật Dữ Liệu Định Kỳ (Tự Động)

### Script tự động (không cần backend)

```bash
cd C:\Users\admin\Downloads\doantotnghiep\financial-etl-pipeline

# Chạy thủ công
python auto_import_mysql.py --symbols VNM FPT VIC HPG

# Hoặc chạy với VN30
python auto_import_mysql.py --sector vn30
```

Script này sẽ tự động:
1. ✅ Chạy ETL pipeline lấy dữ liệu mới
2. ✅ Import trực tiếp vào MySQL (không cần backend)

### Đặt lịch với Windows Task Scheduler

**Cách 1: Dùng PowerShell (Admin)**
```powershell
# Tạo task chạy mỗi ngày lúc 2h sáng
schtasks /create /tn "AutoUpdateFinancialData" /tr "C:\Users\admin\Downloads\doantotnghiep\auto_update.bat" /sc daily /st 02:00 /f

# Test chạy ngay
schtasks /run /tn "AutoUpdateFinancialData"

# Xem trạng thái
schtasks /query /tn "AutoUpdateFinancialData"

# Xóa task
schtasks /delete /tn "AutoUpdateFinancialData" /f
```

**Cách 2: Dùng GUI**
1. Win + R → gõ `taskschd.msc`
2. Create Basic Task → đặt tên, chọn Daily, chọn giờ
3. Action: Start a program → chọn `auto_update.bat`

> ⚠️ **Lưu ý:** Máy phải bật hoặc Sleep (không Shutdown) để Task Scheduler hoạt động.

---

## 📂 Cấu Trúc Thư Mục

```
doantotnghiep/
├── financial-etl-pipeline/      # 🐍 ETL Pipeline (Python)
│   ├── main.py                  # Entry point chạy ETL
│   ├── auto_import_mysql.py     # Script tự động ETL + MySQL
│   ├── extractors/              # Trích xuất dữ liệu
│   ├── transformers/            # Biến đổi dữ liệu
│   ├── loaders/                 # Lưu CSV
│   └── output/                  # 📁 Dữ liệu CSV đầu ra
│       ├── VNM/                 # Dữ liệu theo mã
│       ├── FPT/
│       └── combined/            # File tổng hợp tất cả mã
│
├── backend/                     # ☕ Backend API (Spring Boot)
│   ├── pom.xml                  # Dependencies (Maven)
│   ├── src/main/java/com/investment/
│   │   ├── InvestmentApplication.java  # Main class
│   │   ├── entity/              # Database entities
│   │   ├── repository/          # JPA repositories
│   │   ├── service/             # Business logic
│   │   ├── controller/          # REST API controllers
│   │   └── config/              # Cấu hình (CORS, etc.)
│   └── src/main/resources/
│       └── application.yml      # Cấu hình MySQL, JPA
│
├── frontend/                    # ⚛️ Frontend (React + Vite)
│   ├── package.json
│   ├── src/
│   └── index.html
│
├── auto_update.bat              # 🔄 Script tự động cập nhật
└── README.md                    # 📖 File này
```

---

## 🔧 Cấu Hình

### MySQL (`backend/src/main/resources/application.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/investment_db?createDatabaseIfNotExist=true
    username: root
    password: chien1207    # ← Đổi password của bạn
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQLDialect
```

### Auto Import (`financial-etl-pipeline/auto_import_mysql.py`)

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'chien1207',    # ← Đổi password của bạn
    'database': 'investment_db',
}
```

---

## ❓ Xử Lý Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Giải pháp |
| --- | ----------- | --------- |
| `Access denied for user 'root'` | Sai password MySQL | Sửa password trong `application.yml` |
| `release version 5 not supported` | Sai Java version | Thêm `maven.compiler.source=21` trong `pom.xml` |
| `InvalidPathException: Illegal char` | Tên thư mục có tiếng Việt | Đổi tên thư mục sang ASCII |
| `ratiosImported: 0` | Tên file CSV khác | File là `all_ratioss.csv` (thừa chữ s) |
| Backend không kết nối MySQL | MySQL chưa chạy | Khởi động MySQL service |
