#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Financial Data ETL Pipeline - Entry Point

Script chính để chạy pipeline thu thập dữ liệu báo cáo tài chính
sử dụng thư viện vnstock.

Usage:
    # Chạy với cấu hình mặc định (10 mã blue chip)
    python main.py
    
    # Chạy với các mã cụ thể
    python main.py --symbols VNM FPT VIC HPG
    
    # Chạy chế độ nhanh (cho testing)
    python main.py --quick --symbols VNM FPT
    
    # Chạy với tất cả ngân hàng
    python main.py --sector banks
    
    # Xem danh sách mã có sẵn
    python main.py --list-symbols

Author: Your Name
Created: 2024
"""

import argparse
import sys
from typing import List

from loguru import logger

# Import pipeline
from pipelines.financial_pipeline import FinancialDataPipeline, create_pipeline
from config.symbols import (
    BLUE_CHIPS, BANKS, SECURITIES, REAL_ESTATE, 
    TECHNOLOGY, VN30, get_symbols_by_sectors,
    fetch_all_symbols_from_exchange, get_symbols_by_exchange
)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Financial Data ETL Pipeline - Thu thập dữ liệu BCTC',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Chạy với 10 mã mặc định
  python main.py --symbols VNM FPT VIC    # Chạy với mã cụ thể
  python main.py --sector banks           # Chạy với ngành ngân hàng
  python main.py --quick                  # Chạy nhanh (testing)
  python main.py --list-symbols           # Liệt kê các mã có sẵn
        """
    )
    
    # Symbols options
    parser.add_argument(
        '--symbols', '-s',
        nargs='+',
        help='Danh sách mã cổ phiếu (VD: VNM FPT VIC)'
    )
    
    parser.add_argument(
        '--sector',
        choices=['banks', 'securities', 'real_estate', 'technology', 
                 'steel', 'retail', 'energy', 'blue_chips', 'vn30'],
        help='Chọn nhóm ngành để thu thập'
    )
    
    parser.add_argument(
        '--exchange',
        choices=['HOSE', 'HNX', 'UPCOM', 'all'],
        help='Lấy mã theo sàn giao dịch (HOSE, HNX, UPCOM, hoặc all)'
    )
    
    parser.add_argument(
        '--fetch-all',
        action='store_true',
        help='Lấy TẤT CẢ mã từ API (1600+ mã, mất nhiều thời gian!)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        default='./output',
        help='Thư mục output (mặc định: ./output)'
    )
    
    parser.add_argument(
        '--period',
        choices=['quarter', 'year'],
        default='quarter',
        help='Loại báo cáo: quarter (quý) hoặc year (năm)'
    )
    
    # Performance options
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Chế độ nhanh với delay thấp (cho testing)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='Delay giữa các request (giây, mặc định: 1.5)'
    )
    
    # Utility options
    parser.add_argument(
        '--list-symbols',
        action='store_true',
        help='Liệt kê các mã cổ phiếu có sẵn theo ngành'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='Hiển thị log chi tiết'
    )
    
    return parser.parse_args()


def get_symbols_from_args(args) -> List[str]:
    """Lấy danh sách symbols từ arguments"""
    
    # Nếu chỉ định symbols cụ thể
    if args.symbols:
        return [s.upper() for s in args.symbols]
    
    # Nếu muốn lấy TẤT CẢ từ API
    if args.fetch_all:
        print("🔄 Đang lấy tất cả mã từ API vnstock...")
        exchange = args.exchange if args.exchange else 'all'
        return fetch_all_symbols_from_exchange(exchange)
    
    # Nếu chọn theo sàn
    if args.exchange:
        print(f"📊 Lấy mã từ sàn {args.exchange}...")
        return get_symbols_by_exchange(args.exchange)
    
    # Nếu chọn sector
    if args.sector:
        sector_mapping = {
            'banks': BANKS,
            'securities': SECURITIES,
            'real_estate': REAL_ESTATE,
            'technology': TECHNOLOGY,
            'blue_chips': BLUE_CHIPS,
            'vn30': VN30,
        }
        return sector_mapping.get(args.sector, BLUE_CHIPS)
    
    # Mặc định: 10 mã blue chip
    return BLUE_CHIPS[:10]


def list_available_symbols():
    """In ra danh sách các mã cổ phiếu có sẵn"""
    print("\n" + "=" * 60)
    print("📊 DANH SÁCH MÃ CỔ PHIẾU CÓ SẴN")
    print("=" * 60)
    
    sectors = {
        'Blue Chips': BLUE_CHIPS,
        'Ngân hàng (banks)': BANKS,
        'Chứng khoán (securities)': SECURITIES,
        'Bất động sản (real_estate)': REAL_ESTATE,
        'Công nghệ (technology)': TECHNOLOGY,
        'VN30': VN30,
    }
    
    for name, symbols in sectors.items():
        print(f"\n🏷️  {name}:")
        print(f"   {', '.join(symbols)}")
    
    print("\n" + "=" * 60)
    print("💡 Sử dụng: python main.py --sector banks")
    print("   hoặc:   python main.py --symbols VNM FPT VIC")
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Nếu chỉ muốn liệt kê symbols
    if args.list_symbols:
        list_available_symbols()
        return 0
    
    # Lấy danh sách symbols
    symbols = get_symbols_from_args(args)
    
    # Hiển thị thông tin
    print("\n" + "=" * 60)
    print("🚀 FINANCIAL DATA ETL PIPELINE")
    print("=" * 60)
    print(f"📋 Symbols: {len(symbols)} mã")
    print(f"   {', '.join(symbols[:10])}" + ("..." if len(symbols) > 10 else ""))
    print(f"📁 Output:  {args.output}")
    print(f"📅 Period:  {args.period}")
    print(f"⏱️  Delay:   {0.5 if args.quick else args.delay}s")
    print("=" * 60 + "\n")
    
    # Xác nhận trước khi chạy
    if not args.quick and len(symbols) > 5:
        estimated_time = len(symbols) * 8  # ~8 giây mỗi mã
        print(f"⏳ Ước tính thời gian: ~{estimated_time // 60} phút {estimated_time % 60} giây")
        
        try:
            response = input("Bạn có muốn tiếp tục? (y/n): ")
            if response.lower() not in ['y', 'yes', '']:
                print("❌ Đã hủy.")
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Đã hủy.")
            return 0
    
    # Khởi tạo và chạy pipeline
    try:
        pipeline = FinancialDataPipeline(
            symbols=symbols,
            output_dir=args.output,
            source='VCI',
            period=args.period,
            language='vi',
            request_delay=0.5 if args.quick else args.delay,
            verbose=args.verbose
        )
        
        result = pipeline.run()
        
        # Hiển thị kết quả
        print(result.summary())
        
        if result.success_count > 0:
            print(f"📂 Dữ liệu đã lưu tại: {args.output}")
            print(f"   - Thư mục theo mã: {args.output}/<SYMBOL>/")
            print(f"   - File tổng hợp:   {args.output}/combined/")
        
        if result.errors:
            print("\n⚠️  Các mã bị lỗi:")
            for symbol, error in result.errors.items():
                print(f"   - {symbol}: {error}")
        
        return 0 if result.failed_count == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\n❌ Pipeline bị dừng bởi người dùng.")
        return 1
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        print(f"\n❌ Lỗi: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
