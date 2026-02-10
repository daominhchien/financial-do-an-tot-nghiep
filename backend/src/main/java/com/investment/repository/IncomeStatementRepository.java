package com.investment.repository;

import com.investment.entity.IncomeStatement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository: Income Statement
 */
@Repository
public interface IncomeStatementRepository extends JpaRepository<IncomeStatement, Long> {

    List<IncomeStatement> findBySymbolOrderByReportDateDesc(String symbol);

    List<IncomeStatement> findBySymbolAndPeriodOrderByReportDateDesc(String symbol, String period);

    List<IncomeStatement> findBySymbolAndYearReport(String symbol, Integer year);

    @Query("SELECT i FROM IncomeStatement i WHERE i.symbol = :symbol ORDER BY i.reportDate DESC LIMIT 1")
    IncomeStatement findLatestBySymbol(String symbol);

    List<IncomeStatement> findBySymbolIn(List<String> symbols);
}
