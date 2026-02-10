import { useQuery } from '@tanstack/react-query'
import { compareStocks } from '../services/api'
import { useState } from 'react'
import { GitCompare, Plus, X, Search } from 'lucide-react'

export default function Compare() {
    const [symbols, setSymbols] = useState(['VNM', 'FPT'])
    const [inputValue, setInputValue] = useState('')

    const { data: comparison, isLoading, refetch } = useQuery({
        queryKey: ['compare', symbols],
        queryFn: () => compareStocks(symbols),
        enabled: symbols.length > 0,
    })

    const addSymbol = () => {
        if (inputValue && !symbols.includes(inputValue.toUpperCase())) {
            setSymbols([...symbols, inputValue.toUpperCase()])
            setInputValue('')
        }
    }

    const removeSymbol = (symbol) => {
        setSymbols(symbols.filter(s => s !== symbol))
    }

    const formatPercent = (val) => {
        if (!val) return 'N/A'
        return (Number(val) * 100).toFixed(2) + '%'
    }

    // Danh sách mã gợi ý
    const suggestedSymbols = ['VIC', 'HPG', 'VCB', 'TCB', 'MWG', 'MSN']

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
                    <GitCompare className="w-7 h-7 text-primary-600" />
                    So sánh cổ phiếu
                </h1>
                <p className="text-slate-500 mt-1">So sánh chỉ số tài chính giữa các mã</p>
            </div>

            {/* Symbol selector */}
            <div className="card">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Chọn mã cổ phiếu</h3>

                {/* Selected symbols */}
                <div className="flex flex-wrap gap-2 mb-4">
                    {symbols.map((symbol) => (
                        <div
                            key={symbol}
                            className="flex items-center gap-2 bg-primary-50 text-primary-700 px-3 py-1.5 rounded-full"
                        >
                            <span className="font-medium">{symbol}</span>
                            <button
                                onClick={() => removeSymbol(symbol)}
                                className="hover:bg-primary-100 rounded-full p-0.5"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Add symbol input */}
                <div className="flex gap-2 mb-4">
                    <div className="relative flex-1 max-w-xs">
                        <input
                            type="text"
                            placeholder="Nhập mã (VD: VIC)"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value.toUpperCase())}
                            onKeyDown={(e) => e.key === 'Enter' && addSymbol()}
                            className="w-full pl-4 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                    </div>
                    <button
                        onClick={addSymbol}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Thêm
                    </button>
                </div>

                {/* Suggested symbols */}
                <div className="flex flex-wrap gap-2">
                    <span className="text-sm text-slate-500">Gợi ý:</span>
                    {suggestedSymbols.filter(s => !symbols.includes(s)).map((symbol) => (
                        <button
                            key={symbol}
                            onClick={() => setSymbols([...symbols, symbol])}
                            className="px-3 py-1 text-sm bg-slate-100 text-slate-600 rounded-full hover:bg-slate-200"
                        >
                            {symbol}
                        </button>
                    ))}
                </div>
            </div>

            {/* Comparison table */}
            {symbols.length > 0 && (
                <div className="card">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">Bảng so sánh</h3>

                    {isLoading ? (
                        <div className="text-center py-8 text-slate-400">Đang tải dữ liệu...</div>
                    ) : (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Mã</th>
                                        <th className="text-right">ROE</th>
                                        <th className="text-right">ROA</th>
                                        <th className="text-right">P/E</th>
                                        <th className="text-right">P/B</th>
                                        <th className="text-right">Biên LN gộp</th>
                                        <th className="text-right">D/E</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {comparison?.map((r, i) => (
                                        <tr key={i} className="hover:bg-slate-50">
                                            <td className="font-bold text-primary-600">{r.symbol}</td>
                                            <td className={`text-right ${Number(r.roe) > 0.15 ? 'value-positive' : ''}`}>
                                                {formatPercent(r.roe)}
                                            </td>
                                            <td className="text-right">{formatPercent(r.roa)}</td>
                                            <td className={`text-right ${Number(r.pe) < 15 ? 'value-positive' : ''}`}>
                                                {r.pe?.toFixed(2) || 'N/A'}
                                            </td>
                                            <td className="text-right">{r.pb?.toFixed(2) || 'N/A'}</td>
                                            <td className="text-right">{formatPercent(r.grossMargin)}</td>
                                            <td className={`text-right ${Number(r.debtToEquity) > 2 ? 'value-negative' : ''}`}>
                                                {r.debtToEquity?.toFixed(2) || 'N/A'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {comparison?.length === 0 && (
                        <div className="text-center py-8 text-slate-400">
                            Không có dữ liệu. Hãy import dữ liệu từ ETL pipeline.
                        </div>
                    )}
                </div>
            )}

            {/* Legend */}
            <div className="card bg-slate-50">
                <h4 className="font-semibold text-slate-700 mb-2">📊 Hướng dẫn đọc</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600">
                    <div>
                        <strong>ROE</strong>: Tỷ suất lợi nhuận trên vốn chủ sở hữu. ROE &gt; 15% là tốt.
                    </div>
                    <div>
                        <strong>P/E</strong>: Giá/Lợi nhuận. P/E thấp có thể là cổ phiếu giá trị.
                    </div>
                    <div>
                        <strong>D/E</strong>: Nợ/Vốn chủ sở hữu. D/E &gt; 2 là rủi ro cao.
                    </div>
                </div>
            </div>
        </div>
    )
}
