import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { AuthLayout } from '../components/Layout/AuthLayout'
import { Input } from '../components/UI/Input'
import { Button } from '../components/UI/Button'
import { Link } from '../components/UI/Link'
import { AuthService } from '../services/authService'
import type { ApiError } from '../types/auth'

export const Route = createFileRoute('/forgot-password')({
  component: ForgotPasswordPage,
})

function ForgotPasswordPage() {
  const navigate = useNavigate()
  const authService = AuthService.getInstance()

  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await authService.requestPasswordReset(email)
      setSuccess(true)
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || 'Failed to send reset link. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <AuthLayout
        title="Check Your Email"
        subtitle="We've sent you a password reset link"
        quote="RESET YOUR PASSWORD"
      >
        <div className="space-y-6">
          <div className="p-6 bg-green-50 border border-green-200 rounded-lg text-center">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-gray-700 mb-2">
              If the email exists in our system, you'll receive a password reset link shortly.
            </p>
            <p className="text-sm text-gray-600">
              Please check your inbox and spam folder.
            </p>
          </div>

          <Button type="button" variant="outline" fullWidth onClick={() => navigate({ to: '/login' })}>
            Back to Sign In
          </Button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Forgot Password?"
      subtitle="No worries, we'll send you reset instructions"
      quote="RESET YOUR PASSWORD"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <Input
          label="Email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          helperText="We'll send you a password reset link"
        />

        <Button type="submit" fullWidth isLoading={isLoading}>
          Send Reset Link
        </Button>

        <div className="text-center">
          <Link to="/login" variant="default" className="text-sm">
            <span className="flex items-center justify-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Sign In
            </span>
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
