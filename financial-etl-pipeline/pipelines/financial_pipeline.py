# pipelines/financial_pipeline.py
"""
Financial Data Pipeline - Pipeline ETL hoàn chỉnh

Pipeline này kết hợp 3 bước ETL:
1. EXTRACT: Thu thập dữ liệu từ vnstock
2. TRANSFORM: Làm sạch và tính toán chỉ số
3. LOAD: Lưu ra CSV (và database nếu cấu hình)

Features:
- Xử lý nhiều mã cổ phiếu song song
- Progress tracking và logging chi tiết
- Error handling và retry mechanism
- Summary report sau khi chạy
"""

import sys
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import pandas as pd
from loguru import logger
from tqdm import tqdm

# Import các modules
from extractors.vnstock_extractor import VNStockExtractor, ExtractedData
from transformers.cleaner import DataCleaner
from transformers.calculator import RatioCalculator
from loaders.csv_loader import CSVLoader


@dataclass
class PipelineResult:
    """
    Kết quả chạy pipeline
    
    Attributes:
        success_count: Số mã thành công
        failed_count: Số mã thất bại
        total_time: Tổng thời gian chạy (giây)
        data: Dictionary chứa dữ liệu đã extract
        errors: Dictionary chứa các lỗi
    """
    success_count: int = 0
    failed_count: int = 0
    total_time: float = 0.0
    data: Dict[str, ExtractedData] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    output_paths: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Tỷ lệ thành công (%)"""
        total = self.success_count + self.failed_count
        return (self.success_count / total * 100) if total > 0 else 0
    
    def summary(self) -> str:
        """Tạo text summary"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    PIPELINE RESULT SUMMARY                   ║
╠══════════════════════════════════════════════════════════════╣
║  Total symbols processed: {self.success_count + self.failed_count:>4}                              ║
║  Successful: {self.success_count:>4}  |  Failed: {self.failed_count:>4}  |  Rate: {self.success_rate:>5.1f}%       ║
║  Total time: {self.total_time:>6.1f} seconds                                ║
╚══════════════════════════════════════════════════════════════╝
"""


class FinancialDataPipeline:
    """
    Pipeline ETL chính để thu thập dữ liệu tài chính
    
    Quy trình:
    1. Khởi tạo các components (extractor, cleaner, calculator, loader)
    2. Lặp qua từng mã cổ phiếu
    3. Extract dữ liệu từ vnstock
    4. Transform (làm sạch, tính chỉ số bổ sung)
    5. Load (lưu ra CSV)
    6. Tạo summary report
    
    Example:
        >>> from config.settings import PipelineConfig
        >>> config = PipelineConfig(symbols=['VNM', 'FPT', 'VIC'])
        >>> pipeline = FinancialDataPipeline(config)
        >>> result = pipeline.run()
        >>> print(result.summary())
    """
    
    def __init__(
        self,
        symbols: List[str] = None,
        output_dir: str = './output',
        source: str = 'VCI',
        period: str = 'quarter',
        language: str = 'vi',
        request_delay: float = 1.5,
        verbose: bool = True
    ):
        """
        Khởi tạo Pipeline
        
        Args:
            symbols: Danh sách mã cổ phiếu cần thu thập
            output_dir: Thư mục output cho CSV
            source: Nguồn dữ liệu vnstock ('VCI', 'TCBS', 'SSI')
            period: Loại báo cáo ('quarter' hoặc 'year')
            language: Ngôn ngữ ('vi' hoặc 'en')
            request_delay: Delay giữa các request (giây)
            verbose: Hiển thị progress bar và log chi tiết
        """
        # Mã cổ phiếu mặc định nếu không truyền
        self.symbols = symbols or ['VNM', 'FPT', 'VIC', 'HPG', 'TCB']
        self.output_dir = output_dir
        self.verbose = verbose
        
        # Khởi tạo các components
        self.extractor = VNStockExtractor(
            source=source,
            period=period,
            language=language,
            request_delay=request_delay
        )
        
        self.cleaner = DataCleaner(
            fill_na_strategy='zero',
            remove_duplicates=True,
            normalize_columns=True
        )
        
        self.calculator = RatioCalculator(decimal_places=4)
        
        self.loader = CSVLoader(
            output_dir=output_dir,
            encoding='utf-8-sig',
            create_combined=True
        )
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Pipeline initialized for {len(self.symbols)} symbols")
    
    def _setup_logging(self):
        """Cấu hình logging"""
        # Xóa default handler
        logger.remove()
        
        # Console handler với màu
        if self.verbose:
            logger.add(
                sys.stdout,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
                level="INFO",
                colorize=True
            )
        
        # File handler
        log_dir = Path(self.output_dir) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="10 MB"
        )
    
    def run(self) -> PipelineResult:
        """
        Chạy pipeline cho tất cả mã cổ phiếu
        
        Returns:
            PipelineResult chứa kết quả và thống kê
        """
        result = PipelineResult()
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("🚀 STARTING FINANCIAL DATA PIPELINE")
        logger.info(f"   Symbols: {len(self.symbols)}")
        logger.info(f"   Output: {self.output_dir}")
        logger.info("=" * 60)
        
        # Progress bar
        iterator = tqdm(
            self.symbols, 
            desc="Processing", 
            disable=not self.verbose,
            ncols=80
        )
        
        for symbol in iterator:
            iterator.set_description(f"Processing {symbol}")
            
            try:
                # === EXTRACT ===
                extracted = self._extract(symbol)
                
                if not extracted.is_valid():
                    logger.warning(f"⚠️ {symbol}: No valid data extracted")
                    result.failed_count += 1
                    result.errors[symbol] = "No valid data"
                    continue
                
                # === TRANSFORM ===
                transformed = self._transform(extracted)
                
                # === LOAD ===
                paths = self._load(transformed)
                
                # Thành công
                result.success_count += 1
                result.data[symbol] = transformed
                result.output_paths[symbol] = paths
                
                logger.info(f"✅ {symbol}: Completed successfully")
                
            except Exception as e:
                result.failed_count += 1
                result.errors[symbol] = str(e)
                logger.error(f"❌ {symbol}: {str(e)}")
        
        # Tính thời gian và tạo summary
        result.total_time = time.time() - start_time
        
        # Tạo file combined nếu có dữ liệu
        if result.data:
            self.loader.save_combined(result.data)
        
        # Log summary
        logger.info(result.summary())
        
        # Lưu metadata
        self._save_metadata(result)
        
        return result
    
    def _extract(self, symbol: str) -> ExtractedData:
        """
        Bước EXTRACT: Thu thập dữ liệu từ vnstock
        """
        logger.debug(f"[{symbol}] Extracting...")
        return self.extractor.extract(symbol)
    
    def _transform(self, data: ExtractedData) -> ExtractedData:
        """
        Bước TRANSFORM: Làm sạch và tính toán chỉ số
        """
        logger.debug(f"[{data.symbol}] Transforming...")
        
        # Làm sạch các DataFrame
        if data.balance_sheet is not None:
            data.balance_sheet = self.cleaner.clean(data.balance_sheet)
        
        if data.income_statement is not None:
            data.income_statement = self.cleaner.clean(data.income_statement)
        
        if data.cash_flow is not None:
            data.cash_flow = self.cleaner.clean(data.cash_flow)
        
        # Tính thêm chỉ số nếu chưa có trong ratios
        if data.balance_sheet is not None and data.income_statement is not None:
            additional_ratios = self.calculator.calculate_all(
                data.balance_sheet,
                data.income_statement,
                data.cash_flow
            )
            
            # Merge với ratios có sẵn
            if data.ratios is not None and not data.ratios.empty:
                # Chỉ thêm các cột chưa có
                for col in additional_ratios.columns:
                    if col not in data.ratios.columns:
                        data.ratios[col] = additional_ratios[col].values[0]
            else:
                additional_ratios['_symbol'] = data.symbol
                data.ratios = additional_ratios
        
        return data
    
    def _load(self, data: ExtractedData) -> Dict[str, str]:
        """
        Bước LOAD: Lưu ra CSV
        """
        logger.debug(f"[{data.symbol}] Loading...")
        return self.loader.save(data)
    
    def _save_metadata(self, result: PipelineResult):
        """Lưu metadata về lần chạy pipeline"""
        metadata = {
            'run_time': datetime.now().isoformat(),
            'total_symbols': len(self.symbols),
            'success_count': result.success_count,
            'failed_count': result.failed_count,
            'success_rate': result.success_rate,
            'total_time_seconds': result.total_time,
            'symbols_processed': list(result.data.keys()),
            'symbols_failed': list(result.errors.keys()),
            'errors': result.errors
        }
        
        # Lưu ra JSON
        import json
        metadata_path = Path(self.output_dir) / 'pipeline_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 Metadata saved to {metadata_path}")
    
    def run_single(self, symbol: str) -> Optional[ExtractedData]:
        """
        Chạy pipeline cho một mã cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            
        Returns:
            ExtractedData hoặc None nếu thất bại
        """
        try:
            extracted = self._extract(symbol)
            transformed = self._transform(extracted)
            self._load(transformed)
            return transformed
        except Exception as e:
            logger.error(f"Failed to process {symbol}: {e}")
            return None
    
    def get_data_quality_report(self, symbol: str) -> Dict[str, Any]:
        """
        Tạo báo cáo chất lượng dữ liệu cho một mã
        """
        if symbol not in [d.symbol for d in self.loader.get_saved_symbols()]:
            return {'error': f'No data for {symbol}'}
        
        reports = {}
        
        for report_type in ['balance_sheet', 'income_statement', 'cash_flow', 'ratios']:
            df = self.loader.load(symbol, report_type)
            if df is not None:
                reports[report_type] = self.cleaner.get_data_quality_report(df)
        
        return reports


def create_pipeline(
    symbols: List[str] = None,
    output_dir: str = './output',
    quick: bool = False
) -> FinancialDataPipeline:
    """
    Factory function để tạo pipeline với cấu hình sẵn
    
    Args:
        symbols: Danh sách mã cổ phiếu (mặc định là VN30 top 10)
        output_dir: Thư mục output
        quick: Nếu True, giảm delay để chạy nhanh hơn (cho testing)
    
    Returns:
        FinancialDataPipeline đã cấu hình
    """
    if symbols is None:
        # Top 10 VN30 mặc định
        symbols = ['VNM', 'FPT', 'VIC', 'VHM', 'HPG', 'MWG', 'TCB', 'VCB', 'ACB', 'VPB']
    
    return FinancialDataPipeline(
        symbols=symbols,
        output_dir=output_dir,
        source='VCI',
        period='quarter',
        language='vi',
        request_delay=0.5 if quick else 1.5,
        verbose=True
    )
