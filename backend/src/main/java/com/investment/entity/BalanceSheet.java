package com.investment.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Entity: Balance Sheet (Bảng cân đối kế toán)
 * 
 * Lưu trữ dữ liệu bảng cân đối kế toán của các công ty.
 */
@Entity
@Table(name = "balance_sheets", indexes = {
        @Index(name = "idx_bs_symbol", columnList = "symbol"),
        @Index(name = "idx_bs_date", columnList = "reportDate")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BalanceSheet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 10)
    private String symbol;

    @Column(name = "report_date")
    private LocalDate reportDate;

    @Column(length = 20)
    private String period; // Q1, Q2, Q3, Q4 hoặc YEAR

    @Column(name = "year_report")
    private Integer yearReport;

    // ===== TÀI SẢN (ASSETS) =====
    @Column(precision = 20, scale = 2)
    private BigDecimal totalAssets; // Tổng tài sản

    @Column(precision = 20, scale = 2)
    private BigDecimal currentAssets; // Tài sản ngắn hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal cash; // Tiền và tương đương tiền

    @Column(precision = 20, scale = 2)
    private BigDecimal shortTermInvestments; // Đầu tư ngắn hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal receivables; // Phải thu ngắn hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal inventory; // Hàng tồn kho

    @Column(precision = 20, scale = 2)
    private BigDecimal nonCurrentAssets; // Tài sản dài hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal fixedAssets; // Tài sản cố định

    @Column(precision = 20, scale = 2)
    private BigDecimal longTermInvestments; // Đầu tư dài hạn

    // ===== NỢ PHẢI TRẢ (LIABILITIES) =====
    @Column(precision = 20, scale = 2)
    private BigDecimal totalLiabilities; // Tổng nợ phải trả

    @Column(precision = 20, scale = 2)
    private BigDecimal currentLiabilities; // Nợ ngắn hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal shortTermDebt; // Vay ngắn hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal accountsPayable; // Phải trả người bán

    @Column(precision = 20, scale = 2)
    private BigDecimal nonCurrentLiabilities; // Nợ dài hạn

    @Column(precision = 20, scale = 2)
    private BigDecimal longTermDebt; // Vay dài hạn

    // ===== VỐN CHỦ SỞ HỮU (EQUITY) =====
    @Column(precision = 20, scale = 2)
    private BigDecimal totalEquity; // Vốn chủ sở hữu

    @Column(precision = 20, scale = 2)
    private BigDecimal charterCapital; // Vốn điều lệ

    @Column(precision = 20, scale = 2)
    private BigDecimal retainedEarnings; // Lợi nhuận chưa phân phối

    // Metadata
    @Column(name = "created_at")
    private LocalDate createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
    }
}
