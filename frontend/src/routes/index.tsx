import { createFileRoute } from '@tanstack/react-router'
import { useEffect } from 'react'
import { useAuth } from '../contexts/authContext'
import { useNavigate } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        navigate({ to: '/dashboard' })
      } else {
        navigate({ to: '/login' })
      }
    }
  }, [isAuthenticated, isLoading, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-600 to-blue-600">
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-purple-600 font-bold text-2xl mb-4">
          KAuth
        </div>
        <p className="text-white text-lg">Loading...</p>
      </div>
    </div>
  )
}
