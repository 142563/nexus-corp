// pages/DashboardPage.jsx — Dashboard ejecutivo con KPIs y gráfico de tendencias.
import React, { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar } from 'recharts'
import api from '../services/api'

function KPICard({ title, value, subtitle, color }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border-l-4 p-5 ${color}`}>
      <div className="text-xs text-gray-500 uppercase tracking-wider">{title}</div>
      <div className="text-3xl font-bold text-gray-800 mt-1">{value}</div>
      {subtitle && <div className="text-xs text-gray-400 mt-1">{subtitle}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const [kpis, setKpis] = useState(null)
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/api/v1/kpis/dashboard'),
      api.get('/api/v1/kpis/trends?days=14'),
    ]).then(([kpiRes, trendRes]) => {
      setKpis(kpiRes.data)
      setTrends(trendRes.data.trends)
    }).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-gray-400">Cargando KPIs...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Dashboard Ejecutivo</h1>
      <p className="text-gray-500 text-sm mb-6">DistribLog S.A. — Sistema Nexus-Corp</p>

      {kpis && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KPICard title="Total Decisiones" value={kpis.total_decisions} color="border-blue-500" />
          <KPICard title="Tasa de Aceptación" value={`${kpis.acceptance_rate}%`} subtitle="de recomendaciones" color="border-green-500" />
          <KPICard title="Reglas Activas" value={kpis.active_rules_count} subtitle={`${kpis.rules_in_review} en revisión`} color="border-yellow-500" />
          <KPICard title="Calificación Promedio" value={kpis.average_feedback_rating > 0 ? kpis.average_feedback_rating.toFixed(1) : 'N/A'} subtitle="sobre 5" color="border-purple-500" />
          <KPICard title="Decisiones (7 días)" value={kpis.decisions_last_7_days} color="border-indigo-500" />
          <KPICard title="En Revisión" value={kpis.rules_in_review} subtitle="reglas pausadas" color="border-orange-500" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Decisiones por día (últimos 14 días)</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} />
              <YAxis allowDecimals={false} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="decisions" fill="#3b82f6" radius={[3,3,0,0]} />
              <Bar dataKey="accepted" fill="#22c55e" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-500 inline-block"></span>Evaluadas</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500 inline-block"></span>Aceptadas</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Confianza promedio por día</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 10 }} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
              <Tooltip formatter={v => `${(v*100).toFixed(1)}%`} />
              <Line type="monotone" dataKey="avg_confidence" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
