// context/AuthContext.jsx — Contexto global de autenticación JWT para Nexus-Corp.
import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('nexus_token')
    const stored = localStorage.getItem('nexus_user')
    if (token && stored) {
      setUser(JSON.parse(stored))
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    const resp = await api.post('/api/v1/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    const { access_token, role, user_id, name } = resp.data
    const userObj = { id: user_id, name, role, email }
    localStorage.setItem('nexus_token', access_token)
    localStorage.setItem('nexus_user', JSON.stringify(userObj))
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setUser(userObj)
    return userObj
  }

  const logout = () => {
    localStorage.removeItem('nexus_token')
    localStorage.removeItem('nexus_user')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
