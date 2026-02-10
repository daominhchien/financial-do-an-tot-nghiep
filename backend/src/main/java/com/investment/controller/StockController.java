package com.investment.controller;

import com.investment.entity.*;
import com.investment.service.StockService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller: Stock API
 * 
 * Cung cấp các endpoint để truy vấn dữ liệu cổ phiếu và báo cáo tài chính.
 */
@RestController
@RequestMapping("/api/stocks")
@RequiredArgsConstructor
@CrossOrigin(origins = { "http://localhost:5173", "http://localhost:3000" })
public class StockController {

    private final StockService stockService;

    // ===== STOCK ENDPOINTS =====

    /**
     * Lấy danh sách tất cả cổ phiếu
     * GET /api/stocks
     */
    @GetMapping
    public ResponseEntity<List<Stock>> getAllStocks() {
        return ResponseEntity.ok(stockService.getAllStocks());
    }

    /**
     * Lấy thông tin chi tiết 1 cổ phiếu
     * GET /api/stocks/{symbol}
     */
    @GetMapping("/{symbol}")
    public ResponseEntity<?> getStock(@PathVariable String symbol) {
        return stockService.getStockBySymbol(symbol)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Tìm kiếm cổ phiếu theo keyword
     * GET /api/stocks/search?q=keyword
     */
    @GetMapping("/search")
    public ResponseEntity<List<Stock>> searchStocks(@RequestParam("q") String keyword) {
        return ResponseEntity.ok(stockService.searchStocks(keyword));
    }

    /**
     * Lấy cổ phiếu theo sàn
     * GET /api/stocks/exchange/{exchange}
     */
    @GetMapping("/exchange/{exchange}")
    public ResponseEntity<List<Stock>> getStocksByExchange(@PathVariable String exchange) {
        return ResponseEntity.ok(stockService.getStocksByExchange(exchange));
    }

    /**
     * Lấy danh sách các ngành
     * GET /api/stocks/industries
     */
    @GetMapping("/industries")
    public ResponseEntity<List<String>> getIndustries() {
        return ResponseEntity.ok(stockService.getAllIndustries());
    }

    // ===== FINANCIAL DATA ENDPOINTS =====

    /**
     * Lấy bảng cân đối kế toán
     * GET /api/stocks/{symbol}/balance-sheet
     */
    @GetMapping("/{symbol}/balance-sheet")
    public ResponseEntity<List<BalanceSheet>> getBalanceSheets(@PathVariable String symbol) {
        return ResponseEntity.ok(stockService.getBalanceSheets(symbol));
    }

    /**
     * Lấy báo cáo KQKD
     * GET /api/stocks/{symbol}/income-statement
     */
    @GetMapping("/{symbol}/income-statement")
    public ResponseEntity<List<IncomeStatement>> getIncomeStatements(@PathVariable String symbol) {
        return ResponseEntity.ok(stockService.getIncomeStatements(symbol));
    }

    /**
     * Lấy chỉ số tài chính
     * GET /api/stocks/{symbol}/ratios
     */
    @GetMapping("/{symbol}/ratios")
    public ResponseEntity<List<FinancialRatio>> getFinancialRatios(@PathVariable String symbol) {
        return ResponseEntity.ok(stockService.getFinancialRatios(symbol));
    }

    /**
     * Lấy tổng quan tài chính mới nhất
     * GET /api/stocks/{symbol}/overview
     */
    @GetMapping("/{symbol}/overview")
    public ResponseEntity<Map<String, Object>> getStockOverview(@PathVariable String symbol) {
        var stock = stockService.getStockBySymbol(symbol);
        if (stock.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok(Map.of(
                "stock", stock.get(),
                "latestBalanceSheet", stockService.getLatestBalanceSheet(symbol),
                "latestIncomeStatement", stockService.getLatestIncomeStatement(symbol),
                "latestRatios", stockService.getLatestFinancialRatio(symbol)));
    }

    // ===== COMPARISON ENDPOINT =====

    /**
     * So sánh nhiều cổ phiếu
     * GET /api/stocks/compare?symbols=VNM,FPT,VIC
     */
    @GetMapping("/compare")
    public ResponseEntity<List<FinancialRatio>> compareStocks(
            @RequestParam("symbols") List<String> symbols) {
        return ResponseEntity.ok(stockService.compareStocks(symbols));
    }
}
