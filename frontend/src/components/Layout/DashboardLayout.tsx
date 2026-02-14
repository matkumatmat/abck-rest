import { type ReactNode } from 'react'
import { useAuth } from '../../contexts/authContext'
import { Link } from '../UI/Link'
import { useNavigate } from '@tanstack/react-router'

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate({ to: '/login' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold text-lg">
                KAuth
              </div>

              <div className="hidden md:flex gap-6">
                <Link to="/dashboard" className="text-gray-700 hover:text-gray-900 font-medium">
                  Dashboard
                </Link>
                <Link to="/profile" className="text-gray-700 hover:text-gray-900 font-medium">
                  Profile
                </Link>
                <Link to="/settings" className="text-gray-700 hover:text-gray-900 font-medium">
                  Settings
                </Link>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{user?.username}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>

              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
