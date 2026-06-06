// components/Layout.jsx — Shell principal con sidebar de navegación por rol.
import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { path: '/dashboard',  label: 'Dashboard',          roles: ['system_admin','knowledge_admin','analyst','decision_maker','area_expert'] },
  { path: '/evaluate',   label: 'Evaluar Situación',   roles: ['system_admin','decision_maker','knowledge_admin'] },
  { path: '/whatif',     label: 'Análisis What-If',    roles: ['system_admin','analyst','decision_maker','knowledge_admin'] },
  { path: '/rules',      label: 'Reglas de Negocio',   roles: ['system_admin','knowledge_admin','area_expert'] },
  { path: '/knowledge',  label: 'Mapa de Conocimiento',roles: ['system_admin','knowledge_admin','analyst'] },
  { path: '/history',    label: 'Historial',           roles: ['system_admin','decision_maker','analyst','knowledge_admin'] },
  { path: '/users',      label: 'Usuarios',             roles: ['system_admin'] },
]

const ROLE_LABELS = {
  system_admin:    'Administrador del Sistema',
  knowledge_admin: 'Admin. de Conocimiento',
  decision_maker:  'Decisor',
  analyst:         'Analista',
  area_expert:     'Experto del Área',
}

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const visibleItems = NAV_ITEMS.filter(item => item.roles.includes(user?.role))

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className={`${collapsed ? 'w-16' : 'w-64'} bg-nexus-800 text-white flex flex-col transition-all duration-200`}
             style={{ backgroundColor: '#1e3a5f' }}>
        <div className="flex items-center justify-between p-4 border-b border-blue-700">
          {!collapsed && (
            <div>
              <div className="font-bold text-lg text-blue-200">Nexus-Corp</div>
              <div className="text-xs text-blue-400">DistribLog S.A.</div>
            </div>
          )}
          <button onClick={() => setCollapsed(!collapsed)} className="text-blue-300 hover:text-white ml-auto">
            {collapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="flex-1 py-4 overflow-y-auto">
          {visibleItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 text-sm transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-600 text-white'
                  : 'text-blue-200 hover:bg-blue-700 hover:text-white'
              }`}
            >
              {!collapsed && item.label}
              {collapsed && item.label[0]}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-blue-700">
          {!collapsed && (
            <div className="mb-2">
              <div className="text-sm font-medium text-white truncate">{user?.name}</div>
              <div className="text-xs text-blue-300">{ROLE_LABELS[user?.role]}</div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full text-left text-xs text-blue-300 hover:text-red-400 transition-colors"
          >
            {collapsed ? 'X' : 'Cerrar sesión'}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <div className="p-6">{children}</div>
      </main>
    </div>
  )
}
