# loaders/csv_loader.py
"""
CSV Loader - Xuất dữ liệu ra file CSV

Module này cung cấp các chức năng:
- Lưu DataFrame ra CSV với encoding UTF-8
- Tổ chức thư mục theo symbol/report_type
- Hỗ trợ append hoặc overwrite
- Tạo file tổng hợp (combined)
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import pandas as pd
from loguru import logger

from extractors.vnstock_extractor import ExtractedData


class CSVLoader:
    """
    Xuất dữ liệu tài chính ra file CSV
    
    Cấu trúc thư mục output:
    output/
    ├── VNM/
    │   ├── balance_sheet.csv
    │   ├── income_statement.csv
    │   ├── cash_flow.csv
    │   └── ratios.csv
    ├── FPT/
    │   └── ...
    └── combined/
        ├── all_balance_sheets.csv
        ├── all_income_statements.csv
        └── ...
    
    Example:
        >>> loader = CSVLoader('./output')
        >>> loader.save(extracted_data)
        >>> loader.save_combined(all_data_dict)
    """
    
    def __init__(
        self, 
        output_dir: str = './output',
        encoding: str = 'utf-8-sig',  # UTF-8 with BOM for Excel compatibility
        create_combined: bool = True
    ):
        """
        Khởi tạo CSV Loader
        
        Args:
            output_dir: Thư mục gốc để lưu output
            encoding: Encoding cho file CSV (utf-8-sig để mở được tiếng Việt trong Excel)
            create_combined: Có tạo file tổng hợp không
        """
        self.output_dir = Path(output_dir)
        self.encoding = encoding
        self.create_combined = create_combined
        
        # Tạo thư mục nếu chưa có
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tracking
        self.saved_files: List[str] = []
        
        logger.info(f"CSVLoader initialized: output_dir={output_dir}")
    
    def save(self, data: ExtractedData) -> Dict[str, str]:
        """
        Lưu dữ liệu của một mã cổ phiếu ra CSV
        
        Args:
            data: ExtractedData chứa các DataFrame
            
        Returns:
            Dict với {report_type: file_path}
        """
        if not data or not data.symbol:
            logger.warning("No data to save")
            return {}
        
        symbol = data.symbol
        symbol_dir = self.output_dir / symbol
        symbol_dir.mkdir(exist_ok=True)
        
        saved_paths = {}
        
        # Mapping tên report -> DataFrame
        reports = {
            'company_info': data.company_info,
            'balance_sheet': data.balance_sheet,
            'income_statement': data.income_statement,
            'cash_flow': data.cash_flow,
            'ratios': data.ratios,
            'historical_prices': data.historical_prices,
        }
        
        for report_name, df in reports.items():
            if df is not None and not df.empty:
                file_path = symbol_dir / f'{report_name}.csv'
                self._save_dataframe(df, file_path)
                saved_paths[report_name] = str(file_path)
                self.saved_files.append(str(file_path))
        
        logger.info(f"💾 Saved {len(saved_paths)} files for {symbol}")
        return saved_paths
    
    def save_multiple(self, data_dict: Dict[str, ExtractedData]) -> Dict[str, Dict[str, str]]:
        """
        Lưu dữ liệu của nhiều mã cổ phiếu
        
        Args:
            data_dict: Dictionary {symbol: ExtractedData}
            
        Returns:
            Dictionary {symbol: {report_type: file_path}}
        """
        all_paths = {}
        
        for symbol, data in data_dict.items():
            all_paths[symbol] = self.save(data)
        
        # Tạo file tổng hợp nếu được bật
        if self.create_combined:
            self.save_combined(data_dict)
        
        return all_paths
    
    def save_combined(self, data_dict: Dict[str, ExtractedData]):
        """
        Tạo các file CSV tổng hợp từ tất cả mã cổ phiếu
        
        Mỗi file combined chứa dữ liệu của tất cả symbols, 
        giúp dễ phân tích so sánh.
        """
        combined_dir = self.output_dir / 'combined'
        combined_dir.mkdir(exist_ok=True)
        
        # Gộp từng loại report
        report_types = [
            'balance_sheet', 
            'income_statement', 
            'cash_flow', 
            'ratios', 
            'historical_prices'
        ]
        
        for report_type in report_types:
            dfs = []
            
            for symbol, data in data_dict.items():
                df = getattr(data, report_type, None)
                if df is not None and not df.empty:
                    df = df.copy()
                    df['symbol'] = symbol  # Đảm bảo có cột symbol
                    dfs.append(df)
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                file_path = combined_dir / f'all_{report_type}s.csv'
                self._save_dataframe(combined_df, file_path)
                logger.info(f"📊 Combined {report_type}: {len(combined_df)} rows")
    
    def _save_dataframe(self, df: pd.DataFrame, file_path: Path):
        """
        Lưu DataFrame ra CSV với các options chuẩn
        """
        try:
            df.to_csv(
                file_path,
                index=False,
                encoding=self.encoding,
                date_format='%Y-%m-%d',
                float_format='%.2f'  # 2 decimal places cho số
            )
            logger.debug(f"Saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            raise
    
    def load(self, symbol: str, report_type: str) -> Optional[pd.DataFrame]:
        """
        Load lại dữ liệu từ CSV
        
        Args:
            symbol: Mã cổ phiếu
            report_type: Loại báo cáo (balance_sheet, income_statement, ...)
            
        Returns:
            DataFrame hoặc None nếu không tìm thấy
        """
        file_path = self.output_dir / symbol / f'{report_type}.csv'
        
        if file_path.exists():
            return pd.read_csv(file_path, encoding=self.encoding)
        
        logger.warning(f"File not found: {file_path}")
        return None
    
    def get_saved_symbols(self) -> List[str]:
        """Lấy danh sách các symbols đã lưu"""
        symbols = []
        for item in self.output_dir.iterdir():
            if item.is_dir() and item.name != 'combined':
                symbols.append(item.name)
        return sorted(symbols)
    
    def get_summary(self) -> Dict:
        """Tạo summary về dữ liệu đã lưu"""
        summary = {
            'output_dir': str(self.output_dir),
            'total_files': len(self.saved_files),
            'symbols': self.get_saved_symbols(),
            'last_updated': datetime.now().isoformat()
        }
        return summary


class CSVExporter:
    """
    Utility class để xuất báo cáo phân tích ra CSV
    """
    
    @staticmethod
    def export_ratio_comparison(
        data_dict: Dict[str, ExtractedData],
        output_path: str,
        ratios: List[str] = None
    ):
        """
        Xuất bảng so sánh chỉ số giữa các cổ phiếu
        
        Args:
            data_dict: Dictionary {symbol: ExtractedData}
            output_path: Đường dẫn file output
            ratios: Danh sách chỉ số cần so sánh
        """
        if ratios is None:
            ratios = ['roe', 'roa', 'current_ratio', 'debt_to_equity', 'pe_ratio', 'pb_ratio']
        
        rows = []
        
        for symbol, data in data_dict.items():
            if data.ratios is not None and not data.ratios.empty:
                row = {'symbol': symbol}
                latest = data.ratios.iloc[0]
                
                for ratio in ratios:
                    if ratio in latest:
                        row[ratio] = latest[ratio]
                
                rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"Exported ratio comparison to {output_path}")
    
    @staticmethod
    def export_financial_summary(
        data: ExtractedData,
        output_path: str
    ):
        """
        Xuất bảng tóm tắt tài chính cho một cổ phiếu
        """
        summary_rows = []
        
        # Lấy các chỉ tiêu quan trọng từ mỗi báo cáo
        if data.income_statement is not None and not data.income_statement.empty:
            income = data.income_statement.iloc[0]
            summary_rows.extend([
                {'Metric': 'Revenue', 'Value': income.get('revenue', 'N/A')},
                {'Metric': 'Net Income', 'Value': income.get('net_income', 'N/A')},
                {'Metric': 'EPS', 'Value': income.get('eps', 'N/A')},
            ])
        
        if data.balance_sheet is not None and not data.balance_sheet.empty:
            balance = data.balance_sheet.iloc[0]
            summary_rows.extend([
                {'Metric': 'Total Assets', 'Value': balance.get('total_assets', 'N/A')},
                {'Metric': 'Total Equity', 'Value': balance.get('total_equity', 'N/A')},
            ])
        
        if summary_rows:
            df = pd.DataFrame(summary_rows)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"Exported financial summary to {output_path}")
