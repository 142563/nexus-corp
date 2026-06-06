// pages/HistoryPage.jsx — Historial de decisiones con filtros.
import React, { useEffect, useState } from 'react'
import api from '../services/api'

const OUTCOME_COLORS = {
  aceptada:               'bg-green-100 text-green-700',
  rechazada:              'bg-red-100 text-red-700',
  parcialmente_aceptada:  'bg-yellow-100 text-yellow-700',
}

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    api.get('/api/v1/decisions/history')
      .then(r => setHistory(r.data))
      .finally(() => setLoading(false))
  }, [])

  const filtered = filter
    ? history.filter(h => h.request_type?.includes(filter) || h.outcome?.includes(filter))
    : history

  if (loading) return <div className="text-center py-20 text-gray-400">Cargando historial...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Historial de Decisiones</h1>
      <p className="text-gray-500 text-sm mb-6">Registro completo de evaluaciones realizadas en Nexus-Corp.</p>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Filtrar por tipo o resultado..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">ID</th>
              <th className="px-4 py-3 text-left">Fecha</th>
              <th className="px-4 py-3 text-left">Tipo</th>
              <th className="px-4 py-3 text-left">Acción Sugerida</th>
              <th className="px-4 py-3 text-center">Confianza</th>
              <th className="px-4 py-3 text-center">Riesgo</th>
              <th className="px-4 py-3 text-center">Resultado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">No hay registros.</td></tr>
            )}
            {filtered.map(h => (
              <tr key={h.request_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-400 text-xs">#{h.request_id}</td>
                <td className="px-4 py-3 text-gray-600 text-xs">
                  {h.requested_at ? new Date(h.requested_at).toLocaleString('es-GT') : '—'}
                </td>
                <td className="px-4 py-3 text-gray-700">{h.request_type}</td>
                <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{h.suggested_action || '—'}</td>
                <td className="px-4 py-3 text-center">
                  {h.confidence != null ? `${(h.confidence * 100).toFixed(0)}%` : '—'}
                </td>
                <td className="px-4 py-3 text-center text-xs capitalize text-gray-600">{h.estimated_risk || '—'}</td>
                <td className="px-4 py-3 text-center">
                  {h.outcome ? (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${OUTCOME_COLORS[h.outcome] || 'bg-gray-100 text-gray-600'}`}>
                      {h.outcome}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-300">pendiente</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
