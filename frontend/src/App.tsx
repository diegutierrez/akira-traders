import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/layout/MainLayout'
import { Dashboard } from './pages/Dashboard'
import { Traders } from './pages/Traders'
import { TraderDetail } from './pages/TraderDetail'
import { NewEvaluation } from './pages/NewEvaluation'
import { Analytics } from './pages/Analytics'
import { Login } from './pages/Login'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

function App() {
  return (
    <Routes>
      {/* Ruta pública */}
      <Route path="/login" element={<Login />} />

      {/* Rutas protegidas */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="traders" element={<Traders />} />
        <Route path="traders/:id" element={<TraderDetail />} />
        <Route path="evaluations/new" element={<NewEvaluation />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  )
}

export default App
