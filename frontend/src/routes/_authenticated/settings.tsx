import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { DashboardLayout } from '../../components/Layout/DashboardLayout'
import { Input } from '../../components/UI/Input'
import { Button } from '../../components/UI/Button'
import { AuthService } from '../../services/authService'
import type { ApiError } from '../../types/auth'

export const Route = createFileRoute('/_authenticated/settings')({
  component: SettingsPage,
})

function SettingsPage() {
  const authService = AuthService.getInstance()

  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPasswords, setShowPasswords] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [validationError, setValidationError] = useState('')

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setValidationError('')

    if (newPassword.length < 8) {
      setValidationError('Password must be at least 8 characters')
      return
    }

    if (newPassword !== confirmPassword) {
      setValidationError('Passwords do not match')
      return
    }

    setIsLoading(true)

    try {
      await authService.changePassword(oldPassword, newPassword)
      setSuccess(true)
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || 'Failed to change password. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">
            Manage your account preferences and security settings
          </p>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Change Password</h2>
          <p className="text-sm text-gray-600 mb-6">
            Update your password to keep your account secure. All active sessions will be invalidated.
          </p>

          <form onSubmit={handlePasswordChange} className="space-y-4">
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  Password changed successfully! You'll need to sign in again with your new password.
                </p>
              </div>
            )}

            <Input
              label="Current Password"
              type={showPasswords ? 'text' : 'password'}
              placeholder="Enter current password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
              autoComplete="current-password"
            />

            <Input
              label="New Password"
              type={showPasswords ? 'text' : 'password'}
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              error={validationError && newPassword.length < 8 ? 'Password must be at least 8 characters' : undefined}
              helperText="Must be at least 8 characters"
              required
              autoComplete="new-password"
            />

            <Input
              label="Confirm New Password"
              type={showPasswords ? 'text' : 'password'}
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              error={validationError === 'Passwords do not match' ? validationError : undefined}
              required
              autoComplete="new-password"
            />

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="showPasswords"
                checked={showPasswords}
                onChange={(e) => setShowPasswords(e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <label htmlFor="showPasswords" className="text-sm text-gray-700">
                Show passwords
              </label>
            </div>

            <div className="pt-4">
              <Button type="submit" isLoading={isLoading}>
                Change Password
              </Button>
            </div>
          </form>
        </div>

        {/* Account Security */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Security Settings</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                <p className="text-sm text-gray-500">Add an extra layer of security</p>
              </div>
              <Button variant="outline" size="sm" disabled>
                Coming Soon
              </Button>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-900">Active Sessions</p>
                <p className="text-sm text-gray-500">Manage your active login sessions</p>
              </div>
              <Button variant="outline" size="sm" disabled>
                View Sessions
              </Button>
            </div>
            <div className="flex justify-between items-center py-3">
              <div>
                <p className="font-medium text-gray-900">Login History</p>
                <p className="text-sm text-gray-500">Review recent account activity</p>
              </div>
              <Button variant="outline" size="sm" disabled>
                View History
              </Button>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-lg shadow border-2 border-red-200 p-6">
          <h2 className="text-xl font-bold text-red-900 mb-4">Danger Zone</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-medium text-gray-900">Delete Account</p>
                <p className="text-sm text-gray-500">
                  Permanently delete your account and all associated data
                </p>
              </div>
              <Button variant="outline" size="sm" disabled className="border-red-300 text-red-700 hover:bg-red-50">
                Delete Account
              </Button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
