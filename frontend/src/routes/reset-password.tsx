import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { AuthLayout } from '../components/Layout/AuthLayout'
import { Input } from '../components/UI/Input'
import { Button } from '../components/UI/Button'
import { AuthService } from '../services/authService'
import type { ApiError } from '../types/auth'

export const Route = createFileRoute('/reset-password')({
  component: ResetPasswordPage,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      token: (search.token as string) || '',
    }
  },
})

function ResetPasswordPage() {
  const navigate = useNavigate()
  const { token } = Route.useSearch()
  const authService = AuthService.getInstance()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [validationError, setValidationError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setValidationError('')

    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters')
      return
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match')
      return
    }

    if (!token) {
      setError('Invalid or missing reset token')
      return
    }

    setIsLoading(true)

    try {
      await authService.resetPassword(token, password)
      navigate({ to: '/login', search: { resetSuccess: 'true' } })
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || 'Failed to reset password. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Reset Password"
      subtitle="Enter your new password"
      quote="NEW BEGINNING"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <Input
          label="New Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Enter new password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={validationError && password.length < 8 ? 'Password must be at least 8 characters' : undefined}
          helperText="Must be at least 8 characters"
          required
          autoComplete="new-password"
          rightIcon={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="hover:text-gray-600"
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          }
        />

        <Input
          label="Confirm New Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Confirm new password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          error={validationError === 'Passwords do not match' ? validationError : undefined}
          required
          autoComplete="new-password"
        />

        <Button type="submit" fullWidth isLoading={isLoading}>
          Reset Password
        </Button>
      </form>
    </AuthLayout>
  )
}
