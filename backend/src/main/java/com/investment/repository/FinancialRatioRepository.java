package com.investment.repository;

import com.investment.entity.FinancialRatio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository: Financial Ratios
 */
@Repository
public interface FinancialRatioRepository extends JpaRepository<FinancialRatio, Long> {

    List<FinancialRatio> findBySymbolOrderByReportDateDesc(String symbol);

    List<FinancialRatio> findBySymbolAndPeriodOrderByReportDateDesc(String symbol, String period);

    @Query("SELECT f FROM FinancialRatio f WHERE f.symbol = :symbol ORDER BY f.reportDate DESC LIMIT 1")
    FinancialRatio findLatestBySymbol(String symbol);

    List<FinancialRatio> findBySymbolIn(List<String> symbols);

    // So sánh ROE của nhiều mã, lấy báo cáo mới nhất
    @Query("SELECT f FROM FinancialRatio f WHERE f.symbol IN :symbols " +
            "AND f.reportDate = (SELECT MAX(f2.reportDate) FROM FinancialRatio f2 WHERE f2.symbol = f.symbol)")
    List<FinancialRatio> findLatestBySymbols(List<String> symbols);
}
