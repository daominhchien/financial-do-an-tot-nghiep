# config/settings.py
"""
Cấu hình cho Financial ETL Pipeline

Đọc cấu hình từ file .env và cung cấp các dataclass cho các module khác.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables từ file .env
load_dotenv()


@dataclass
class DatabaseConfig:
    """
    Cấu hình kết nối PostgreSQL
    
    Attributes:
        host: Địa chỉ host database
        port: Port kết nối
        database: Tên database
        user: Username
        password: Password
    """
    host: str = "localhost"
    port: int = 5432
    database: str = "financial_db"
    user: str = "postgres"
    password: str = ""
    
    @property
    def connection_string(self) -> str:
        """Tạo connection string cho SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Khởi tạo từ environment variables"""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'financial_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
        )


@dataclass
class PipelineConfig:
    """
    Cấu hình cho pipeline ETL
    
    Attributes:
        symbols: Danh sách mã cổ phiếu cần thu thập
        period: Loại báo cáo ('quarter' hoặc 'year')
        source: Nguồn dữ liệu cho vnstock ('VCI', 'TCBS', 'SSI')
        output_dir: Thư mục lưu output CSV
        save_to_csv: Có lưu ra CSV không
        save_to_db: Có lưu vào database không
        language: Ngôn ngữ cho tên cột ('vi' hoặc 'en')
    """
    # Danh sách mã cổ phiếu mẫu (Blue chips)
    symbols: List[str] = field(default_factory=lambda: [
        'VNM',   # Vinamilk
        'FPT',   # FPT Corporation
        'VIC',   # Vingroup
        'VHM',   # Vinhomes
        'HPG',   # Hòa Phát
        'MWG',   # Mobile World
        'TCB',   # Techcombank
        'VCB',   # Vietcombank
        'ACB',   # ACB Bank
        'VPB',   # VPBank
    ])
    
    period: str = 'quarter'          # 'quarter' hoặc 'year'
    source: str = 'VCI'              # Nguồn dữ liệu: 'VCI', 'TCBS', 'SSI'
    output_dir: str = './output'     # Thư mục output
    save_to_csv: bool = True         # Lưu ra CSV
    save_to_db: bool = False         # Lưu vào PostgreSQL
    language: str = 'vi'             # Ngôn ngữ: 'vi' hoặc 'en'
    
    # Rate limiting
    request_delay: float = 1.0       # Delay giữa các request (giây)
    
    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Khởi tạo từ environment variables"""
        symbols_str = os.getenv('SYMBOLS', '')
        symbols = [s.strip() for s in symbols_str.split(',')] if symbols_str else None
        
        config = cls(
            period=os.getenv('PERIOD', 'quarter'),
            source=os.getenv('DATA_SOURCE', 'VCI'),
            output_dir=os.getenv('OUTPUT_DIR', './output'),
            save_to_csv=os.getenv('SAVE_TO_CSV', 'true').lower() == 'true',
            save_to_db=os.getenv('SAVE_TO_DB', 'false').lower() == 'true',
            language=os.getenv('LANGUAGE', 'vi'),
            request_delay=float(os.getenv('REQUEST_DELAY', '1.0')),
        )
        
        if symbols:
            config.symbols = symbols
            
        return config


@dataclass 
class Settings:
    """
    Settings tổng hợp cho toàn bộ ứng dụng
    """
    database: DatabaseConfig = field(default_factory=DatabaseConfig.from_env)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig.from_env)
    
    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    
    @property
    def output_path(self) -> Path:
        """Đường dẫn thư mục output"""
        path = Path(self.pipeline.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_path(self) -> Path:
        """Đường dẫn thư mục logs"""
        path = self.base_dir / 'logs'
        path.mkdir(parents=True, exist_ok=True)
        return path


# Singleton instance
settings = Settings()
