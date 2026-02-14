import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { AuthService } from '../services/authService'

interface AuthContextState {
  isAuthenticated: boolean
  user: { user_id: string; email: string; status?: string } | null
  isLoading: boolean
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextState | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<{ user_id: string; email: string; status?: string } | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const authService = AuthService.getInstance()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const isAuth = authService.isAuthenticated()
      setIsAuthenticated(isAuth)

      if (isAuth) {
        const currentUser = authService.getCurrentUser()
        setUser(currentUser)

        // Try to refresh token if expired
        try {
          await authService.refreshToken()
        } catch (error) {
          // Token expired or refresh failed, logout
          await logout()
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string, rememberMe = false) => {
    await authService.login({ email, password }, rememberMe)
    setIsAuthenticated(true)

    // Get user data from storage (set by authService)
    const currentUser = authService.getCurrentUser()
    setUser(currentUser)
  }

  const register = async (name: string, email: string, password: string) => {
    await authService.register(name, email, password)

    // After registration, user data is stored but no tokens yet
    // User needs to verify email or login
    const currentUser = authService.getCurrentUser()
    setUser(currentUser)
  }

  const logout = async () => {
    await authService.logout()
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
