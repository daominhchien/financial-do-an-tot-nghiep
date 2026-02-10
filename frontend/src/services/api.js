import axios from 'axios'

// API Base URL - sử dụng proxy từ vite.config.js
const API_BASE = '/api'

const api = axios.create({
    baseURL: API_BASE,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// ===== STOCK API =====

/**
 * Lấy danh sách tất cả cổ phiếu
 */
export const getStocks = async () => {
    const response = await api.get('/stocks')
    return response.data
}

/**
 * Lấy thông tin chi tiết 1 cổ phiếu
 */
export const getStock = async (symbol) => {
    const response = await api.get(`/stocks/${symbol}`)
    return response.data
}

/**
 * Tìm kiếm cổ phiếu
 */
export const searchStocks = async (keyword) => {
    const response = await api.get('/stocks/search', { params: { q: keyword } })
    return response.data
}

/**
 * Lấy tổng quan tài chính của 1 mã
 */
export const getStockOverview = async (symbol) => {
    const response = await api.get(`/stocks/${symbol}/overview`)
    return response.data
}

// ===== FINANCIAL DATA API =====

/**
 * Lấy bảng cân đối kế toán
 */
export const getBalanceSheets = async (symbol) => {
    const response = await api.get(`/stocks/${symbol}/balance-sheet`)
    return response.data
}

/**
 * Lấy báo cáo KQKD
 */
export const getIncomeStatements = async (symbol) => {
    const response = await api.get(`/stocks/${symbol}/income-statement`)
    return response.data
}

/**
 * Lấy chỉ số tài chính
 */
export const getFinancialRatios = async (symbol) => {
    const response = await api.get(`/stocks/${symbol}/ratios`)
    return response.data
}

// ===== COMPARISON API =====

/**
 * So sánh nhiều cổ phiếu
 */
export const compareStocks = async (symbols) => {
    const response = await api.get('/stocks/compare', {
        params: { symbols: symbols.join(',') }
    })
    return response.data
}

// ===== ADMIN API =====

/**
 * Import dữ liệu từ CSV
 */
export const importCsvData = async (path) => {
    const response = await api.post('/admin/import', null, {
        params: { path }
    })
    return response.data
}

export default api
