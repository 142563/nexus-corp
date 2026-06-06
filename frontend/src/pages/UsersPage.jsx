// pages/UsersPage.jsx — Gestión de usuarios. Solo visible para system_admin.
import React, { useEffect, useState } from 'react'
import api from '../services/api'

const ROLES = ['system_admin','knowledge_admin','decision_maker','analyst','area_expert']
const ROLE_LABELS = {
  system_admin:    'Admin. Sistema',
  knowledge_admin: 'Admin. Conocimiento',
  decision_maker:  'Decisor',
  analyst:         'Analista',
  area_expert:     'Experto',
}

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name:'', email:'', password:'', role:'analyst' })
  const [saving, setSaving] = useState(false)

  const loadUsers = () => {
    api.get('/api/v1/users').then(r => setUsers(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { loadUsers() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/v1/users', form)
      setShowForm(false)
      setForm({ name:'', email:'', password:'', role:'analyst' })
      loadUsers()
    } catch(err) { console.error(err) } finally { setSaving(false) }
  }

  const updateRole = async (userId, role) => {
    try {
      await api.patch(`/api/v1/users/${userId}/role`, { role })
      loadUsers()
    } catch(err) { console.error(err) }
  }

  if (loading) return <div className="text-center py-20 text-gray-400">Cargando usuarios...</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Usuarios del Sistema</h1>
          <p className="text-gray-500 text-sm">Gestión de accesos — Nexus-Corp</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-800 transition-colors">
          + Nuevo Usuario
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">Crear Usuario</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500">Nombre completo</label>
              <input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Correo electrónico</label>
              <input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Contraseña</label>
              <input type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Rol</label>
              <select value={form.role} onChange={e=>setForm({...form,role:e.target.value})} className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:ring-2 focus:ring-blue-500 focus:outline-none">
                {ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
              </select>
            </div>
            <div className="col-span-2 flex gap-3">
              <button type="submit" disabled={saving} className="bg-blue-700 text-white px-6 py-2 rounded-lg text-sm hover:bg-blue-800 disabled:opacity-50">
                {saving ? 'Guardando...' : 'Crear Usuario'}
              </button>
              <button type="button" onClick={()=>setShowForm(false)} className="border text-gray-500 px-6 py-2 rounded-lg text-sm hover:bg-gray-50">Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Nombre</th>
              <th className="px-4 py-3 text-left">Correo</th>
              <th className="px-4 py-3 text-center">Rol</th>
              <th className="px-4 py-3 text-center">Estado</th>
              <th className="px-4 py-3 text-center">Cambiar Rol</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{u.name}</td>
                <td className="px-4 py-3 text-gray-600 text-xs">{u.email}</td>
                <td className="px-4 py-3 text-center">
                  <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                    {ROLE_LABELS[u.role] || u.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`text-xs px-2 py-1 rounded-full ${u.status === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {u.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <select
                    value={u.role}
                    onChange={e => updateRole(u.id, e.target.value)}
                    className="text-xs border rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    {ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
