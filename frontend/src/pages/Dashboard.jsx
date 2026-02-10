import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getStocks, getFinancialRatios } from '../services/api'
import { TrendingUp, TrendingDown, Building2, BarChart3, ArrowRight } from 'lucide-react'

export default function Dashboard() {
    const { data: stocks, isLoading: stocksLoading } = useQuery({
        queryKey: ['stocks'],
        queryFn: getStocks,
    })

    // Thống kê tổng quan
    const stats = [
        {
            label: 'Tổng cổ phiếu',
            value: stocks?.length || 0,
            icon: Building2,
            color: 'bg-blue-500'
        },
        {
            label: 'VN30',
            value: 30,
            icon: BarChart3,
            color: 'bg-emerald-500'
        },
        {
            label: 'Ngân hàng',
            value: 15,
            icon: Building2,
            color: 'bg-purple-500'
        },
        {
            label: 'Blue Chips',
            value: 10,
            icon: TrendingUp,
            color: 'bg-orange-500'
        },
    ]

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
                <p className="text-slate-500 mt-1">Tổng quan thị trường và dữ liệu phân tích</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat, i) => (
                    <div key={i} className="card flex items-center gap-4">
                        <div className={`p-3 rounded-lg ${stat.color}`}>
                            <stat.icon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
                            <p className="text-sm text-slate-500">{stat.label}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick access */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top stocks */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-slate-800">Cổ phiếu phổ biến</h2>
                        <Link to="/stocks" className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1">
                            Xem tất cả <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>

                    {stocksLoading ? (
                        <div className="text-center py-8 text-slate-400">Đang tải...</div>
                    ) : (
                        <div className="space-y-3">
                            {(stocks?.slice(0, 5) || []).map((stock) => (
                                <Link
                                    key={stock.symbol}
                                    to={`/stocks/${stock.symbol}`}
                                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                                            {stock.symbol?.slice(0, 2)}
                                        </div>
                                        <div>
                                            <p className="font-medium text-slate-800">{stock.symbol}</p>
                                            <p className="text-sm text-slate-500 truncate max-w-[200px]">
                                                {stock.companyName || stock.symbol}
                                            </p>
                                        </div>
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-slate-400" />
                                </Link>
                            ))}

                            {(!stocks || stocks.length === 0) && (
                                <div className="text-center py-8 text-slate-400">
                                    <p>Chưa có dữ liệu</p>
                                    <p className="text-sm mt-1">Chạy import để thêm dữ liệu</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Quick compare */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-slate-800">So sánh nhanh</h2>
                        <Link to="/compare" className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1">
                            So sánh chi tiết <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                        {['VNM', 'FPT', 'VIC', 'HPG', 'VCB', 'TCB'].map((symbol) => (
                            <Link
                                key={symbol}
                                to={`/stocks/${symbol}`}
                                className="p-4 bg-slate-50 rounded-lg text-center hover:bg-slate-100 transition-colors"
                            >
                                <p className="font-bold text-primary-600">{symbol}</p>
                            </Link>
                        ))}
                    </div>

                    <div className="mt-4 p-4 bg-primary-50 rounded-lg">
                        <p className="text-sm text-primary-700">
                            💡 <strong>Tip:</strong> Sử dụng trang So sánh để phân tích nhiều mã cùng lúc
                        </p>
                    </div>
                </div>
            </div>

            {/* Info banner */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">🎓 Đồ án tốt nghiệp</h3>
                <p className="text-primary-100">
                    Ứng dụng hỗ trợ đầu tư - Phân tích cơ bản cổ phiếu Việt Nam.
                    Sử dụng dữ liệu từ vnstock để phân tích các chỉ số tài chính.
                </p>
            </div>
        </div>
    )
}
