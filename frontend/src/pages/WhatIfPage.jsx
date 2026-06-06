// pages/WhatIfPage.jsx — Crea y compara escenarios hipotéticos lado a lado.
import React, { useState } from 'react'
import api from '../services/api'

function ScenarioForm({ index, scenario, onChange }) {
  const fields = [
    { key: 'order_priority', label: 'Prioridad', type: 'select', options: ['alta','media','baja'] },
    { key: 'delay_minutes', label: 'Retraso (min)', type: 'number' },
    { key: 'client_type', label: 'Tipo cliente', type: 'select', options: ['estrategico','regular','ocasional'] },
    { key: 'delay_probability', label: 'Prob. retraso (%)', type: 'number' },
    { key: 'route_risk', label: 'Riesgo ruta', type: 'select', options: ['alto','medio','bajo'] },
  ]
  return (
    <div className="bg-white rounded-xl shadow-sm p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Escenario {index + 1}</h3>
      <div className="mb-3">
        <label className="text-xs text-gray-500">Nombre del escenario</label>
        <input
          type="text"
          value={scenario.name}
          onChange={e => onChange('name', e.target.value)}
          className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          placeholder={`Escenario ${index + 1}`}
        />
      </div>
      {fields.map(f => (
        <div key={f.key} className="mb-3">
          <label className="text-xs text-gray-500">{f.label}</label>
          {f.type === 'select' ? (
            <select
              onChange={e => onChange(f.key, e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">--</option>
              {f.options.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          ) : (
            <input
              type="number"
              onChange={e => onChange(f.key, Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          )}
        </div>
      ))}
    </div>
  )
}

function ResultCard({ result }) {
  if (!result) return null
  return (
    <div className="bg-blue-50 rounded-xl p-4 mt-4">
      <div className="text-xs font-semibold text-blue-800 mb-1">{result.name}</div>
      <div className="text-sm font-medium text-gray-800 mb-1">{result.suggested_action}</div>
      <div className="text-xs text-gray-500">Confianza: {(result.confidence * 100).toFixed(0)}% · Riesgo: {result.risk}</div>
      <div className="text-xs text-gray-400 mt-1">Reglas activadas: {result.activated_rules.length}</div>
    </div>
  )
}

export default function WhatIfPage() {
  const [scenarios, setScenarios] = useState([
    { name: 'Escenario A', input_data: {} },
    { name: 'Escenario B', input_data: {} },
  ])
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const updateScenario = (index, key, value) => {
    setScenarios(prev => prev.map((s, i) => {
      if (i !== index) return s
      if (key === 'name') return { ...s, name: value }
      return { ...s, input_data: { ...s.input_data, [key]: value } }
    }))
  }

  const handleCompare = async () => {
    setLoading(true)
    try {
      const resp = await api.post('/api/v1/whatif/compare', { scenarios })
      setResults(resp.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Análisis What-If</h1>
      <p className="text-gray-500 text-sm mb-6">Compare escenarios hipotéticos sin afectar el historial de decisiones.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {scenarios.map((s, i) => (
          <div key={i}>
            <ScenarioForm index={i} scenario={s} onChange={(k, v) => updateScenario(i, k, v)} />
            <ResultCard result={results[i]} />
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-center">
        <button
          onClick={handleCompare}
          disabled={loading}
          className="bg-blue-700 hover:bg-blue-800 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {loading ? 'Comparando...' : 'Comparar Escenarios'}
        </button>
      </div>
    </div>
  )
}
