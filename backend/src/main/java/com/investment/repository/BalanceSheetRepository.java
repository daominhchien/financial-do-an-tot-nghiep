package com.investment.repository;

import com.investment.entity.BalanceSheet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository: Balance Sheet
 */
@Repository
public interface BalanceSheetRepository extends JpaRepository<BalanceSheet, Long> {

    // Lấy theo mã cổ phiếu, sắp xếp theo ngày mới nhất
    List<BalanceSheet> findBySymbolOrderByReportDateDesc(String symbol);

    // Lấy theo mã và kỳ báo cáo
    List<BalanceSheet> findBySymbolAndPeriodOrderByReportDateDesc(String symbol, String period);

    // Lấy theo năm
    List<BalanceSheet> findBySymbolAndYearReport(String symbol, Integer year);

    // Lấy báo cáo mới nhất của mã
    @Query("SELECT b FROM BalanceSheet b WHERE b.symbol = :symbol ORDER BY b.reportDate DESC LIMIT 1")
    BalanceSheet findLatestBySymbol(String symbol);

    // Lấy theo nhiều mã (để so sánh)
    List<BalanceSheet> findBySymbolIn(List<String> symbols);
}
