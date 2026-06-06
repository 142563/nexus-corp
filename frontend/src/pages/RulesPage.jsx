// pages/RulesPage.jsx — Gestión completa de reglas de negocio con CRUD.
import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

const STATUS_COLORS = {
  activa:      'bg-green-100 text-green-700',
  pendiente:   'bg-yellow-100 text-yellow-700',
  inactiva:    'bg-gray-100 text-gray-600',
  en_revision: 'bg-orange-100 text-orange-700',
  rechazada:   'bg-red-100 text-red-700',
}

export default function RulesPage() {
  const { user } = useAuth()
  const canManage = ['system_admin','knowledge_admin'].includes(user?.role)
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name:'', description:'', suggested_action:'', priority:5, area_id:1, expert_id:1, confidence_level:0.8, user_explanation:'' })
  const [conditions, setConditions] = useState([{ field:'', operator:'eq', value:'' }])
  const [saving, setSaving] = useState(false)

  const loadRules = () => {
    api.get('/api/v1/rules').then(r => setRules(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { loadRules() }, [])

  const addCondition = () => setConditions(c => [...c, { field:'', operator:'eq', value:'' }])
  const updateCondition = (i, key, val) => setConditions(c => c.map((x,idx) => idx===i ? {...x,[key]:val} : x))

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const parsed = conditions.map(c => ({
        field: c.field,
        operator: c.operator,
        value: isNaN(c.value) || c.value==='' ? c.value : Number(c.value),
      }))
      await api.post('/api/v1/rules', { ...form, conditions: parsed, priority: Number(form.priority), confidence_level: Number(form.confidence_level) })
      setShowForm(false)
      loadRules()
    } catch(err) { console.error(err) } finally { setSaving(false) }
  }

  const toggleStatus = async (rule) => {
    const next = rule.status === 'activa' ? 'inactiva' : 'activa'
    try {
      await api.patch(`/api/v1/rules/${rule.id}/status`, { status: next })
      loadRules()
    } catch(err) { console.error(err) }
  }

  if (loading) return <div className="text-center py-20 text-gray-400">Cargando reglas...</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Reglas de Negocio</h1>
          <p className="text-gray-500 text-sm">Base de conocimiento de DistribLog S.A.</p>
        </div>
        {canManage && (
          <button onClick={() => setShowForm(!showForm)} className="bg-blue-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-800 transition-colors">
            + Nueva Regla
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">Nueva Regla de Negocio</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-500">Nombre</label>
                <input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
              </div>
              <div>
                <label className="text-xs text-gray-500">Prioridad (1-10)</label>
                <input type="number" min="1" max="10" value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-500">Descripción</label>
              <textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})} rows="2" className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Acción sugerida</label>
              <textarea value={form.suggested_action} onChange={e=>setForm({...form,suggested_action:e.target.value})} rows="2" required className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs text-gray-500">Condiciones</label>
                <button type="button" onClick={addCondition} className="text-xs text-blue-600 hover:underline">+ Agregar</button>
              </div>
              {conditions.map((c,i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input placeholder="campo" value={c.field} onChange={e=>updateCondition(i,'field',e.target.value)} className="flex-1 border rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none" />
                  <select value={c.operator} onChange={e=>updateCondition(i,'operator',e.target.value)} className="border rounded-lg px-2 py-2 text-xs">
                    {['eq','ne','gt','gte','lt','lte','in','contains'].map(op=><option key={op}>{op}</option>)}
                  </select>
                  <input placeholder="valor" value={c.value} onChange={e=>updateCondition(i,'value',e.target.value)} className="flex-1 border rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-gray-500">ID Área</label>
                <input type="number" value={form.area_id} onChange={e=>setForm({...form,area_id:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
              </div>
              <div>
                <label className="text-xs text-gray-500">ID Experto</label>
                <input type="number" value={form.expert_id} onChange={e=>setForm({...form,expert_id:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
              </div>
              <div>
                <label className="text-xs text-gray-500">Confianza (0-1)</label>
                <input type="number" step="0.01" min="0" max="1" value={form.confidence_level} onChange={e=>setForm({...form,confidence_level:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={saving} className="bg-blue-700 text-white px-6 py-2 rounded-lg text-sm hover:bg-blue-800 transition-colors disabled:opacity-50">
                {saving ? 'Guardando...' : 'Guardar Regla'}
              </button>
              <button type="button" onClick={()=>setShowForm(false)} className="text-gray-500 px-6 py-2 rounded-lg text-sm border hover:bg-gray-50">
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Nombre</th>
              <th className="px-4 py-3 text-center">Prioridad</th>
              <th className="px-4 py-3 text-center">Confianza</th>
              <th className="px-4 py-3 text-center">Estado</th>
              <th className="px-4 py-3 text-center">Condiciones</th>
              {canManage && <th className="px-4 py-3 text-center">Acción</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {rules.map(rule => (
              <tr key={rule.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-800">{rule.name}</div>
                  <div className="text-xs text-gray-400">{rule.suggested_action.slice(0,60)}...</div>
                </td>
                <td className="px-4 py-3 text-center font-bold text-blue-700">{rule.priority}</td>
                <td className="px-4 py-3 text-center">{(rule.confidence_level*100).toFixed(0)}%</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[rule.status] || 'bg-gray-100'}`}>
                    {rule.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-center text-gray-500">{rule.conditions.length}</td>
                {canManage && (
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => toggleStatus(rule)}
                      className={`text-xs px-3 py-1 rounded-lg transition-colors ${rule.status === 'activa' ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'}`}
                    >
                      {rule.status === 'activa' ? 'Desactivar' : 'Activar'}
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
