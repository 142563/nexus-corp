// pages/KnowledgeMapPage.jsx — Mapa de conocimiento: expertos por área con estado de captura.
import React, { useEffect, useState } from 'react'
import api from '../services/api'

const STATUS_COLOR = {
  pendiente:    'bg-gray-100 text-gray-600',
  en_progreso:  'bg-blue-100 text-blue-700',
  completado:   'bg-yellow-100 text-yellow-700',
  validado:     'bg-green-100 text-green-700',
}

const CRIT_COLOR = {
  baja:    'text-gray-500',
  media:   'text-yellow-600',
  alta:    'text-orange-600',
  critica: 'text-red-600',
}

export default function KnowledgeMapPage() {
  const [map, setMap] = useState([])
  const [experts, setExperts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/api/v1/knowledge-areas/map'),
      api.get('/api/v1/experts'),
    ]).then(([mapRes, expertRes]) => {
      setMap(mapRes.data)
      setExperts(expertRes.data)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20 text-gray-400">Cargando mapa de conocimiento...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Mapa de Conocimiento</h1>
      <p className="text-gray-500 text-sm mb-6">Estado de captura de conocimiento por área — DistribLog S.A.</p>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-8">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Área</th>
              <th className="px-4 py-3 text-center">Criticidad</th>
              <th className="px-4 py-3 text-left">Experto Responsable</th>
              <th className="px-4 py-3 text-left">Cargo</th>
              <th className="px-4 py-3 text-center">Estado Captura</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {map.map(row => (
              <tr key={row.area_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{row.area_name}</td>
                <td className={`px-4 py-3 text-center font-semibold text-xs uppercase ${CRIT_COLOR[row.criticality]}`}>
                  {row.criticality}
                </td>
                <td className="px-4 py-3 text-gray-700">{row.expert_name || '—'}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">{row.expert_position || '—'}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLOR[row.capture_status] || 'bg-gray-100'}`}>
                    {row.capture_status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="text-lg font-semibold text-gray-800 mb-4">Directorio de Expertos</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {experts.map(e => (
          <div key={e.id} className="bg-white rounded-xl shadow-sm p-5">
            <div className="font-semibold text-gray-800">{e.name}</div>
            <div className="text-xs text-blue-600 mt-1">{e.position}</div>
            <div className="text-xs text-gray-500 mt-1">{e.area}</div>
            <div className="text-xs text-gray-400 mt-1">{e.email}</div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-xs text-gray-400">{e.years_experience} años de experiencia</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${e.status === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                {e.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
