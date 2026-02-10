"""
Auto Import: ETL → MySQL (không cần backend)

Script này chạy độc lập, không cần Spring Boot backend:
1. Chạy ETL pipeline lấy dữ liệu từ vnstock
2. Đọc CSV output  
3. Import trực tiếp vào MySQL

Sử dụng:
    python auto_import_mysql.py
    python auto_import_mysql.py --symbols VNM FPT VIC
    python auto_import_mysql.py --sector vn30
"""

import os
import sys
import csv
import subprocess
import mysql.connector
from datetime import datetime
from pathlib import Path

# ===== CẤU HÌNH MySQL =====
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'chien1207',
    'database': 'investment_db',
    'charset': 'utf8mb4'
}

OUTPUT_DIR = './output'
COMBINED_DIR = './output/combined'

def log(msg):
    """Log với timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def run_etl(args):
    """Bước 1: Chạy ETL pipeline"""
    log("🚀 Bước 1: Chạy ETL pipeline...")
    
    cmd = [sys.executable, 'main.py'] + args
    log(f"   Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        log("❌ ETL pipeline thất bại!")
        return False
    
    log("✅ ETL pipeline hoàn thành!")
    return True

def get_connection():
    """Kết nối MySQL"""
    return mysql.connector.connect(**MYSQL_CONFIG)

def import_stocks(conn):
    """Import thông tin cổ phiếu từ các thư mục trong output"""
    log("📥 Import stocks...")
    cursor = conn.cursor()
    
    output_path = Path(OUTPUT_DIR)
    count = 0
    
    for symbol_dir in output_path.iterdir():
        if symbol_dir.is_dir() and symbol_dir.name not in ('combined', 'logs'):
            symbol = symbol_dir.name.upper()
            cursor.execute("""
                INSERT INTO stocks (symbol, company_name, exchange, created_at) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE updated_at = %s
            """, (symbol, symbol, 'HOSE', datetime.now().date(), datetime.now().date()))
            count += 1
    
    conn.commit()
    cursor.close()
    log(f"   ✅ {count} stocks imported/updated")
    return count

def import_balance_sheets(conn):
    """Import bảng cân đối kế toán"""
    csv_path = os.path.join(COMBINED_DIR, 'all_balance_sheets.csv')
    if not os.path.exists(csv_path):
        log("   ⚠️ Không tìm thấy all_balance_sheets.csv")
        return 0
    
    log("📥 Import balance sheets...")
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ
    cursor.execute("TRUNCATE TABLE balance_sheets")
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                symbol = row.get('cp', '').strip()
                year = row.get('năm', '').strip()
                period = row.get('kỳ', '').strip()
                
                if not symbol or not year:
                    continue
                
                year_int = int(float(year))
                period_int = int(float(period)) if period else 4
                period_str = f"Q{period_int}"
                
                month_map = {1: 3, 2: 6, 3: 9, 4: 12}
                month = month_map.get(period_int, 12)
                report_date = f"{year_int}-{month:02d}-01"
                
                def safe_decimal(val):
                    if val and val.strip():
                        try:
                            return float(val.strip().replace(',', ''))
                        except:
                            return None
                    return None
                
                cursor.execute("""
                    INSERT INTO balance_sheets 
                    (symbol, year_report, period, report_date, created_at,
                     total_assets, total_liabilities, total_equity,
                     cash, inventory, fixed_assets,
                     current_assets, non_current_assets,
                     current_liabilities, non_current_liabilities,
                     short_term_debt, long_term_debt,
                     short_term_investments, long_term_investments,
                     receivables, retained_earnings, charter_capital)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, year_int, period_str, report_date, datetime.now().date(),
                    safe_decimal(row.get('tổng_cộng_tài_sản_đồng')),
                    safe_decimal(row.get('nợ_phải_trả_đồng')),
                    safe_decimal(row.get('vốn_chủ_sở_hữu_đồng')),
                    safe_decimal(row.get('tiền_và_tương_đương_tiền_đồng')),
                    safe_decimal(row.get('hàng_tồn_kho_ròng_đồng')),
                    safe_decimal(row.get('tài_sản_cố_định_đồng')),
                    safe_decimal(row.get('tài_sản_ngắn_hạn_đồng')),
                    safe_decimal(row.get('tài_sản_dài_hạn_đồng')),
                    safe_decimal(row.get('nợ_ngắn_hạn_đồng')),
                    safe_decimal(row.get('nợ_dài_hạn_đồng')),
                    safe_decimal(row.get('vay_và_nợ_thuê_tài_chính_ngắn_hạn_đồng')),
                    safe_decimal(row.get('vay_và_nợ_thuê_tài_chính_dài_hạn_đồng')),
                    safe_decimal(row.get('giá_trị_thuần_đầu_tư_ngắn_hạn_đồng')),
                    safe_decimal(row.get('đầu_tư_dài_hạn_đồng')),
                    safe_decimal(row.get('các_khoản_phải_thu_ngắn_hạn_đồng')),
                    safe_decimal(row.get('lãi_chưa_phân_phối_đồng')),
                    safe_decimal(row.get('vốn_góp_của_chủ_sở_hữu_đồng')),
                ))
                count += 1
            except Exception as e:
                pass  # Skip invalid rows
    
    conn.commit()
    cursor.close()
    log(f"   ✅ {count} balance sheets imported")
    return count

def import_income_statements(conn):
    """Import báo cáo kết quả kinh doanh"""
    csv_path = os.path.join(COMBINED_DIR, 'all_income_statements.csv')
    if not os.path.exists(csv_path):
        log("   ⚠️ Không tìm thấy all_income_statements.csv")
        return 0
    
    log("📥 Import income statements...")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE income_statements")
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                symbol = row.get('cp', '').strip()
                year = row.get('năm', '').strip()
                period = row.get('kỳ', '').strip()
                
                if not symbol or not year:
                    continue
                
                year_int = int(float(year))
                period_int = int(float(period)) if period else 4
                period_str = f"Q{period_int}"
                
                month_map = {1: 3, 2: 6, 3: 9, 4: 12}
                month = month_map.get(period_int, 12)
                report_date = f"{year_int}-{month:02d}-01"
                
                def safe_decimal(val):
                    if val and val.strip():
                        try:
                            return float(val.strip().replace(',', ''))
                        except:
                            return None
                    return None
                
                cursor.execute("""
                    INSERT INTO income_statements
                    (symbol, year_report, period, report_date, created_at,
                     revenue, cost_of_goods_sold, gross_profit,
                     operating_profit, profit_before_tax, net_income,
                     net_income_parent, financial_income, financial_expenses,
                     interest_expenses, selling_expenses, admin_expenses, income_tax)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, year_int, period_str, report_date, datetime.now().date(),
                    safe_decimal(row.get('doanh_thu_đồng')),
                    safe_decimal(row.get('giá_vốn_hàng_bán')),
                    safe_decimal(row.get('lãi_gộp')),
                    safe_decimal(row.get('lãi_lỗ_từ_hoạt_động_kinh_doanh')),
                    safe_decimal(row.get('ln_trước_thuế')),
                    safe_decimal(row.get('lợi_nhuận_thuần')),
                    safe_decimal(row.get('lợi_nhuận_sau_thuế_của_cổ_đông_công_ty_mẹ_đồng')),
                    safe_decimal(row.get('thu_nhập_tài_chính')),
                    safe_decimal(row.get('chi_phí_tài_chính')),
                    safe_decimal(row.get('chi_phí_tiền_lãi_vay')),
                    safe_decimal(row.get('chi_phí_bán_hàng')),
                    safe_decimal(row.get('chi_phí_quản_lý_dn')),
                    safe_decimal(row.get('chi_phí_thuế_tndn_hiện_hành')),
                ))
                count += 1
            except Exception as e:
                pass
    
    conn.commit()
    cursor.close()
    log(f"   ✅ {count} income statements imported")
    return count

def import_ratios(conn):
    """Import chỉ số tài chính"""
    # File có thể là all_ratioss.csv hoặc all_ratios.csv
    csv_path = os.path.join(COMBINED_DIR, 'all_ratioss.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(COMBINED_DIR, 'all_ratios.csv')
    if not os.path.exists(csv_path):
        log("   ⚠️ Không tìm thấy file ratios CSV")
        return 0
    
    log("📥 Import financial ratios...")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE financial_ratios")
    
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        if len(rows) < 3:
            return 0
        
        # Row 0 = category headers, Row 1 = column names, Row 2+ = data
        headers = [h.strip() for h in rows[1]]
        header_map = {h: i for i, h in enumerate(headers)}
        
        def get_val(row, col_name):
            idx = header_map.get(col_name)
            if idx is not None and idx < len(row) and row[idx].strip():
                try:
                    return float(row[idx].strip().replace(',', ''))
                except:
                    return None
            return None
        
        for i in range(2, len(rows)):
            row = rows[i]
            if len(row) < 3:
                continue
            try:
                symbol = row[0].strip()  # CP
                if not symbol:
                    continue
                
                year_val = row[1].strip()  # Năm
                period_val = row[2].strip()  # Kỳ
                
                year_int = int(float(year_val)) if year_val else None
                period_int = int(float(period_val)) if period_val else None
                period_str = f"Q{period_int}" if period_int else None
                
                if year_int is None:
                    continue
                
                month_map = {1: 3, 2: 6, 3: 9, 4: 12}
                month = month_map.get(period_int, 12)
                report_date = f"{year_int}-{month:02d}-01"
                
                cursor.execute("""
                    INSERT INTO financial_ratios
                    (symbol, year_report, period, report_date, created_at,
                     debt_to_equity, gross_margin, net_margin,
                     roe, roa, asset_turnover, inventory_turnover,
                     current_ratio, quick_ratio, cash_ratio,
                     dividend_yield, pe, pb, ps, interest_coverage)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, year_int, period_str, report_date, datetime.now().date(),
                    get_val(row, 'Nợ/VCSH'),
                    get_val(row, 'Biên lợi nhuận gộp (%)'),
                    get_val(row, 'Biên lợi nhuận ròng (%)'),
                    get_val(row, 'ROE (%)'),
                    get_val(row, 'ROA (%)'),
                    get_val(row, 'Vòng quay tài sản'),
                    get_val(row, 'Vòng quay hàng tồn kho'),
                    get_val(row, 'Chỉ số thanh toán hiện thời'),
                    get_val(row, 'Chỉ số thanh toán nhanh'),
                    get_val(row, 'Chỉ số thanh toán tiền mặt'),
                    get_val(row, 'Tỷ suất cổ tức (%)'),
                    get_val(row, 'P/E'),
                    get_val(row, 'P/B'),
                    get_val(row, 'P/S'),
                    get_val(row, 'Khả năng chi trả lãi vay'),
                ))
                count += 1
            except Exception as e:
                pass
    
    conn.commit()
    cursor.close()
    log(f"   ✅ {count} financial ratios imported")
    return count

def main():
    log("=" * 60)
    log("🔄 AUTO UPDATE: ETL + MySQL Import")
    log("=" * 60)
    
    # Lấy arguments cho ETL
    etl_args = sys.argv[1:] if len(sys.argv) > 1 else ['--symbols', 'VNM', 'FPT', 'VIC', 'HPG']
    
    # Bước 1: Chạy ETL
    if not run_etl(etl_args):
        log("❌ ETL thất bại, dừng lại!")
        sys.exit(1)
    
    # Bước 2: Import vào MySQL
    log("🚀 Bước 2: Import dữ liệu vào MySQL...")
    
    try:
        conn = get_connection()
        log("   ✅ Kết nối MySQL thành công!")
        
        stocks = import_stocks(conn)
        bs = import_balance_sheets(conn)
        is_count = import_income_statements(conn)
        ratios = import_ratios(conn)
        
        conn.close()
        
        log("=" * 60)
        log("🎉 HOÀN THÀNH!")
        log(f"   Stocks:            {stocks}")
        log(f"   Balance Sheets:    {bs}")
        log(f"   Income Statements: {is_count}")
        log(f"   Financial Ratios:  {ratios}")
        log("=" * 60)
        
    except mysql.connector.Error as e:
        log(f"❌ Lỗi MySQL: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
