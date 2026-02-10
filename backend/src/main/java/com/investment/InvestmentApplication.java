package com.investment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Investment Support API - Main Application
 * 
 * Ứng dụng hỗ trợ đầu tư cho người phân tích cơ bản.
 * Cung cấp API để truy vấn dữ liệu báo cáo tài chính, 
 * chỉ số tài chính và so sánh cổ phiếu.
 * 
 * @author Đồ án tốt nghiệp
 */
@SpringBootApplication
public class InvestmentApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(InvestmentApplication.class, args);
        System.out.println("\n" +
            "╔══════════════════════════════════════════════════════════╗\n" +
            "║     🚀 INVESTMENT SUPPORT API STARTED                    ║\n" +
            "╠══════════════════════════════════════════════════════════╣\n" +
            "║  API:        http://localhost:8080/api                   ║\n" +
            "║  H2 Console: http://localhost:8080/h2-console            ║\n" +
            "║  Swagger:    http://localhost:8080/swagger-ui            ║\n" +
            "╚══════════════════════════════════════════════════════════╝\n"
        );
    }
}
