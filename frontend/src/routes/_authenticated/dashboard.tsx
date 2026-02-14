import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '../../contexts/authContext'
import { DashboardLayout } from '../../components/Layout/DashboardLayout'

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: DashboardPage,
})

function DashboardPage() {
  const { profile, user } = useAuth()

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your account today.
          </p>
        </div>

        {/* Account Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600">Account Status</p>
                <p className="text-lg font-semibold text-gray-900">
                  {profile?.active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-lg font-semibold text-gray-900 truncate">
                  {profile?.email || user?.email}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600">Member Since</p>
                <p className="text-lg font-semibold text-gray-900">
                  {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Account Information</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-medium text-gray-600">Username</label>
                <p className="mt-1 text-gray-900">{profile?.username || user?.username}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Email</label>
                <p className="mt-1 text-gray-900">{profile?.email || user?.email}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">First Name</label>
                <p className="mt-1 text-gray-900">{profile?.first_name || 'Not set'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Last Name</label>
                <p className="mt-1 text-gray-900">{profile?.last_name || 'Not set'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Phone</label>
                <p className="mt-1 text-gray-900">{profile?.phone || 'Not set'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">User ID</label>
                <p className="mt-1 text-gray-900 font-mono text-sm">{profile?.user_id || user?.user_id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Account Inactive Warning */}
        {profile && !profile.active && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex gap-4">
              <svg className="w-6 h-6 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <h3 className="text-lg font-semibold text-yellow-900 mb-2">Account Not Verified</h3>
                <p className="text-sm text-yellow-800">
                  Your account is inactive until you verify your email address.
                  Please check your inbox for the verification link.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
