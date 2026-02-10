import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getStocks } from '../services/api'
import { Search, ArrowUpRight, TrendingUp } from 'lucide-react'
import { useState } from 'react'

export default function StockList() {
    const [searchTerm, setSearchTerm] = useState('')

    const { data: stocks, isLoading, error } = useQuery({
        queryKey: ['stocks'],
        queryFn: getStocks,
    })

    // Filter stocks
    const filteredStocks = stocks?.filter(stock =>
        stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.companyName?.toLowerCase().includes(searchTerm.toLowerCase())
    ) || []

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-slate-400">Đang tải danh sách cổ phiếu...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="card text-center py-8">
                <p className="text-red-500 mb-4">Lỗi kết nối API</p>
                <p className="text-slate-500 text-sm">
                    Đảm bảo backend đang chạy tại http://localhost:8080
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Danh sách cổ phiếu</h1>
                    <p className="text-slate-500 mt-1">{stocks?.length || 0} mã cổ phiếu</p>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Tìm mã CK hoặc tên..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2.5 w-full sm:w-72 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                </div>
            </div>

            {/* Stock grid */}
            {filteredStocks.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filteredStocks.map((stock) => (
                        <Link
                            key={stock.symbol}
                            to={`/stocks/${stock.symbol}`}
                            className="card hover:shadow-md hover:border-primary-200 transition-all group"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center text-white font-bold">
                                        {stock.symbol?.slice(0, 2)}
                                    </div>
                                    <div>
                                        <p className="font-bold text-lg text-slate-800 group-hover:text-primary-600">
                                            {stock.symbol}
                                        </p>
                                        <p className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded mt-1">
                                            {stock.exchange || 'HOSE'}
                                        </p>
                                    </div>
                                </div>
                                <ArrowUpRight className="w-5 h-5 text-slate-300 group-hover:text-primary-500 transition-colors" />
                            </div>

                            <p className="text-sm text-slate-600 mt-3 line-clamp-2">
                                {stock.companyName || stock.symbol}
                            </p>

                            {stock.industry && (
                                <p className="text-xs text-slate-400 mt-2">
                                    {stock.industry}
                                </p>
                            )}
                        </Link>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-12">
                    <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                    <p className="text-slate-500">
                        {searchTerm ? 'Không tìm thấy kết quả' : 'Chưa có dữ liệu cổ phiếu'}
                    </p>
                    <p className="text-sm text-slate-400 mt-2">
                        Chạy API import để thêm dữ liệu từ ETL pipeline
                    </p>
                </div>
            )}
        </div>
    )
}
