import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Home } from './pages/Home'
import { RunDetail } from './pages/RunDetail'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/runs/:runId" element={<RunDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
