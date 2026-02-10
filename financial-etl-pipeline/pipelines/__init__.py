# pipelines/__init__.py
"""
Pipelines package - ETL Pipeline chính

Modules:
    - financial_pipeline: Pipeline thu thập dữ liệu tài chính
"""

from .financial_pipeline import FinancialDataPipeline

__all__ = ['FinancialDataPipeline']
