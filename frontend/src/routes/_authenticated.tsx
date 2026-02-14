import { createFileRoute, Outlet, redirect } from '@tanstack/react-router'
import { AuthService } from '../services/authService'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async () => {
    const authService = AuthService.getInstance()
    const isAuthenticated = authService.isAuthenticated()

    if (!isAuthenticated) {
      throw redirect({
        to: '/login',
        search: {
          redirect: window.location.pathname,
        },
      })
    }
  },
  component: AuthenticatedLayout,
})

function AuthenticatedLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Outlet />
    </div>
  )
}
