package com.investment.service;

import com.investment.entity.*;
import com.investment.repository.*;
import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.FileReader;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Stream;

/**
 * Service: CSV Import
 * 
 * Import dữ liệu từ CSV files (output của ETL pipeline) vào database.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CsvImportService {

    private final StockRepository stockRepository;
    private final BalanceSheetRepository balanceSheetRepository;
    private final IncomeStatementRepository incomeStatementRepository;
    private final FinancialRatioRepository financialRatioRepository;

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    /**
     * Import tất cả dữ liệu từ thư mục output của ETL pipeline
     * 
     * @param outputDir Đường dẫn đến thư mục output (VD:
     *                  ../financial-etl-pipeline/output)
     */
    @Transactional
    public Map<String, Object> importFromDirectory(String outputDir) {
        log.info("🔄 Starting CSV import from: {}", outputDir);

        Map<String, Object> result = new HashMap<>();
        int stocksImported = 0;
        int balanceSheetsImported = 0;
        int incomeStatementsImported = 0;
        int ratiosImported = 0;
        List<String> errors = new ArrayList<>();

        Path basePath = Paths.get(outputDir);

        // Import dữ liệu combined
        Path combinedPath = basePath.resolve("combined");
        if (Files.exists(combinedPath)) {
            try {
                // Import balance sheets
                Path bsPath = combinedPath.resolve("all_balance_sheets.csv");
                if (Files.exists(bsPath)) {
                    balanceSheetsImported = importBalanceSheets(bsPath.toString());
                    log.info("✅ Imported {} balance sheets", balanceSheetsImported);
                }

                // Import income statements
                Path isPath = combinedPath.resolve("all_income_statements.csv");
                if (Files.exists(isPath)) {
                    incomeStatementsImported = importIncomeStatements(isPath.toString());
                    log.info("✅ Imported {} income statements", incomeStatementsImported);
                }

                // Import ratios (filename có thêm chữ 's')
                Path ratiosPath = combinedPath.resolve("all_ratioss.csv");
                if (!Files.exists(ratiosPath)) {
                    ratiosPath = combinedPath.resolve("all_ratios.csv");
                }
                if (Files.exists(ratiosPath)) {
                    ratiosImported = importRatios(ratiosPath.toString());
                    log.info("✅ Imported {} financial ratios", ratiosImported);
                }

            } catch (Exception e) {
                log.error("❌ Error importing combined files: {}", e.getMessage());
                errors.add(e.getMessage());
            }
        }

        // Lấy danh sách symbols từ các thư mục con
        try (Stream<Path> directories = Files.list(basePath)) {
            directories
                    .filter(Files::isDirectory)
                    .filter(p -> !p.getFileName().toString().equals("combined"))
                    .filter(p -> !p.getFileName().toString().equals("logs"))
                    .forEach(symbolPath -> {
                        String symbol = symbolPath.getFileName().toString().toUpperCase();
                        // Tạo stock entry nếu chưa có
                        if (!stockRepository.existsById(symbol)) {
                            Stock stock = Stock.builder()
                                    .symbol(symbol)
                                    .companyName(symbol) // Sẽ update sau
                                    .exchange("HOSE")
                                    .build();
                            stockRepository.save(stock);
                        }
                    });
            stocksImported = (int) stockRepository.count();
        } catch (IOException e) {
            log.error("❌ Error reading directories: {}", e.getMessage());
            errors.add(e.getMessage());
        }

        result.put("stocksImported", stocksImported);
        result.put("balanceSheetsImported", balanceSheetsImported);
        result.put("incomeStatementsImported", incomeStatementsImported);
        result.put("ratiosImported", ratiosImported);
        result.put("errors", errors);
        result.put("success", errors.isEmpty());

        log.info("🎉 Import completed! Stocks: {}, BS: {}, IS: {}, Ratios: {}",
                stocksImported, balanceSheetsImported, incomeStatementsImported, ratiosImported);

        return result;
    }

    /**
     * Import Balance Sheets từ CSV
     * Headers: cp, năm, kỳ, tổng_cộng_tài_sản_đồng, nợ_phải_trả_đồng,
     * vốn_chủ_sở_hữu_đồng, ...
     */
    private int importBalanceSheets(String filePath) throws IOException, CsvException {
        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            List<String[]> rows = reader.readAll();
            if (rows.isEmpty())
                return 0;

            String[] headers = rows.get(0);
            Map<String, Integer> headerMap = createHeaderMap(headers);
            log.info("📊 Balance Sheet headers: {}", headerMap.keySet());

            int count = 0;
            for (int i = 1; i < rows.size(); i++) {
                String[] row = rows.get(i);
                if (row.length < 3)
                    continue;
                try {
                    String symbol = getValueByIndex(row, 0); // cp
                    if (symbol == null || symbol.isEmpty())
                        continue;

                    Integer year = getIntFromString(getValueByIndex(row, 1)); // năm
                    Integer period = getIntFromString(getValueByIndex(row, 2)); // kỳ
                    String periodStr = period != null ? "Q" + period : null;

                    BalanceSheet bs = BalanceSheet.builder()
                            .symbol(symbol)
                            .yearReport(year)
                            .period(periodStr)
                            .reportDate(buildDate(year, periodStr))
                            .totalAssets(getBigDecimalByHeader(row, headerMap, "tổng_cộng_tài_sản_đồng"))
                            .totalLiabilities(getBigDecimalByHeader(row, headerMap, "nợ_phải_trả_đồng"))
                            .totalEquity(getBigDecimalByHeader(row, headerMap, "vốn_chủ_sở_hữu_đồng"))
                            .cash(getBigDecimalByHeader(row, headerMap, "tiền_và_tương_đương_tiền_đồng"))
                            .inventory(getBigDecimalByHeader(row, headerMap, "hàng_tồn_kho_ròng_đồng"))
                            .fixedAssets(getBigDecimalByHeader(row, headerMap, "tài_sản_cố_định_đồng"))
                            .currentAssets(getBigDecimalByHeader(row, headerMap, "tài_sản_ngắn_hạn_đồng"))
                            .nonCurrentAssets(getBigDecimalByHeader(row, headerMap, "tài_sản_dài_hạn_đồng"))
                            .currentLiabilities(getBigDecimalByHeader(row, headerMap, "nợ_ngắn_hạn_đồng"))
                            .nonCurrentLiabilities(getBigDecimalByHeader(row, headerMap, "nợ_dài_hạn_đồng"))
                            .shortTermDebt(
                                    getBigDecimalByHeader(row, headerMap, "vay_và_nợ_thuê_tài_chính_ngắn_hạn_đồng"))
                            .longTermDebt(
                                    getBigDecimalByHeader(row, headerMap, "vay_và_nợ_thuê_tài_chính_dài_hạn_đồng"))
                            .shortTermInvestments(
                                    getBigDecimalByHeader(row, headerMap, "giá_trị_thuần_đầu_tư_ngắn_hạn_đồng"))
                            .longTermInvestments(getBigDecimalByHeader(row, headerMap, "đầu_tư_dài_hạn_đồng"))
                            .receivables(getBigDecimalByHeader(row, headerMap, "các_khoản_phải_thu_ngắn_hạn_đồng"))
                            .retainedEarnings(getBigDecimalByHeader(row, headerMap, "lãi_chưa_phân_phối_đồng"))
                            .charterCapital(getBigDecimalByHeader(row, headerMap, "vốn_góp_của_chủ_sở_hữu_đồng"))
                            .build();

                    balanceSheetRepository.save(bs);
                    count++;
                } catch (Exception e) {
                    log.warn("Skip BS row {}: {}", i, e.getMessage());
                }
            }
            return count;
        }
    }

    /**
     * Import Income Statements từ CSV
     * Headers: cp, năm, kỳ, doanh_thu_đồng, giá_vốn_hàng_bán, lãi_gộp, ...
     */
    private int importIncomeStatements(String filePath) throws IOException, CsvException {
        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            List<String[]> rows = reader.readAll();
            if (rows.isEmpty())
                return 0;

            String[] headers = rows.get(0);
            Map<String, Integer> headerMap = createHeaderMap(headers);
            log.info("📊 Income Statement headers: {}", headerMap.keySet());

            int count = 0;
            for (int i = 1; i < rows.size(); i++) {
                String[] row = rows.get(i);
                if (row.length < 3)
                    continue;
                try {
                    String symbol = getValueByIndex(row, 0); // cp
                    if (symbol == null || symbol.isEmpty())
                        continue;

                    Integer year = getIntFromString(getValueByIndex(row, 1)); // năm
                    Integer period = getIntFromString(getValueByIndex(row, 2)); // kỳ
                    String periodStr = period != null ? "Q" + period : null;

                    IncomeStatement is = IncomeStatement.builder()
                            .symbol(symbol)
                            .yearReport(year)
                            .period(periodStr)
                            .reportDate(buildDate(year, periodStr))
                            .revenue(getBigDecimalByHeader(row, headerMap, "doanh_thu_đồng"))
                            .costOfGoodsSold(getBigDecimalByHeader(row, headerMap, "giá_vốn_hàng_bán"))
                            .grossProfit(getBigDecimalByHeader(row, headerMap, "lãi_gộp"))
                            .operatingProfit(getBigDecimalByHeader(row, headerMap, "lãi_lỗ_từ_hoạt_động_kinh_doanh"))
                            .profitBeforeTax(getBigDecimalByHeader(row, headerMap, "ln_trước_thuế"))
                            .netIncome(getBigDecimalByHeader(row, headerMap, "lợi_nhuận_thuần"))
                            .netIncomeParent(getBigDecimalByHeader(row, headerMap,
                                    "lợi_nhuận_sau_thuế_của_cổ_đông_công_ty_mẹ_đồng"))
                            .financialIncome(getBigDecimalByHeader(row, headerMap, "thu_nhập_tài_chính"))
                            .financialExpenses(getBigDecimalByHeader(row, headerMap, "chi_phí_tài_chính"))
                            .interestExpenses(getBigDecimalByHeader(row, headerMap, "chi_phí_tiền_lãi_vay"))
                            .sellingExpenses(getBigDecimalByHeader(row, headerMap, "chi_phí_bán_hàng"))
                            .adminExpenses(getBigDecimalByHeader(row, headerMap, "chi_phí_quản_lý_dn"))
                            .incomeTax(getBigDecimalByHeader(row, headerMap, "chi_phí_thuế_tndn_hiện_hành"))
                            .build();

                    incomeStatementRepository.save(is);
                    count++;
                } catch (Exception e) {
                    log.warn("Skip IS row {}: {}", i, e.getMessage());
                }
            }
            return count;
        }
    }

    /**
     * Import Financial Ratios từ CSV
     * 
     * File ratios có cấu trúc đặc biệt:
     * - Row 0: Category headers (Meta, Chỉ tiêu cơ cấu nguồn vốn, ...)
     * - Row 1: Column names (CP, Năm, Kỳ, ROE (%), P/E, ...)
     * - Row 2+: Data
     */
    private int importRatios(String filePath) throws IOException, CsvException {
        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            List<String[]> rows = reader.readAll();
            if (rows.size() < 3)
                return 0;

            // Row 1 (index 1) = actual column names
            String[] headers = rows.get(1);
            Map<String, Integer> headerMap = createHeaderMap(headers);

            log.info("📊 Ratios headers: {}", headerMap.keySet());

            int count = 0;
            // Data starts from row 2 (index 2)
            for (int i = 2; i < rows.size(); i++) {
                String[] row = rows.get(i);
                if (row.length < 3)
                    continue;
                try {
                    String symbol = getValueByIndex(row, 0); // CP column
                    if (symbol == null || symbol.isEmpty())
                        continue;

                    Integer year = getIntFromString(getValueByIndex(row, 1)); // Năm
                    Integer period = getIntFromString(getValueByIndex(row, 2)); // Kỳ
                    String periodStr = period != null ? "Q" + period : null;

                    FinancialRatio fr = FinancialRatio.builder()
                            .symbol(symbol)
                            .yearReport(year)
                            .period(periodStr)
                            .reportDate(buildDate(year, periodStr))
                            .debtToEquity(getBigDecimalByHeader(row, headerMap, "Nợ/VCSH"))
                            .grossMargin(getBigDecimalByHeader(row, headerMap, "Biên lợi nhuận gộp (%)"))
                            .netMargin(getBigDecimalByHeader(row, headerMap, "Biên lợi nhuận ròng (%)"))
                            .roe(getBigDecimalByHeader(row, headerMap, "ROE (%)"))
                            .roa(getBigDecimalByHeader(row, headerMap, "ROA (%)"))
                            .assetTurnover(getBigDecimalByHeader(row, headerMap, "Vòng quay tài sản"))
                            .inventoryTurnover(getBigDecimalByHeader(row, headerMap, "Vòng quay hàng tồn kho"))
                            .currentRatio(getBigDecimalByHeader(row, headerMap, "Chỉ số thanh toán hiện thời"))
                            .quickRatio(getBigDecimalByHeader(row, headerMap, "Chỉ số thanh toán nhanh"))
                            .cashRatio(getBigDecimalByHeader(row, headerMap, "Chỉ số thanh toán tiền mặt"))
                            .dividendYield(getBigDecimalByHeader(row, headerMap, "Tỷ suất cổ tức (%)"))
                            .pe(getBigDecimalByHeader(row, headerMap, "P/E"))
                            .pb(getBigDecimalByHeader(row, headerMap, "P/B"))
                            .ps(getBigDecimalByHeader(row, headerMap, "P/S"))
                            .interestCoverage(getBigDecimalByHeader(row, headerMap, "Khả năng chi trả lãi vay"))
                            .build();

                    financialRatioRepository.save(fr);
                    count++;
                } catch (Exception e) {
                    log.warn("Skip ratios row {}: {}", i, e.getMessage());
                }
            }
            return count;
        }
    }

    // ===== HELPER METHODS =====

    private Map<String, Integer> createHeaderMap(String[] headers) {
        Map<String, Integer> map = new HashMap<>();
        for (int i = 0; i < headers.length; i++) {
            map.put(headers[i].trim(), i);
        }
        return map;
    }

    private String getStringValue(String[] row, Map<String, Integer> headerMap, String... keys) {
        for (String key : keys) {
            Integer idx = headerMap.get(key);
            if (idx != null && idx < row.length && !row[idx].isEmpty()) {
                return row[idx].trim();
            }
        }
        return null;
    }

    private Integer getIntValue(String[] row, Map<String, Integer> headerMap, String key) {
        String val = getStringValue(row, headerMap, key);
        if (val != null && !val.isEmpty()) {
            try {
                return Integer.parseInt(val.split("\\.")[0]); // Handle "2024.0"
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    private BigDecimal getBigDecimalValue(String[] row, Map<String, Integer> headerMap, String... keys) {
        String val = getStringValue(row, headerMap, keys);
        if (val != null && !val.isEmpty()) {
            try {
                return new BigDecimal(val.replace(",", ""));
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    private LocalDate getDateValue(String[] row, Map<String, Integer> headerMap, String yearKey, String periodKey) {
        Integer year = getIntValue(row, headerMap, yearKey);
        String period = getStringValue(row, headerMap, periodKey);

        if (year == null)
            return null;

        // Xác định tháng từ period (Q1, Q2, Q3, Q4)
        int month = 12; // Default cuối năm
        if (period != null) {
            switch (period.toUpperCase()) {
                case "Q1" -> month = 3;
                case "Q2" -> month = 6;
                case "Q3" -> month = 9;
                case "Q4" -> month = 12;
            }
        }

        return LocalDate.of(year, month, 1);
    }

    private String getValueByIndex(String[] row, int index) {
        if (index < row.length && row[index] != null && !row[index].trim().isEmpty()) {
            return row[index].trim();
        }
        return null;
    }

    private Integer getIntFromString(String val) {
        if (val == null || val.isEmpty())
            return null;
        try {
            return Integer.parseInt(val.split("\\.")[0]);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private BigDecimal getBigDecimalByHeader(String[] row, Map<String, Integer> headerMap, String headerName) {
        Integer idx = headerMap.get(headerName);
        if (idx != null && idx < row.length && row[idx] != null && !row[idx].trim().isEmpty()) {
            try {
                return new BigDecimal(row[idx].trim().replace(",", ""));
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    private LocalDate buildDate(Integer year, String period) {
        if (year == null)
            return null;
        int month = 12;
        if (period != null) {
            switch (period.toUpperCase()) {
                case "Q1" -> month = 3;
                case "Q2" -> month = 6;
                case "Q3" -> month = 9;
                case "Q4" -> month = 12;
            }
        }
        return LocalDate.of(year, month, 1);
    }
}
