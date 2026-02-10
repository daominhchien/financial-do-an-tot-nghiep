# transformers/calculator.py
"""
Ratio Calculator - Tính toán các chỉ số tài chính

Module này tính toán các nhóm chỉ số:
1. Chỉ số sinh lời (Profitability Ratios)
2. Chỉ số hiệu quả sử dụng vốn (Return Ratios)
3. Chỉ số thanh khoản (Liquidity Ratios)
4. Chỉ số đòn bẩy (Leverage Ratios)
5. Chỉ số hoạt động (Activity Ratios)
6. Chỉ số định giá (Valuation Ratios)
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger


class RatioCalculator:
    """
    Tính toán các chỉ số tài chính cho phân tích cơ bản
    
    Hỗ trợ tính:
    - Tự động từ raw data
    - Theo công thức tùy chỉnh
    - So sánh qua các kỳ
    
    Example:
        >>> calculator = RatioCalculator()
        >>> ratios = calculator.calculate_all(balance_sheet, income_statement)
        >>> print(ratios['roe'], ratios['current_ratio'])
    """
    
    def __init__(self, decimal_places: int = 4):
        """
        Args:
            decimal_places: Số chữ số thập phân cho các chỉ số
        """
        self.decimal_places = decimal_places
    
    def calculate_all(
        self,
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        cash_flow: Optional[pd.DataFrame] = None,
        market_data: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Tính tất cả các chỉ số tài chính
        
        Args:
            balance_sheet: Bảng cân đối kế toán
            income_statement: Báo cáo KQKD
            cash_flow: Báo cáo lưu chuyển tiền tệ (optional)
            market_data: Dict chứa price, market_cap, shares_outstanding
        
        Returns:
            DataFrame chứa các chỉ số đã tính
        """
        ratios = {}
        
        try:
            # 1. Chỉ số sinh lời
            profitability = self.calculate_profitability_ratios(income_statement)
            ratios.update(profitability)
            
            # 2. Chỉ số return
            returns = self.calculate_return_ratios(balance_sheet, income_statement)
            ratios.update(returns)
            
            # 3. Chỉ số thanh khoản
            liquidity = self.calculate_liquidity_ratios(balance_sheet)
            ratios.update(liquidity)
            
            # 4. Chỉ số đòn bẩy
            leverage = self.calculate_leverage_ratios(balance_sheet)
            ratios.update(leverage)
            
            # 5. Chỉ số hoạt động
            if cash_flow is not None:
                activity = self.calculate_activity_ratios(
                    balance_sheet, income_statement, cash_flow
                )
                ratios.update(activity)
            
            # 6. Chỉ số định giá (nếu có market data)
            if market_data:
                valuation = self.calculate_valuation_ratios(
                    balance_sheet, income_statement, market_data
                )
                ratios.update(valuation)
            
            # Chuyển thành DataFrame
            result = pd.DataFrame([ratios])
            
            logger.debug(f"Calculated {len(ratios)} ratios")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating ratios: {e}")
            return pd.DataFrame()
    
    def calculate_profitability_ratios(
        self, 
        income_statement: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Tính chỉ số sinh lời
        
        Công thức:
        - Gross Margin = Lợi nhuận gộp / Doanh thu
        - Operating Margin = Lợi nhuận từ HĐKD / Doanh thu
        - Net Margin = Lợi nhuận sau thuế / Doanh thu
        - EBITDA Margin = EBITDA / Doanh thu
        """
        ratios = {}
        
        try:
            # Lấy dữ liệu mới nhất (hàng đầu tiên)
            latest = income_statement.iloc[0] if len(income_statement) > 0 else {}
            
            # Tìm các cột phù hợp (có thể khác nhau tùy source)
            revenue = self._find_value(latest, ['revenue', 'doanh_thu', 'doanh_thu_thuần'])
            gross_profit = self._find_value(latest, ['gross_profit', 'lợi_nhuận_gộp'])
            operating_income = self._find_value(latest, ['operating_income', 'lợi_nhuận_từ_hđkd'])
            net_income = self._find_value(latest, ['net_income', 'lợi_nhuận_sau_thuế'])
            
            if revenue and revenue != 0:
                if gross_profit:
                    ratios['gross_margin'] = round(gross_profit / revenue, self.decimal_places)
                
                if operating_income:
                    ratios['operating_margin'] = round(operating_income / revenue, self.decimal_places)
                
                if net_income:
                    ratios['net_margin'] = round(net_income / revenue, self.decimal_places)
                    
        except Exception as e:
            logger.warning(f"Could not calculate profitability ratios: {e}")
        
        return ratios
    
    def calculate_return_ratios(
        self,
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Tính chỉ số hiệu quả sử dụng vốn
        
        Công thức:
        - ROE = Lợi nhuận sau thuế / Vốn chủ sở hữu bình quân
        - ROA = Lợi nhuận sau thuế / Tổng tài sản bình quân
        - ROIC = NOPAT / Invested Capital
        """
        ratios = {}
        
        try:
            # Dữ liệu mới nhất
            bs_latest = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            is_latest = income_statement.iloc[0] if len(income_statement) > 0 else {}
            
            # Giá trị cần thiết
            net_income = self._find_value(is_latest, ['net_income', 'lợi_nhuận_sau_thuế'])
            total_equity = self._find_value(bs_latest, ['total_equity', 'vốn_chủ_sở_hữu'])
            total_assets = self._find_value(bs_latest, ['total_assets', 'tổng_tài_sản'])
            
            # Tính ROE
            if net_income and total_equity and total_equity != 0:
                ratios['roe'] = round(net_income / total_equity, self.decimal_places)
            
            # Tính ROA
            if net_income and total_assets and total_assets != 0:
                ratios['roa'] = round(net_income / total_assets, self.decimal_places)
                
        except Exception as e:
            logger.warning(f"Could not calculate return ratios: {e}")
        
        return ratios
    
    def calculate_liquidity_ratios(
        self, 
        balance_sheet: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Tính chỉ số thanh khoản
        
        Công thức:
        - Current Ratio = Tài sản ngắn hạn / Nợ ngắn hạn
        - Quick Ratio = (Tài sản ngắn hạn - Hàng tồn kho) / Nợ ngắn hạn
        - Cash Ratio = Tiền và tương đương tiền / Nợ ngắn hạn
        """
        ratios = {}
        
        try:
            latest = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            
            current_assets = self._find_value(latest, ['current_assets', 'tài_sản_ngắn_hạn'])
            current_liabilities = self._find_value(latest, ['current_liabilities', 'nợ_ngắn_hạn'])
            inventory = self._find_value(latest, ['inventory', 'hàng_tồn_kho'], default=0)
            cash = self._find_value(latest, ['cash', 'tiền_và_tương_đương_tiền'], default=0)
            
            if current_liabilities and current_liabilities != 0:
                # Current Ratio
                if current_assets:
                    ratios['current_ratio'] = round(
                        current_assets / current_liabilities, 
                        self.decimal_places
                    )
                
                # Quick Ratio
                if current_assets:
                    quick_assets = current_assets - inventory
                    ratios['quick_ratio'] = round(
                        quick_assets / current_liabilities,
                        self.decimal_places
                    )
                
                # Cash Ratio
                if cash:
                    ratios['cash_ratio'] = round(
                        cash / current_liabilities,
                        self.decimal_places
                    )
                    
        except Exception as e:
            logger.warning(f"Could not calculate liquidity ratios: {e}")
        
        return ratios
    
    def calculate_leverage_ratios(
        self, 
        balance_sheet: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Tính chỉ số đòn bẩy tài chính
        
        Công thức:
        - Debt to Equity = Tổng nợ / Vốn chủ sở hữu
        - Debt to Assets = Tổng nợ / Tổng tài sản
        - Equity Ratio = Vốn chủ sở hữu / Tổng tài sản
        - Interest Coverage = EBIT / Chi phí lãi vay
        """
        ratios = {}
        
        try:
            latest = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            
            total_liabilities = self._find_value(latest, ['total_liabilities', 'nợ_phải_trả', 'tổng_nợ'])
            total_equity = self._find_value(latest, ['total_equity', 'vốn_chủ_sở_hữu'])
            total_assets = self._find_value(latest, ['total_assets', 'tổng_tài_sản'])
            
            # Debt to Equity
            if total_liabilities and total_equity and total_equity != 0:
                ratios['debt_to_equity'] = round(
                    total_liabilities / total_equity,
                    self.decimal_places
                )
            
            # Debt to Assets
            if total_liabilities and total_assets and total_assets != 0:
                ratios['debt_to_assets'] = round(
                    total_liabilities / total_assets,
                    self.decimal_places
                )
            
            # Equity Ratio
            if total_equity and total_assets and total_assets != 0:
                ratios['equity_ratio'] = round(
                    total_equity / total_assets,
                    self.decimal_places
                )
                
        except Exception as e:
            logger.warning(f"Could not calculate leverage ratios: {e}")
        
        return ratios
    
    def calculate_activity_ratios(
        self,
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        cash_flow: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Tính chỉ số hoạt động
        
        Công thức:
        - Asset Turnover = Doanh thu / Tổng tài sản bình quân
        - Inventory Turnover = Giá vốn / Hàng tồn kho bình quân
        - Receivables Turnover = Doanh thu / Phải thu bình quân
        """
        ratios = {}
        
        try:
            bs_latest = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            is_latest = income_statement.iloc[0] if len(income_statement) > 0 else {}
            
            revenue = self._find_value(is_latest, ['revenue', 'doanh_thu'])
            total_assets = self._find_value(bs_latest, ['total_assets', 'tổng_tài_sản'])
            inventory = self._find_value(bs_latest, ['inventory', 'hàng_tồn_kho'])
            cogs = self._find_value(is_latest, ['cost_of_goods_sold', 'giá_vốn', 'giá_vốn_hàng_bán'])
            
            # Asset Turnover
            if revenue and total_assets and total_assets != 0:
                ratios['asset_turnover'] = round(
                    revenue / total_assets,
                    self.decimal_places
                )
            
            # Inventory Turnover
            if cogs and inventory and inventory != 0:
                ratios['inventory_turnover'] = round(
                    cogs / inventory,
                    self.decimal_places
                )
                # Days Inventory Outstanding
                ratios['days_inventory'] = round(365 / ratios['inventory_turnover'], 0)
                
        except Exception as e:
            logger.warning(f"Could not calculate activity ratios: {e}")
        
        return ratios
    
    def calculate_valuation_ratios(
        self,
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        market_data: Dict
    ) -> Dict[str, float]:
        """
        Tính chỉ số định giá
        
        Cần market_data chứa:
        - price: Giá hiện tại
        - market_cap: Vốn hóa thị trường
        - shares_outstanding: Số cổ phiếu lưu hành
        
        Công thức:
        - P/E = Giá / EPS
        - P/B = Vốn hóa / Vốn chủ sở hữu
        - P/S = Vốn hóa / Doanh thu
        - EV/EBITDA = Enterprise Value / EBITDA
        """
        ratios = {}
        
        try:
            price = market_data.get('price')
            market_cap = market_data.get('market_cap')
            shares = market_data.get('shares_outstanding')
            
            bs_latest = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            is_latest = income_statement.iloc[0] if len(income_statement) > 0 else {}
            
            eps = self._find_value(is_latest, ['eps', 'lãi_cơ_bản_trên_cổ_phiếu'])
            total_equity = self._find_value(bs_latest, ['total_equity', 'vốn_chủ_sở_hữu'])
            revenue = self._find_value(is_latest, ['revenue', 'doanh_thu'])
            
            # P/E Ratio
            if price and eps and eps != 0:
                ratios['pe_ratio'] = round(price / eps, self.decimal_places)
            
            # P/B Ratio
            if market_cap and total_equity and total_equity != 0:
                ratios['pb_ratio'] = round(market_cap / total_equity, self.decimal_places)
            
            # P/S Ratio
            if market_cap and revenue and revenue != 0:
                ratios['ps_ratio'] = round(market_cap / revenue, self.decimal_places)
                
        except Exception as e:
            logger.warning(f"Could not calculate valuation ratios: {e}")
        
        return ratios
    
    def _find_value(
        self, 
        data: Dict, 
        possible_keys: list, 
        default=None
    ) -> Optional[float]:
        """
        Tìm giá trị từ dict với nhiều key có thể
        
        Args:
            data: Dictionary hoặc Series chứa dữ liệu
            possible_keys: Danh sách các key có thể
            default: Giá trị mặc định nếu không tìm thấy
        """
        if isinstance(data, pd.Series):
            data = data.to_dict()
        
        for key in possible_keys:
            if key in data:
                value = data[key]
                if pd.notna(value) and value != 0:
                    return float(value)
            
            # Thử với lowercase
            key_lower = key.lower()
            if key_lower in data:
                value = data[key_lower]
                if pd.notna(value) and value != 0:
                    return float(value)
        
        return default
    
    def calculate_growth_rates(
        self,
        current_period: pd.DataFrame,
        previous_period: pd.DataFrame,
        metrics: list = None
    ) -> Dict[str, float]:
        """
        Tính tốc độ tăng trưởng so với kỳ trước
        
        Args:
            current_period: Dữ liệu kỳ hiện tại
            previous_period: Dữ liệu kỳ trước
            metrics: Danh sách chỉ tiêu cần tính growth
        
        Returns:
            Dict với {metric_growth: percentage}
        """
        if metrics is None:
            metrics = ['revenue', 'net_income', 'total_assets', 'total_equity']
        
        growth_rates = {}
        
        for metric in metrics:
            try:
                current = self._find_value(current_period.iloc[0], [metric])
                previous = self._find_value(previous_period.iloc[0], [metric])
                
                if current and previous and previous != 0:
                    growth = (current - previous) / abs(previous)
                    growth_rates[f'{metric}_growth'] = round(growth, self.decimal_places)
                    
            except Exception:
                continue
        
        return growth_rates
