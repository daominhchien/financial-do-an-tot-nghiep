# extractors/vnstock_extractor.py
"""
VNStock Extractor - Thu thập dữ liệu báo cáo tài chính từ vnstock

Module này sử dụng thư viện vnstock để lấy:
- Bảng cân đối kế toán (Balance Sheet)
- Báo cáo kết quả kinh doanh (Income Statement)  
- Báo cáo lưu chuyển tiền tệ (Cash Flow)
- Các chỉ số tài chính (Financial Ratios)
- Thông tin doanh nghiệp (Company Info)
- Giá lịch sử (Historical Prices)
"""

import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd
from loguru import logger

try:
    from vnstock import Vnstock
except ImportError:
    raise ImportError("Vui lòng cài đặt vnstock: pip install vnstock")


@dataclass
class ExtractedData:
    """
    Container chứa tất cả dữ liệu đã extract cho một mã cổ phiếu
    
    Attributes:
        symbol: Mã cổ phiếu
        company_info: Thông tin doanh nghiệp
        balance_sheet: Bảng cân đối kế toán
        income_statement: Báo cáo kết quả kinh doanh
        cash_flow: Báo cáo lưu chuyển tiền tệ
        ratios: Các chỉ số tài chính
        historical_prices: Giá lịch sử
        extracted_at: Thời điểm extract
    """
    symbol: str
    company_info: Optional[pd.DataFrame] = None
    balance_sheet: Optional[pd.DataFrame] = None
    income_statement: Optional[pd.DataFrame] = None
    cash_flow: Optional[pd.DataFrame] = None
    ratios: Optional[pd.DataFrame] = None
    historical_prices: Optional[pd.DataFrame] = None
    extracted_at: datetime = None
    
    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now()
    
    def to_dict(self) -> Dict[str, pd.DataFrame]:
        """Chuyển đổi thành dictionary của DataFrames"""
        return {
            'company_info': self.company_info,
            'balance_sheet': self.balance_sheet,
            'income_statement': self.income_statement,
            'cash_flow': self.cash_flow,
            'ratios': self.ratios,
            'historical_prices': self.historical_prices,
        }
    
    def is_valid(self) -> bool:
        """Kiểm tra dữ liệu có hợp lệ không"""
        # Phải có ít nhất balance_sheet hoặc income_statement
        has_balance = self.balance_sheet is not None and not self.balance_sheet.empty
        has_income = self.income_statement is not None and not self.income_statement.empty
        return has_balance or has_income


class VNStockExtractor:
    """
    Extractor sử dụng thư viện vnstock để thu thập dữ liệu tài chính
    
    Attributes:
        source: Nguồn dữ liệu ('VCI', 'TCBS', 'SSI')
        period: Loại báo cáo ('quarter' hoặc 'year')
        language: Ngôn ngữ ('vi' hoặc 'en')
        request_delay: Delay giữa các request (giây)
    
    Example:
        >>> extractor = VNStockExtractor(source='VCI', period='quarter')
        >>> data = extractor.extract('VNM')
        >>> print(data.balance_sheet.head())
    """
    
    def __init__(
        self,
        source: str = 'VCI',
        period: str = 'quarter',
        language: str = 'vi',
        request_delay: float = 1.0
    ):
        """
        Khởi tạo VNStock Extractor
        
        Args:
            source: Nguồn dữ liệu - 'VCI' (khuyến nghị), 'TCBS', 'SSI'
            period: Loại báo cáo - 'quarter' (quý) hoặc 'year' (năm)
            language: Ngôn ngữ trả về - 'vi' (Tiếng Việt) hoặc 'en' (English)
            request_delay: Thời gian chờ giữa các request để tránh rate limit
        """
        self.source = source
        self.period = period
        self.language = language
        self.request_delay = request_delay
        
        # Khởi tạo vnstock
        self._vnstock = Vnstock()
        
        logger.info(f"VNStockExtractor initialized: source={source}, period={period}, lang={language}")
    
    def extract(self, symbol: str, max_retries: int = 3) -> ExtractedData:
        """
        Thu thập toàn bộ dữ liệu tài chính cho một mã cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu (VD: 'VNM', 'FPT', 'VIC')
            max_retries: Số lần thử lại khi bị rate limit
        
        Returns:
            ExtractedData chứa tất cả báo cáo tài chính
        
        Raises:
            Exception: Khi không thể kết nối hoặc lấy dữ liệu
        """
        logger.info(f"📥 Extracting data for {symbol}...")
        
        result = ExtractedData(symbol=symbol)
        
        for attempt in range(max_retries):
            try:
                # Khởi tạo stock object cho mã cụ thể
                stock = self._vnstock.stock(symbol=symbol, source=self.source)
                
                # 1. Lấy thông tin công ty
                result.company_info = self._extract_company_info(stock)
                time.sleep(self.request_delay)
                
                # 2. Lấy bảng cân đối kế toán
                result.balance_sheet = self._extract_balance_sheet(stock)
                time.sleep(self.request_delay)
                
                # 3. Lấy báo cáo KQKD
                result.income_statement = self._extract_income_statement(stock)
                time.sleep(self.request_delay)
                
                # 4. Lấy báo cáo lưu chuyển tiền tệ
                result.cash_flow = self._extract_cash_flow(stock)
                time.sleep(self.request_delay)
                
                # 5. Lấy các chỉ số tài chính
                result.ratios = self._extract_ratios(stock)
                time.sleep(self.request_delay)
                
                # 6. Lấy giá lịch sử (1 năm gần nhất)
                result.historical_prices = self._extract_historical_prices(stock)
                
                # Thêm metadata vào mỗi DataFrame
                self._add_metadata(result, symbol)
                
                logger.success(f"✅ Successfully extracted data for {symbol}")
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Kiểm tra nếu là rate limit error
                if 'rate limit' in error_msg or 'limit exceeded' in error_msg or '429' in error_msg:
                    wait_time = (attempt + 1) * 15  # 15s, 30s, 45s
                    logger.warning(f"⏳ Rate limit! Đợi {wait_time}s rồi thử lại... (lần {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Error extracting {symbol}: {str(e)}")
                    raise
        
        # Nếu hết retry
        logger.error(f"❌ Failed after {max_retries} retries for {symbol}")
        return result
    
    def _extract_company_info(self, stock) -> Optional[pd.DataFrame]:
        """Lấy thông tin doanh nghiệp"""
        try:
            # Lấy thông tin tổng quan
            overview = stock.company.overview()
            if overview is not None:
                return overview
        except Exception as e:
            logger.warning(f"Could not extract company info: {e}")
        return None
    
    def _extract_balance_sheet(self, stock) -> Optional[pd.DataFrame]:
        """
        Lấy bảng cân đối kế toán
        
        Các chỉ tiêu chính:
        - Tài sản ngắn hạn / Tài sản dài hạn
        - Tiền và tương đương tiền
        - Hàng tồn kho
        - Phải thu
        - Nợ ngắn hạn / Nợ dài hạn
        - Vốn chủ sở hữu
        """
        try:
            df = stock.finance.balance_sheet(
                period=self.period,
                lang=self.language
            )
            if df is not None and not df.empty:
                logger.debug(f"Balance sheet: {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"Could not extract balance sheet: {e}")
        return None
    
    def _extract_income_statement(self, stock) -> Optional[pd.DataFrame]:
        """
        Lấy báo cáo kết quả kinh doanh
        
        Các chỉ tiêu chính:
        - Doanh thu thuần
        - Giá vốn hàng bán
        - Lợi nhuận gộp
        - Chi phí bán hàng, quản lý
        - Lợi nhuận từ HĐKD
        - Lợi nhuận trước/sau thuế
        - EPS
        """
        try:
            df = stock.finance.income_statement(
                period=self.period,
                lang=self.language
            )
            if df is not None and not df.empty:
                logger.debug(f"Income statement: {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"Could not extract income statement: {e}")
        return None
    
    def _extract_cash_flow(self, stock) -> Optional[pd.DataFrame]:
        """
        Lấy báo cáo lưu chuyển tiền tệ
        
        Các dòng tiền:
        - Dòng tiền từ hoạt động kinh doanh
        - Dòng tiền từ hoạt động đầu tư
        - Dòng tiền từ hoạt động tài chính
        - Tiền thuần trong kỳ
        """
        try:
            df = stock.finance.cash_flow(
                period=self.period,
                lang=self.language
            )
            if df is not None and not df.empty:
                logger.debug(f"Cash flow: {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"Could not extract cash flow: {e}")
        return None
    
    def _extract_ratios(self, stock) -> Optional[pd.DataFrame]:
        """
        Lấy các chỉ số tài chính
        
        Các nhóm chỉ số:
        - Định giá: P/E, P/B, P/S, EV/EBITDA
        - Sinh lời: ROE, ROA, ROS, Biên lợi nhuận
        - Thanh khoản: Current ratio, Quick ratio
        - Đòn bẩy: D/E, D/A
        """
        try:
            df = stock.finance.ratio(
                period=self.period,
                lang=self.language
            )
            if df is not None and not df.empty:
                logger.debug(f"Ratios: {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"Could not extract ratios: {e}")
        return None
    
    def _extract_historical_prices(self, stock, days: int = 365) -> Optional[pd.DataFrame]:
        """
        Lấy giá lịch sử
        
        Args:
            days: Số ngày lịch sử cần lấy (mặc định 365)
        
        Returns:
            DataFrame với các cột: open, high, low, close, volume
        """
        try:
            from datetime import timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            df = stock.quote.history(
                start=start_date,
                end=end_date
            )
            if df is not None and not df.empty:
                logger.debug(f"Historical prices: {len(df)} rows")
                return df
        except Exception as e:
            logger.warning(f"Could not extract historical prices: {e}")
        return None
    
    def _add_metadata(self, data: ExtractedData, symbol: str):
        """Thêm metadata vào các DataFrame"""
        for name, df in data.to_dict().items():
            if df is not None and not df.empty:
                df['_symbol'] = symbol
                df['_extracted_at'] = data.extracted_at
                df['_source'] = self.source
    
    def get_all_symbols(self) -> pd.DataFrame:
        """
        Lấy danh sách tất cả mã cổ phiếu trên sàn
        
        Returns:
            DataFrame chứa thông tin các mã cổ phiếu
        """
        try:
            stock = self._vnstock.stock(symbol='VNM', source=self.source)
            listing = stock.listing.all_symbols()
            return listing
        except Exception as e:
            logger.error(f"Could not get symbols list: {e}")
            return pd.DataFrame()
    
    def extract_multiple(self, symbols: list) -> Dict[str, ExtractedData]:
        """
        Thu thập dữ liệu cho nhiều mã cổ phiếu
        
        Args:
            symbols: Danh sách mã cổ phiếu
            
        Returns:
            Dictionary {symbol: ExtractedData}
        """
        results = {}
        total = len(symbols)
        
        for idx, symbol in enumerate(symbols, 1):
            logger.info(f"[{idx}/{total}] Processing {symbol}...")
            try:
                results[symbol] = self.extract(symbol)
            except Exception as e:
                logger.error(f"Failed to extract {symbol}: {e}")
                results[symbol] = ExtractedData(symbol=symbol)
        
        return results
