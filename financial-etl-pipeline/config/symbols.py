# config/symbols.py
"""
Danh sách mã cổ phiếu theo ngành và nhóm

Module này cung cấp các danh sách mã cổ phiếu được phân loại sẵn
để dễ dàng lựa chọn khi chạy pipeline.
"""

from typing import List, Dict

# ===== BLUE CHIPS - Cổ phiếu lớn thanh khoản cao =====
BLUE_CHIPS: List[str] = [
    'VNM',   # Vinamilk - Thực phẩm
    'FPT',   # FPT - Công nghệ
    'VIC',   # Vingroup - Bất động sản
    'VHM',   # Vinhomes - Bất động sản
    'HPG',   # Hòa Phát - Thép
    'MWG',   # Mobile World - Bán lẻ
    'MSN',   # Masan - Tiêu dùng
    'VRE',   # Vincom Retail - Bất động sản thương mại
    'SAB',   # Sabeco - Đồ uống
    'GAS',   # PV Gas - Dầu khí
]

# ===== NGÂN HÀNG =====
BANKS: List[str] = [
    'VCB',   # Vietcombank
    'TCB',   # Techcombank
    'CTG',   # Vietinbank
    'BID',   # BIDV
    'MBB',   # MB Bank
    'ACB',   # ACB
    'VPB',   # VPBank
    'TPB',   # TPBank
    'HDB',   # HDBank
    'STB',   # Sacombank
    'LPB',   # LienVietPostBank
    'EIB',   # Eximbank
    'SHB',   # SHB
    'OCB',   # OCB
    'MSB',   # MSB
]

# ===== CHỨNG KHOÁN =====
SECURITIES: List[str] = [
    'SSI',   # SSI
    'VCI',   # Vietcap
    'HCM',   # HSC
    'VND',   # VNDS
    'SHS',   # SHS
    'VIX',   # VIX
    'MBS',   # MBS
    'TVS',   # TVS
    'CTS',   # CTS
    'FTS',   # FTS
]

# ===== BẤT ĐỘNG SẢN =====
REAL_ESTATE: List[str] = [
    'VIC',   # Vingroup
    'VHM',   # Vinhomes
    'VRE',   # Vincom Retail
    'NVL',   # Novaland
    'KDH',   # Khang Điền
    'DXG',   # Đất Xanh
    'PDR',   # Phát Đạt
    'NLG',   # Nam Long
    'DIG',   # DIC Corp
    'HDG',   # Ha Do
]

# ===== CÔNG NGHỆ =====
TECHNOLOGY: List[str] = [
    'FPT',   # FPT
    'CMG',   # CMC
    'ELC',   # Elcom
    'ITD',   # ITD
    'POW',   # Powertech
]

# ===== THÉP - VẬT LIỆU XÂY DỰNG =====
STEEL_MATERIALS: List[str] = [
    'HPG',   # Hòa Phát
    'HSG',   # Hoa Sen
    'NKG',   # Nam Kim
    'TLH',   # Thép Tiến Lên
    'HMC',   # HMC
    'SMC',   # SMC
]

# ===== BÁN LẺ - TIÊU DÙNG =====
RETAIL_CONSUMER: List[str] = [
    'MWG',   # Mobile World
    'PNJ',   # PNJ
    'FRT',   # FPT Retail
    'DGW',   # Digiworld
    'VNM',   # Vinamilk
    'MSN',   # Masan
]

# ===== DẦU KHÍ - NĂNG LƯỢNG =====
OIL_GAS_ENERGY: List[str] = [
    'GAS',   # PV Gas
    'PLX',   # Petrolimex
    'PVD',   # PV Drilling
    'BSR',   # BSR
    'OIL',   # PV Oil
    'PVS',   # PV Tech
    'POW',   # Điện lực VN
    'PC1',   # PC1
    'GEX',   # Gelex
    'REE',   # Ree
]

# ===== TẤT CẢ THEO NGÀNH =====
SYMBOLS_BY_SECTOR: Dict[str, List[str]] = {
    'blue_chips': BLUE_CHIPS,
    'banks': BANKS,
    'securities': SECURITIES,
    'real_estate': REAL_ESTATE,
    'technology': TECHNOLOGY,
    'steel_materials': STEEL_MATERIALS,
    'retail_consumer': RETAIL_CONSUMER,
    'oil_gas_energy': OIL_GAS_ENERGY,
}

# ===== VN30 INDEX =====
VN30: List[str] = [
    'ACB', 'BCM', 'BID', 'BVH', 'CTG',
    'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW',
    'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB',
    'VIC', 'VJC', 'VNM', 'VPB', 'VRE',
]


def get_symbols_by_sectors(sectors: List[str]) -> List[str]:
    """
    Lấy danh sách mã cổ phiếu từ nhiều ngành
    
    Args:
        sectors: Danh sách tên ngành
        
    Returns:
        Danh sách mã cổ phiếu unique
        
    Example:
        >>> get_symbols_by_sectors(['banks', 'technology'])
        ['VCB', 'TCB', ..., 'FPT', 'CMG', ...]
    """
    symbols = []
    for sector in sectors:
        if sector in SYMBOLS_BY_SECTOR:
            symbols.extend(SYMBOLS_BY_SECTOR[sector])
    return list(set(symbols))  # Remove duplicates


def get_all_symbols() -> List[str]:
    """Lấy tất cả mã cổ phiếu từ mọi ngành (danh sách có sẵn)"""
    all_symbols = []
    for symbols in SYMBOLS_BY_SECTOR.values():
        all_symbols.extend(symbols)
    return list(set(all_symbols))


def fetch_all_symbols_from_exchange(exchange: str = 'all') -> List[str]:
    """
    Lấy TẤT CẢ mã cổ phiếu từ sàn chứng khoán thông qua vnstock API
    
    Args:
        exchange: Sàn giao dịch - 'HOSE', 'HNX', 'UPCOM', hoặc 'all'
    
    Returns:
        Danh sách tất cả mã cổ phiếu
        
    Example:
        >>> symbols = fetch_all_symbols_from_exchange('HOSE')
        >>> print(f"HOSE có {len(symbols)} mã")
        HOSE có 400+ mã
        
        >>> all_symbols = fetch_all_symbols_from_exchange('all')
        >>> print(f"Tổng cộng {len(all_symbols)} mã")
        Tổng cộng 1600+ mã
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock()
        listing = stock.stock(symbol='VNM', source='VCI').listing.all_symbols()
        
        if listing is None or listing.empty:
            print("⚠️ Không thể lấy danh sách từ API, sử dụng danh sách có sẵn")
            return get_all_symbols()
        
        # Lọc theo sàn nếu cần
        if exchange.upper() != 'ALL':
            listing = listing[listing['exchange'] == exchange.upper()]
        
        symbols = listing['symbol'].tolist()
        print(f"✅ Lấy được {len(symbols)} mã từ sàn {exchange.upper()}")
        return symbols
        
    except Exception as e:
        print(f"⚠️ Lỗi khi lấy từ API: {e}")
        print("   Sử dụng danh sách có sẵn...")
        return get_all_symbols()


def get_symbols_by_exchange(exchange: str) -> List[str]:
    """
    Lấy mã theo sàn từ danh sách có sẵn (không cần kết nối API)
    
    Danh sách một số mã phổ biến theo sàn:
    """
    HOSE_POPULAR = [
        'VNM', 'FPT', 'VIC', 'VHM', 'HPG', 'MWG', 'MSN', 'VRE', 'SAB', 'GAS',
        'VCB', 'TCB', 'CTG', 'BID', 'MBB', 'ACB', 'VPB', 'TPB', 'HDB', 'STB',
        'SSI', 'VCI', 'HCM', 'VND', 'SHS', 'VIX', 'MBS', 'TVS', 'CTS', 'FTS',
        'NVL', 'KDH', 'DXG', 'PDR', 'NLG', 'DIG', 'HDG',
        'HSG', 'NKG', 'TLH', 'HMC', 'SMC',
        'PNJ', 'FRT', 'DGW', 'PLX', 'PVD', 'BSR', 'OIL', 'PVS', 'POW', 'PC1', 'GEX', 'REE',
    ]
    
    HNX_POPULAR = [
        'SHB', 'PVS', 'NVB', 'IDC', 'CEO', 'PVI', 'VC3', 'TNG',
        'PLC', 'DBC', 'NDN', 'L14', 'HUT', 'VC2',
    ]
    
    UPCOM_POPULAR = [
        'BSR', 'ACV', 'MCH', 'VEA', 'QNS', 'VGT',
    ]
    
    exchange = exchange.upper()
    if exchange == 'HOSE':
        return HOSE_POPULAR
    elif exchange == 'HNX':
        return HNX_POPULAR
    elif exchange == 'UPCOM':
        return UPCOM_POPULAR
    else:
        return HOSE_POPULAR + HNX_POPULAR + UPCOM_POPULAR
