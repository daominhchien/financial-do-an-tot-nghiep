import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import StockList from './pages/StockList'
import StockDetail from './pages/StockDetail'
import Compare from './pages/Compare'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="stocks" element={<StockList />} />
                    <Route path="stocks/:symbol" element={<StockDetail />} />
                    <Route path="compare" element={<Compare />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
