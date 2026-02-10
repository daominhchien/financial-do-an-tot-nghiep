package com.investment.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;

/**
 * Entity: Stock (Thông tin cổ phiếu)
 * 
 * Lưu trữ thông tin cơ bản của các mã cổ phiếu.
 */
@Entity
@Table(name = "stocks")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Stock {

    @Id
    @Column(length = 10)
    private String symbol; // Mã cổ phiếu (VNM, FPT...)

    @Column(length = 255)
    private String companyName; // Tên công ty

    @Column(length = 500)
    private String companyNameEn; // Tên tiếng Anh

    @Column(length = 20)
    private String exchange; // Sàn (HOSE, HNX, UPCOM)

    @Column(length = 100)
    private String industry; // Ngành

    @Column(length = 100)
    private String sector; // Lĩnh vực

    @Column(length = 1000)
    private String description; // Mô tả ngắn

    @Column(name = "listing_date")
    private LocalDate listingDate; // Ngày niêm yết

    @Column(name = "created_at")
    private LocalDate createdAt;

    @Column(name = "updated_at")
    private LocalDate updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDate.now();
        updatedAt = LocalDate.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDate.now();
    }
}
