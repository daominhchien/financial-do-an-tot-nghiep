package com.investment.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Entity: Financial Ratios (Chỉ số tài chính)
 * 
 * Lưu trữ các chỉ số tài chính phục vụ phân tích cơ bản.
 */
@Entity
@Table(name = "financial_ratios", indexes = {
        @Index(name = "idx_fr_symbol", columnList = "symbol"),
        @Index(name = "idx_fr_date", columnList = "reportDate")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FinancialRatio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 10)
    private String symbol;

    @Column(name = "report_date")
    private LocalDate reportDate;

    @Column(length = 20)
    private String period;

    @Column(name = "year_report")
    private Integer yearReport;

    // ===== CHỈ SỐ SINH LỜI (Profitability) =====
    @Column(precision = 10, scale = 4)
    private BigDecimal grossMargin; // Biên lợi nhuận gộp

    @Column(precision = 10, scale = 4)
    private BigDecimal operatingMargin; // Biên lợi nhuận hoạt động

    @Column(precision = 10, scale = 4)
    private BigDecimal netMargin; // Biên lợi nhuận ròng

    @Column(precision = 10, scale = 4)
    private BigDecimal roe; // Return on Equity

    @Column(precision = 10, scale = 4)
    private BigDecimal roa; // Return on Assets

    @Column(precision = 10, scale = 4)
    private BigDecimal roic; // Return on Invested Capital

    // ===== CHỈ SỐ ĐỊNH GIÁ (Valuation) =====
    @Column(precision = 10, scale = 2)
    private BigDecimal pe; // Price to Earnings

    @Column(precision = 10, scale = 2)
    private BigDecimal pb; // Price to Book

    @Column(precision = 10, scale = 2)
    private BigDecimal ps; // Price to Sales

    @Column(precision = 10, scale = 4)
    private BigDecimal evToEbitda; // EV/EBITDA

    // ===== CHỈ SỐ THANH KHOẢN (Liquidity) =====
    @Column(precision = 10, scale = 2)
    private BigDecimal currentRatio; // Hệ số thanh toán hiện hành

    @Column(precision = 10, scale = 2)
    private BigDecimal quickRatio; // Hệ số thanh toán nhanh

    @Column(precision = 10, scale = 2)
    private BigDecimal cashRatio; // Hệ số thanh toán tiền mặt

    // ===== CHỈ SỐ ĐÒN BẨY (Leverage) =====
    @Column(precision = 10, scale = 2)
    private BigDecimal debtToEquity; // Nợ/Vốn chủ sở hữu

    @Column(precision = 10, scale = 2)
    private BigDecimal debtToAssets; // Nợ/Tổng tài sản

    @Column(precision = 10, scale = 2)
    private BigDecimal interestCoverage; // Hệ số thanh toán lãi vay

    // ===== CHỈ SỐ HIỆU QUẢ (Efficiency) =====
    @Column(precision = 10, scale = 2)
    private BigDecimal assetTurnover; // Vòng quay tài sản

    @Column(precision = 10, scale = 2)
    private BigDecimal inventoryTurnover; // Vòng quay hàng tồn kho

    @Column(precision = 10, scale = 2)
    private BigDecimal receivablesTurnover; // Vòng quay phải thu

    // ===== CHỈ SỐ CỔ TỨC =====
    @Column(precision = 10, scale = 4)
    private BigDecimal dividendYield; // Tỷ suất cổ tức

    @Column(precision = 10, scale = 2)
    private BigDecimal payoutRatio; // Tỷ lệ chi trả cổ tức

    // ===== CHỈ SỐ TĂNG TRƯỞNG (Growth) =====
    @Column(precision = 10, scale = 4)
    private BigDecimal revenueGrowth; // Tăng trưởng doanh thu

    @Column(precision = 10, scale = 4)
    private BigDecimal netIncomeGrowth; // Tăng trưởng lợi nhuận

    @Column(precision = 10, scale = 4)
    private BigDecimal epsGrowth; // Tăng trưởng EPS

    // Metadata
    @Column(name = "created_at")
    private LocalDate createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
    }
}
