package com.investment.controller;

import com.investment.service.CsvImportService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST Controller: Admin API
 * 
 * Các endpoint quản trị: import data, health check...
 */
@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final CsvImportService csvImportService;

    /**
     * Import dữ liệu từ CSV
     * POST /api/admin/import?path=../financial-etl-pipeline/output
     */
    @PostMapping("/import")
    public ResponseEntity<Map<String, Object>> importCsv(
            @RequestParam(value = "path", defaultValue = "../financial-etl-pipeline/output") String path) {
        Map<String, Object> result = csvImportService.importFromDirectory(path);
        return ResponseEntity.ok(result);
    }

    /**
     * Health check
     * GET /api/admin/health
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "Investment Support API"));
    }
}
