// pages/EvaluatePage.jsx — Formulario para evaluar una situación logística.
import React, { useState } from 'react'
import api from '../services/api'

const FIELDS = [
  { key: 'order_priority',             label: 'Prioridad del pedido',                type: 'select', options: ['alta','media','baja'] },
  { key: 'delay_minutes',              label: 'Minutos de retraso',                  type: 'number' },
  { key: 'inventory_shortage',         label: '¿Inventario insuficiente?',           type: 'select', options: ['true','false'] },
  { key: 'route_risk',                 label: 'Riesgo de ruta',                      type: 'select', options: ['alto','medio','bajo'] },
  { key: 'alternative_route_available',label: 'Ruta alternativa disponible',         type: 'select', options: ['true','false'] },
  { key: 'client_type',                label: 'Tipo de cliente',                     type: 'select', options: ['estrategico','regular','ocasional'] },
  { key: 'delay_probability',          label: 'Probabilidad de retraso (%)',         type: 'number' },
]

const RISK_COLORS = { alto: 'bg-red-100 text-red-700', medio: 'bg-yellow-100 text-yellow-700', bajo: 'bg-green-100 text-green-700' }

export default function EvaluatePage() {
  const [form, setForm] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (key, value) => {
    let parsed = value
    if (value === 'true') parsed = true
    else if (value === 'false') parsed = false
    else if (!isNaN(value) && value !== '') parsed = Number(value)
    setForm(f => ({ ...f, [key]: parsed }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const resp = await api.post('/api/v1/decisions/evaluate', {
        input_data: form, request_type: 'logistica'
      })
      setResult(resp.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al evaluar la situación.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Evaluar Situación Logística</h1>
      <p className="text-gray-500 text-sm mb-6">Complete los parámetros de la situación para obtener una recomendación.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Parámetros de la situación</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {FIELDS.map(f => (
              <div key={f.key}>
                <label className="block text-xs font-medium text-gray-600 mb-1">{f.label}</label>
                {f.type === 'select' ? (
                  <select
                    onChange={e => handleChange(f.key, e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="">-- Seleccionar --</option>
                    {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input
                    type="number"
                    onChange={e => handleChange(f.key, e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    placeholder="0"
                  />
                )}
              </div>
            ))}
            {error && <div className="text-red-600 text-sm">{error}</div>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-700 hover:bg-blue-800 text-white py-2.5 rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
            >
              {loading ? 'Evaluando...' : 'Evaluar Situación'}
            </button>
          </form>
        </div>

        {result && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-base font-semibold text-gray-700 mb-4">Recomendación del Sistema</h2>

            <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mb-4 ${RISK_COLORS[result.estimated_risk] || 'bg-gray-100 text-gray-600'}`}>
              Riesgo: {result.estimated_risk}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="text-xs font-medium text-blue-700 mb-1">Acción sugerida</div>
              <div className="text-sm text-blue-900">{result.suggested_action}</div>
            </div>

            <div className="mb-4">
              <div className="text-xs font-medium text-gray-500 mb-1">Confianza del sistema</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(result.confidence * 100).toFixed(0)}%` }}></div>
                </div>
                <span className="text-sm font-bold text-gray-700">{(result.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs font-medium text-gray-500 mb-2">Reglas activadas ({result.activated_rules.length})</div>
              {result.activated_rules.length === 0 ? (
                <p className="text-xs text-gray-400">Ninguna regla activa aplica a la situación.</p>
              ) : (
                <div className="space-y-2">
                  {result.activated_rules.map(r => (
                    <div key={r.rule_id} className="bg-gray-50 border rounded-lg p-3">
                      <div className="text-xs font-semibold text-gray-700">{r.rule_name}</div>
                      <div className="text-xs text-gray-500 mt-1">{r.suggested_action}</div>
                      <div className="text-xs text-blue-600 mt-1">Confianza: {(r.confidence * 100).toFixed(0)}% · Prioridad: {r.priority}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
              <div className="font-medium mb-1">Explicación</div>
              <p className="whitespace-pre-line">{result.explanation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
