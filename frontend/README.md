# Investment Support Frontend

Frontend React cho ứng dụng hỗ trợ đầu tư.

## 🛠️ Tech Stack

- **React 18** + **Vite**
- **TailwindCSS**
- **React Router**
- **React Query**
- **Recharts** (biểu đồ)
- **Lucide React** (icons)

## 🚀 Chạy ứng dụng

### Yêu cầu
- Node.js 18+
- npm hoặc yarn

### Cài đặt và chạy

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

### Truy cập
- **Frontend**: http://localhost:5173

## 📁 Cấu trúc project

```
src/
├── main.jsx              # Entry point
├── App.jsx               # Router config
├── index.css             # Global styles (TailwindCSS)
├── components/
│   └── Layout.jsx        # Main layout with sidebar
├── pages/
│   ├── Dashboard.jsx     # Trang chủ
│   ├── StockList.jsx     # Danh sách cổ phiếu
│   ├── StockDetail.jsx   # Chi tiết cổ phiếu
│   └── Compare.jsx       # So sánh cổ phiếu
└── services/
    └── api.js            # API service
```

## 🔗 Kết nối Backend

Frontend tự động proxy `/api/*` đến `http://localhost:8080` (xem `vite.config.js`).

Đảm bảo backend đang chạy trước khi sử dụng frontend.

## 📱 Pages

| Route | Trang | Mô tả |
|-------|-------|-------|
| `/` | Dashboard | Tổng quan, thống kê |
| `/stocks` | Stock List | Danh sách cổ phiếu |
| `/stocks/:symbol` | Stock Detail | Chi tiết 1 mã |
| `/compare` | Compare | So sánh nhiều mã |
