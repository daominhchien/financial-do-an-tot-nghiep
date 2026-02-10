import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { getStockOverview, getBalanceSheets, getIncomeStatements, getFinancialRatios } from '../services/api'
import { ArrowLeft, TrendingUp, TrendingDown, Building2, Calendar, BarChart3 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { useState } from 'react'

export default function StockDetail() {
    const { symbol } = useParams()
    const [activeTab, setActiveTab] = useState('overview')

    const { data: overview } = useQuery({
        queryKey: ['stock-overview', symbol],
        queryFn: () => getStockOverview(symbol),
    })

    const { data: balanceSheets } = useQuery({
        queryKey: ['balance-sheets', symbol],
        queryFn: () => getBalanceSheets(symbol),
    })

    const { data: incomeStatements } = useQuery({
        queryKey: ['income-statements', symbol],
        queryFn: () => getIncomeStatements(symbol),
    })

    const { data: ratios } = useQuery({
        queryKey: ['ratios', symbol],
        queryFn: () => getFinancialRatios(symbol),
    })

    const tabs = [
        { id: 'overview', label: 'Tổng quan' },
        { id: 'balance', label: 'Bảng CĐKT' },
        { id: 'income', label: 'KQKD' },
        { id: 'ratios', label: 'Chỉ số' },
    ]

    // Format số tiền (tỷ VND)
    const formatBillion = (val) => {
        if (!val) return 'N/A'
        return (Number(val) / 1e9).toFixed(1) + ' tỷ'
    }

    // Format phần trăm
    const formatPercent = (val) => {
        if (!val) return 'N/A'
        return (Number(val) * 100).toFixed(2) + '%'
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link to="/stocks" className="p-2 hover:bg-slate-100 rounded-lg">
                    <ArrowLeft className="w-5 h-5 text-slate-600" />
                </Link>
                <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white font-bold text-xl">
                        {symbol?.slice(0, 2)}
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">{symbol}</h1>
                        <p className="text-slate-500">{overview?.stock?.companyName || symbol}</p>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-200 pb-2">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id
                                ? 'bg-primary-50 text-primary-700'
                                : 'text-slate-600 hover:bg-slate-50'
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Key metrics */}
                    <div className="card">
                        <h3 className="text-lg font-semibold text-slate-800 mb-4">Chỉ số chính</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {[
                                { label: 'P/E', value: overview?.latestRatios?.pe },
                                { label: 'P/B', value: overview?.latestRatios?.pb },
                                { label: 'ROE', value: formatPercent(overview?.latestRatios?.roe) },
                                { label: 'ROA', value: formatPercent(overview?.latestRatios?.roa) },
                            ].map((item, i) => (
                                <div key={i} className="bg-slate-50 p-4 rounded-lg">
                                    <p className="text-sm text-slate-500">{item.label}</p>
                                    <p className="text-xl font-bold text-slate-800">{item.value || 'N/A'}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Financial highlights */}
                    <div className="card">
                        <h3 className="text-lg font-semibold text-slate-800 mb-4">Tài chính nổi bật</h3>
                        <div className="space-y-3">
                            {[
                                { label: 'Tổng tài sản', value: formatBillion(overview?.latestBalanceSheet?.totalAssets) },
                                { label: 'Vốn chủ sở hữu', value: formatBillion(overview?.latestBalanceSheet?.totalEquity) },
                                { label: 'Doanh thu', value: formatBillion(overview?.latestIncomeStatement?.revenue) },
                                { label: 'Lợi nhuận ròng', value: formatBillion(overview?.latestIncomeStatement?.netIncome) },
                            ].map((item, i) => (
                                <div key={i} className="flex justify-between items-center py-2 border-b border-slate-100">
                                    <span className="text-slate-600">{item.label}</span>
                                    <span className="font-semibold text-slate-800">{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'balance' && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Bảng cân đối kế toán</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Kỳ</th>
                                    <th className="text-right">Tổng TS</th>
                                    <th className="text-right">Nợ phải trả</th>
                                    <th className="text-right">VCSH</th>
                                </tr>
                            </thead>
                            <tbody>
                                {balanceSheets?.slice(0, 8).map((bs, i) => (
                                    <tr key={i} className="hover:bg-slate-50">
                                        <td className="font-medium">{bs.period} {bs.yearReport}</td>
                                        <td className="text-right">{formatBillion(bs.totalAssets)}</td>
                                        <td className="text-right">{formatBillion(bs.totalLiabilities)}</td>
                                        <td className="text-right">{formatBillion(bs.totalEquity)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {activeTab === 'income' && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Kết quả kinh doanh</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Kỳ</th>
                                    <th className="text-right">Doanh thu</th>
                                    <th className="text-right">LN gộp</th>
                                    <th className="text-right">LN ròng</th>
                                </tr>
                            </thead>
                            <tbody>
                                {incomeStatements?.slice(0, 8).map((is, i) => (
                                    <tr key={i} className="hover:bg-slate-50">
                                        <td className="font-medium">{is.period} {is.yearReport}</td>
                                        <td className="text-right">{formatBillion(is.revenue)}</td>
                                        <td className="text-right">{formatBillion(is.grossProfit)}</td>
                                        <td className={`text-right ${Number(is.netIncome) >= 0 ? 'value-positive' : 'value-negative'}`}>
                                            {formatBillion(is.netIncome)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {activeTab === 'ratios' && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Chỉ số tài chính</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Kỳ</th>
                                    <th className="text-right">ROE</th>
                                    <th className="text-right">ROA</th>
                                    <th className="text-right">P/E</th>
                                    <th className="text-right">P/B</th>
                                    <th className="text-right">D/E</th>
                                </tr>
                            </thead>
                            <tbody>
                                {ratios?.slice(0, 8).map((r, i) => (
                                    <tr key={i} className="hover:bg-slate-50">
                                        <td className="font-medium">{r.period} {r.yearReport}</td>
                                        <td className="text-right">{formatPercent(r.roe)}</td>
                                        <td className="text-right">{formatPercent(r.roa)}</td>
                                        <td className="text-right">{r.pe?.toFixed(2) || 'N/A'}</td>
                                        <td className="text-right">{r.pb?.toFixed(2) || 'N/A'}</td>
                                        <td className="text-right">{r.debtToEquity?.toFixed(2) || 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
