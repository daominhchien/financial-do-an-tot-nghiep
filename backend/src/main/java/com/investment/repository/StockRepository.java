package com.investment.repository;

import com.investment.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository: Stock
 */
@Repository
public interface StockRepository extends JpaRepository<Stock, String> {

    // Tìm theo sàn
    List<Stock> findByExchange(String exchange);

    // Tìm theo ngành
    List<Stock> findByIndustry(String industry);

    // Tìm theo keyword (tên hoặc mã)
    @Query("SELECT s FROM Stock s WHERE " +
            "LOWER(s.symbol) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
            "LOWER(s.companyName) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<Stock> searchByKeyword(String keyword);

    // Lấy danh sách các ngành
    @Query("SELECT DISTINCT s.industry FROM Stock s WHERE s.industry IS NOT NULL")
    List<String> findAllIndustries();
}
