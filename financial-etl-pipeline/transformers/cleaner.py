# transformers/cleaner.py
"""
Data Cleaner - Làm sạch và chuẩn hóa dữ liệu tài chính

Module này thực hiện các bước tiền xử lý:
- Xử lý giá trị null/NaN
- Chuẩn hóa tên cột
- Chuyển đổi kiểu dữ liệu
- Loại bỏ dữ liệu trùng lặp
- Validate dữ liệu
"""

import re
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger


class DataCleaner:
    """
    Làm sạch và chuẩn hóa dữ liệu tài chính
    
    Example:
        >>> cleaner = DataCleaner()
        >>> cleaned_df = cleaner.clean(raw_df)
        >>> validated = cleaner.validate(cleaned_df, rules={'revenue': 'positive'})
    """
    
    # Mapping tên cột tiếng Việt -> English (nếu cần)
    COLUMN_MAPPING = {
        'Doanh thu thuần': 'revenue',
        'Lợi nhuận gộp': 'gross_profit', 
        'Lợi nhuận sau thuế': 'net_income',
        'Tổng tài sản': 'total_assets',
        'Vốn chủ sở hữu': 'total_equity',
        'Nợ phải trả': 'total_liabilities',
    }
    
    def __init__(self, 
                 fill_na_strategy: str = 'zero',
                 remove_duplicates: bool = True,
                 normalize_columns: bool = True):
        """
        Khởi tạo DataCleaner
        
        Args:
            fill_na_strategy: Chiến lược xử lý NaN - 'zero', 'mean', 'median', 'ffill', 'drop'
            remove_duplicates: Có xóa dữ liệu trùng không
            normalize_columns: Có chuẩn hóa tên cột không
        """
        self.fill_na_strategy = fill_na_strategy
        self.remove_duplicates = remove_duplicates
        self.normalize_columns = normalize_columns
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Thực hiện full cleaning pipeline
        
        Args:
            df: DataFrame gốc
            
        Returns:
            DataFrame đã được làm sạch
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Clone để không ảnh hưởng dữ liệu gốc
        df = df.copy()
        
        # Pipeline làm sạch
        df = self._clean_column_names(df)
        df = self._convert_data_types(df)
        df = self._handle_missing_values(df)
        
        if self.remove_duplicates:
            df = self._remove_duplicates(df)
        
        df = self._clean_numeric_strings(df)
        
        logger.debug(f"Cleaned DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Chuẩn hóa tên cột
        
        - Loại bỏ khoảng trắng thừa
        - Thay thế ký tự đặc biệt
        - Chuyển về lowercase với underscore
        """
        if not self.normalize_columns:
            return df
            
        def normalize_column(col):
            # Xử lý cột None hoặc không phải string
            if col is None or not isinstance(col, str):
                return str(col) if col is not None else 'unnamed'
            
            # Loại bỏ khoảng trắng đầu cuối
            col = col.strip()
            
            # Thay thế các ký tự đặc biệt bằng underscore
            col = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', '_', col, flags=re.IGNORECASE)
            
            # Thay thế nhiều khoảng trắng/underscore liên tiếp
            col = re.sub(r'[\s_]+', '_', col)
            
            # Loại bỏ underscore đầu cuối
            col = col.strip('_')
            
            # Chuyển lowercase
            col = col.lower()
            
            return col if col else 'unnamed'
        
        df.columns = [normalize_column(c) for c in df.columns]
        return df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Chuyển đổi kiểu dữ liệu cho các cột
        
        - Cột số: float64
        - Cột ngày: datetime
        - Cột text: string
        """
        for col in df.columns:
            # Bỏ qua các cột metadata
            if col.startswith('_'):
                continue
                
            # Thử chuyển thành số
            if df[col].dtype == 'object':
                # Thử chuyển thành numeric
                numeric_series = pd.to_numeric(
                    df[col].astype(str).str.replace(',', '').str.replace(' ', ''),
                    errors='coerce'
                )
                
                # Nếu > 50% giá trị là số, chuyển thành numeric
                if numeric_series.notna().sum() / len(df) > 0.5:
                    df[col] = numeric_series
                else:
                    # Thử chuyển thành datetime
                    try:
                        datetime_series = pd.to_datetime(df[col], errors='coerce')
                        if datetime_series.notna().sum() / len(df) > 0.5:
                            df[col] = datetime_series
                    except:
                        pass
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Xử lý giá trị thiếu theo chiến lược đã chọn
        """
        if self.fill_na_strategy == 'zero':
            # Chỉ fill 0 cho cột số
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
        elif self.fill_na_strategy == 'mean':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            
        elif self.fill_na_strategy == 'median':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            
        elif self.fill_na_strategy == 'ffill':
            df = df.fillna(method='ffill')
            
        elif self.fill_na_strategy == 'drop':
            df = df.dropna()
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Loại bỏ dòng trùng lặp"""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        
        if before > after:
            logger.debug(f"Removed {before - after} duplicate rows")
        
        return df
    
    def _clean_numeric_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Làm sạch các chuỗi số
        - Loại bỏ dấu phẩy ngăn cách hàng nghìn
        - Xử lý dấu thập phân
        - Xử lý số âm trong ngoặc
        """
        for col in df.select_dtypes(include=['object']).columns:
            if col.startswith('_'):
                continue
                
            try:
                # Xử lý số trong ngoặc là số âm: (1,000) -> -1000
                df[col] = df[col].astype(str).apply(self._parse_accounting_number)
            except:
                pass
        
        return df
    
    def _parse_accounting_number(self, value: str) -> str:
        """
        Parse số theo format kế toán
        - (1,234.56) -> -1234.56
        - 1,234.56 -> 1234.56
        """
        if pd.isna(value) or value in ['nan', 'None', '']:
            return value
            
        value = str(value).strip()
        
        # Số trong ngoặc là số âm
        if value.startswith('(') and value.endswith(')'):
            value = '-' + value[1:-1]
        
        # Loại bỏ dấu phẩy
        value = value.replace(',', '')
        
        return value
    
    def validate(self, 
                 df: pd.DataFrame, 
                 rules: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Validate dữ liệu theo các rules
        
        Args:
            df: DataFrame cần validate
            rules: Dictionary {column: rule}
                   Rules: 'positive', 'negative', 'not_null', 'unique'
        
        Returns:
            Dictionary với kết quả validation
        """
        if rules is None:
            rules = {}
        
        results = {
            'is_valid': True,
            'total_rows': len(df),
            'errors': [],
            'warnings': []
        }
        
        for col, rule in rules.items():
            if col not in df.columns:
                results['warnings'].append(f"Column '{col}' not found")
                continue
            
            if rule == 'positive':
                invalid = (df[col] < 0).sum()
                if invalid > 0:
                    results['errors'].append(f"Column '{col}' has {invalid} negative values")
                    results['is_valid'] = False
                    
            elif rule == 'not_null':
                null_count = df[col].isna().sum()
                if null_count > 0:
                    results['errors'].append(f"Column '{col}' has {null_count} null values")
                    results['is_valid'] = False
                    
            elif rule == 'unique':
                duplicates = df[col].duplicated().sum()
                if duplicates > 0:
                    results['warnings'].append(f"Column '{col}' has {duplicates} duplicate values")
        
        return results
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Tạo báo cáo chất lượng dữ liệu
        
        Returns:
            Dictionary chứa các metrics về chất lượng dữ liệu
        """
        if df is None or df.empty:
            return {'error': 'Empty DataFrame'}
        
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'columns': {}
        }
        
        for col in df.columns:
            col_report = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isna().sum()),
                'null_percent': round(df[col].isna().sum() / len(df) * 100, 2),
                'unique_count': int(df[col].nunique()),
            }
            
            # Thêm thống kê cho cột số
            if pd.api.types.is_numeric_dtype(df[col]):
                col_report.update({
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                })
            
            report['columns'][col] = col_report
        
        return report
