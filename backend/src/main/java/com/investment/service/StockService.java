package com.investment.service;

import com.investment.entity.*;
import com.investment.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Service: Stock Service
 * 
 * Business logic cho việc quản lý và truy vấn dữ liệu cổ phiếu.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class StockService {

    private final StockRepository stockRepository;
    private final BalanceSheetRepository balanceSheetRepository;
    private final IncomeStatementRepository incomeStatementRepository;
    private final FinancialRatioRepository financialRatioRepository;

    // ===== STOCK OPERATIONS =====

    public List<Stock> getAllStocks() {
        return stockRepository.findAll();
    }

    public Optional<Stock> getStockBySymbol(String symbol) {
        return stockRepository.findById(symbol.toUpperCase());
    }

    public List<Stock> searchStocks(String keyword) {
        return stockRepository.searchByKeyword(keyword);
    }

    public List<Stock> getStocksByExchange(String exchange) {
        return stockRepository.findByExchange(exchange);
    }

    public List<Stock> getStocksByIndustry(String industry) {
        return stockRepository.findByIndustry(industry);
    }

    public List<String> getAllIndustries() {
        return stockRepository.findAllIndustries();
    }

    // ===== FINANCIAL DATA =====

    public List<BalanceSheet> getBalanceSheets(String symbol) {
        return balanceSheetRepository.findBySymbolOrderByReportDateDesc(symbol.toUpperCase());
    }

    public List<IncomeStatement> getIncomeStatements(String symbol) {
        return incomeStatementRepository.findBySymbolOrderByReportDateDesc(symbol.toUpperCase());
    }

    public List<FinancialRatio> getFinancialRatios(String symbol) {
        return financialRatioRepository.findBySymbolOrderByReportDateDesc(symbol.toUpperCase());
    }

    // ===== COMPARISON =====

    public List<FinancialRatio> compareStocks(List<String> symbols) {
        List<String> upperSymbols = symbols.stream()
                .map(String::toUpperCase)
                .toList();
        return financialRatioRepository.findLatestBySymbols(upperSymbols);
    }

    // ===== LATEST DATA =====

    public BalanceSheet getLatestBalanceSheet(String symbol) {
        return balanceSheetRepository.findLatestBySymbol(symbol.toUpperCase());
    }

    public IncomeStatement getLatestIncomeStatement(String symbol) {
        return incomeStatementRepository.findLatestBySymbol(symbol.toUpperCase());
    }

    public FinancialRatio getLatestFinancialRatio(String symbol) {
        return financialRatioRepository.findLatestBySymbol(symbol.toUpperCase());
    }
}
