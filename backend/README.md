# Investment Support API - Backend

Backend API cho ứng dụng hỗ trợ đầu tư, cung cấp dữ liệu báo cáo tài chính và chỉ số phân tích cơ bản.

## 🛠️ Tech Stack

- **Java 17**
- **Spring Boot 3.2**
- **Spring Data JPA**
- **H2 Database** (development) / **PostgreSQL** (production)
- **Lombok**
- **OpenCSV**

## 🚀 Chạy ứng dụng

### Yêu cầu
- Java 17+ (JDK)
- Maven 3.8+

### Chạy development

```bash
# Di chuyển vào thư mục backend
cd backend

# Chạy với Maven
./mvnw spring-boot:run

# Hoặc trên Windows
mvnw.cmd spring-boot:run
```

### Truy cập

- **API**: http://localhost:8080/api
- **H2 Console**: http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:file:./data/investmentdb`
  - Username: `sa`
  - Password: (để trống)

## 📊 Import dữ liệu

Sau khi backend chạy, import dữ liệu từ ETL pipeline:

```bash
# Import dữ liệu từ CSV
curl -X POST "http://localhost:8080/api/admin/import?path=../financial-etl-pipeline/output"
```

## 🔌 API Endpoints

### Stocks
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/stocks` | Danh sách tất cả cổ phiếu |
| GET | `/api/stocks/{symbol}` | Chi tiết 1 cổ phiếu |
| GET | `/api/stocks/search?q=keyword` | Tìm kiếm |
| GET | `/api/stocks/industries` | Danh sách ngành |

### Financial Data
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/stocks/{symbol}/balance-sheet` | Bảng cân đối kế toán |
| GET | `/api/stocks/{symbol}/income-statement` | Báo cáo KQKD |
| GET | `/api/stocks/{symbol}/ratios` | Chỉ số tài chính |
| GET | `/api/stocks/{symbol}/overview` | Tổng quan |

### Comparison
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/stocks/compare?symbols=VNM,FPT` | So sánh nhiều mã |

### Admin
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/admin/import?path=...` | Import CSV |
| GET | `/api/admin/health` | Health check |

## 📁 Cấu trúc project

```
src/main/java/com/investment/
├── InvestmentApplication.java     # Main class
├── config/
│   └── WebConfig.java             # CORS config
├── controller/
│   ├── StockController.java       # Stock API
│   └── AdminController.java       # Admin API
├── entity/
│   ├── Stock.java
│   ├── BalanceSheet.java
│   ├── IncomeStatement.java
│   └── FinancialRatio.java
├── repository/
│   ├── StockRepository.java
│   ├── BalanceSheetRepository.java
│   ├── IncomeStatementRepository.java
│   └── FinancialRatioRepository.java
└── service/
    ├── StockService.java
    └── CsvImportService.java
```

## 🔄 Chuyển sang PostgreSQL

Khi deploy production, sửa `application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/investment_db
    driver-class-name: org.postgresql.Driver
    username: postgres
    password: your_password
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```
