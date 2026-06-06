// App.jsx — Enrutamiento principal de Nexus-Corp con protección por rol.
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'

import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import EvaluatePage from './pages/EvaluatePage'
import WhatIfPage from './pages/WhatIfPage'
import RulesPage from './pages/RulesPage'
import KnowledgeMapPage from './pages/KnowledgeMapPage'
import HistoryPage from './pages/HistoryPage'
import UsersPage from './pages/UsersPage'

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Cargando...</div>
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return <Layout>{children}</Layout>
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/evaluate" element={
        <ProtectedRoute allowedRoles={['system_admin','decision_maker','knowledge_admin']}>
          <EvaluatePage />
        </ProtectedRoute>
      } />
      <Route path="/whatif" element={
        <ProtectedRoute allowedRoles={['system_admin','analyst','decision_maker','knowledge_admin']}>
          <WhatIfPage />
        </ProtectedRoute>
      } />
      <Route path="/rules" element={
        <ProtectedRoute allowedRoles={['system_admin','knowledge_admin','area_expert']}>
          <RulesPage />
        </ProtectedRoute>
      } />
      <Route path="/knowledge" element={
        <ProtectedRoute allowedRoles={['system_admin','knowledge_admin','analyst']}>
          <KnowledgeMapPage />
        </ProtectedRoute>
      } />
      <Route path="/history" element={
        <ProtectedRoute allowedRoles={['system_admin','decision_maker','analyst','knowledge_admin']}>
          <HistoryPage />
        </ProtectedRoute>
      } />
      <Route path="/users" element={
        <ProtectedRoute allowedRoles={['system_admin']}>
          <UsersPage />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
