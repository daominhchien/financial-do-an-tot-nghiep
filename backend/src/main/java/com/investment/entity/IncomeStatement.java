package com.investment.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Entity: Income Statement (Báo cáo kết quả kinh doanh)
 * 
 * Lưu trữ dữ liệu báo cáo KQKD của các công ty.
 */
@Entity
@Table(name = "income_statements", indexes = {
        @Index(name = "idx_is_symbol", columnList = "symbol"),
        @Index(name = "idx_is_date", columnList = "reportDate")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IncomeStatement {

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

    // ===== DOANH THU =====
    @Column(precision = 20, scale = 2)
    private BigDecimal revenue; // Doanh thu thuần

    @Column(precision = 20, scale = 2)
    private BigDecimal costOfGoodsSold; // Giá vốn hàng bán

    @Column(precision = 20, scale = 2)
    private BigDecimal grossProfit; // Lợi nhuận gộp

    // ===== CHI PHÍ =====
    @Column(precision = 20, scale = 2)
    private BigDecimal sellingExpenses; // Chi phí bán hàng

    @Column(precision = 20, scale = 2)
    private BigDecimal adminExpenses; // Chi phí quản lý

    @Column(precision = 20, scale = 2)
    private BigDecimal operatingExpenses; // Chi phí hoạt động

    // ===== LỢI NHUẬN =====
    @Column(precision = 20, scale = 2)
    private BigDecimal operatingProfit; // Lợi nhuận từ HĐKD

    @Column(precision = 20, scale = 2)
    private BigDecimal financialIncome; // Thu nhập tài chính

    @Column(precision = 20, scale = 2)
    private BigDecimal financialExpenses; // Chi phí tài chính

    @Column(precision = 20, scale = 2)
    private BigDecimal interestExpenses; // Chi phí lãi vay

    @Column(precision = 20, scale = 2)
    private BigDecimal profitBeforeTax; // Lợi nhuận trước thuế

    @Column(precision = 20, scale = 2)
    private BigDecimal incomeTax; // Thuế TNDN

    @Column(precision = 20, scale = 2)
    private BigDecimal netIncome; // Lợi nhuận sau thuế

    @Column(precision = 20, scale = 2)
    private BigDecimal netIncomeParent; // LNST của cổ đông công ty mẹ

    // ===== CHỈ SỐ TRÊN CỔ PHIẾU =====
    @Column(precision = 15, scale = 2)
    private BigDecimal eps; // Lãi cơ bản trên cổ phiếu

    @Column(precision = 15, scale = 2)
    private BigDecimal dilutedEps; // EPS pha loãng

    // Metadata
    @Column(name = "created_at")
    private LocalDate createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
    }
}
