# Financial Data ETL Pipeline

Pipeline ETL hoàn chỉnh để thu thập dữ liệu báo cáo tài chính từ thị trường chứng khoán Việt Nam sử dụng thư viện **vnstock**.

## 🚀 Quick Start

### 1. Cài đặt dependencies

```bash
cd financial-etl-pipeline
pip install -r requirements.txt
```

### 2. Chạy pipeline

```bash
# Chạy với 10 mã blue chip mặc định
python main.py

# Chạy với các mã cụ thể
python main.py --symbols VNM FPT VIC HPG

# Chạy với ngành ngân hàng
python main.py --sector banks

# Chế độ nhanh (cho testing)
python main.py --quick --symbols VNM FPT
```

## 📁 Cấu Trúc Project

```
financial-etl-pipeline/
├── config/
│   ├── settings.py      # Cấu hình database, pipeline
│   └── symbols.py       # Danh sách mã cổ phiếu theo ngành
├── extractors/
│   └── vnstock_extractor.py  # Thu thập từ vnstock API
├── transformers/
│   ├── cleaner.py       # Làm sạch dữ liệu
│   └── calculator.py    # Tính toán chỉ số tài chính
├── loaders/
│   └── csv_loader.py    # Xuất ra CSV
├── pipelines/
│   └── financial_pipeline.py  # Pipeline chính
├── main.py              # Entry point
├── requirements.txt
└── .env.example         # Template cấu hình
```

## 📊 Dữ Liệu Thu Thập

Pipeline thu thập các báo cáo tài chính sau cho mỗi mã cổ phiếu:

| Báo cáo | File | Mô tả |
|---------|------|-------|
| Balance Sheet | `balance_sheet.csv` | Bảng cân đối kế toán |
| Income Statement | `income_statement.csv` | Báo cáo kết quả kinh doanh |
| Cash Flow | `cash_flow.csv` | Báo cáo lưu chuyển tiền tệ |
| Ratios | `ratios.csv` | Các chỉ số tài chính |
| Historical Prices | `historical_prices.csv` | Giá lịch sử 1 năm |
| Company Info | `company_info.csv` | Thông tin doanh nghiệp |

## 📈 Chỉ Số Tài Chính

### Chỉ số sinh lời
- Gross Margin (Biên lợi nhuận gộp)
- Operating Margin (Biên lợi nhuận hoạt động)
- Net Margin (Biên lợi nhuận ròng)

### Chỉ số hiệu quả
- ROE (Return on Equity)
- ROA (Return on Assets)

### Chỉ số thanh khoản
- Current Ratio
- Quick Ratio
- Cash Ratio

### Chỉ số đòn bẩy
- Debt to Equity
- Debt to Assets
- Equity Ratio

### Chỉ số định giá
- P/E Ratio
- P/B Ratio
- P/S Ratio

## 💻 Sử Dụng Trong Code

```python
from pipelines.financial_pipeline import FinancialDataPipeline

# Khởi tạo pipeline
pipeline = FinancialDataPipeline(
    symbols=['VNM', 'FPT', 'VIC', 'HPG', 'TCB'],
    output_dir='./data',
    period='quarter',    # 'quarter' hoặc 'year'
    language='vi',       # 'vi' hoặc 'en'
    request_delay=1.5    # Delay giữa các request
)

# Chạy pipeline
result = pipeline.run()

# Xem kết quả
print(result.summary())
print(f"Thành công: {result.success_count}")
print(f"Thất bại: {result.failed_count}")

# Truy cập dữ liệu
for symbol, data in result.data.items():
    print(f"{symbol}: {len(data.balance_sheet)} bản ghi")
```

## 🔧 Cấu Hình

Copy `.env.example` thành `.env` và chỉnh sửa:

```env
# Danh sách mã (hoặc để trống dùng mặc định)
SYMBOLS=VNM,FPT,VIC,HPG,TCB

# Loại báo cáo
PERIOD=quarter

# Thư mục output
OUTPUT_DIR=./output
```

## 📋 Các Nhóm Ngành Có Sẵn

- `banks` - Ngân hàng (VCB, TCB, CTG, BID...)
- `securities` - Chứng khoán (SSI, VCI, HCM...)
- `real_estate` - Bất động sản (VIC, VHM, NVL...)
- `technology` - Công nghệ (FPT, CMG...)
- `blue_chips` - Blue chips (VNM, FPT, VIC, HPG...)
- `vn30` - VN30 Index

```bash
# Xem danh sách đầy đủ
python main.py --list-symbols
```

## 📂 Output

Sau khi chạy, dữ liệu được lưu theo cấu trúc:

```
output/
├── VNM/
│   ├── balance_sheet.csv
│   ├── income_statement.csv
│   ├── cash_flow.csv
│   ├── ratios.csv
│   └── historical_prices.csv
├── FPT/
│   └── ...
├── combined/                    # File tổng hợp tất cả mã
│   ├── all_balance_sheets.csv
│   ├── all_income_statements.csv
│   └── ...
├── logs/
│   └── pipeline_20240101_120000.log
└── pipeline_metadata.json       # Metadata về lần chạy
```

## ⚠️ Lưu Ý

1. **Rate Limiting**: Không chạy quá nhanh, nên để `request_delay >= 1.5` giây
2. **Dữ liệu**: vnstock cung cấp dữ liệu miễn phí, có thể có độ trễ so với thời gian thực
3. **Encoding**: File CSV sử dụng UTF-8 with BOM để mở được tiếng Việt trong Excel

## 📚 Tài Liệu Tham Khảo

- [vnstock Documentation](https://docs.vnstock.site/)
- [Hướng dẫn phân tích cơ bản](./docs/financial-data-etl-pipeline.md)
