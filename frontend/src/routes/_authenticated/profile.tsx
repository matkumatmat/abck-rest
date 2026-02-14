import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '../../contexts/authContext'
import { DashboardLayout } from '../../components/Layout/DashboardLayout'
import { Button } from '../../components/UI/Button'

export const Route = createFileRoute('/_authenticated/profile')({
  component: ProfilePage,
})

function ProfilePage() {
  const { profile, user } = useAuth()

  return (
    <DashboardLayout>
      <div className="max-w-3xl space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
          <p className="text-gray-600">
            Manage your personal information and account settings
          </p>
        </div>

        {/* Profile Picture Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Profile Picture</h2>
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <Button variant="outline">Upload Photo</Button>
              <p className="text-sm text-gray-500 mt-2">
                JPG, GIF or PNG. Max size of 2MB.
              </p>
            </div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Personal Information</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={profile?.username || user?.username || ''}
                  disabled
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-100 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={profile?.email || user?.email || ''}
                  disabled
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-100 cursor-not-allowed"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  value={profile?.first_name || ''}
                  placeholder="Not set"
                  disabled
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-100 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  value={profile?.last_name || ''}
                  placeholder="Not set"
                  disabled
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-100 cursor-not-allowed"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                value={profile?.phone || ''}
                placeholder="Not set"
                disabled
                className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-100 cursor-not-allowed"
              />
            </div>

            <div className="pt-4">
              <Button variant="outline" disabled>
                Edit Profile (Coming Soon)
              </Button>
            </div>
          </div>
        </div>

        {/* Account Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Account Details</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-900">Account Status</p>
                <p className="text-sm text-gray-500">Your account verification status</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                profile?.active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {profile?.active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-900">Member Since</p>
                <p className="text-sm text-gray-500">Account creation date</p>
              </div>
              <p className="text-gray-900">
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'N/A'}
              </p>
            </div>
            <div className="flex justify-between items-center py-3">
              <div>
                <p className="font-medium text-gray-900">User ID</p>
                <p className="text-sm text-gray-500">Your unique identifier</p>
              </div>
              <p className="text-gray-900 font-mono text-sm">
                {profile?.user_id || user?.user_id}
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
