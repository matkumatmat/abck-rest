import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { AuthLayout } from '../components/Layout/AuthLayout'
import { Button } from '../components/UI/Button'
import { AuthService } from '../services/authService'
import type { ApiError } from '../types/auth'

export const Route = createFileRoute('/verify-email')({
  component: VerifyEmailPage,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      token: (search.token as string) || '',
    }
  },
})

function VerifyEmailPage() {
  const navigate = useNavigate()
  const { token } = Route.useSearch()
  const authService = AuthService.getInstance()

  const [isVerifying, setIsVerifying] = useState(true)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) {
      setError('Invalid or missing verification token')
      setIsVerifying(false)
      return
    }

    verifyEmail()
  }, [token])

  const verifyEmail = async () => {
    try {
      await authService.verifyEmail(token)
      setSuccess(true)
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.detail || 'Email verification failed. The link may have expired.')
    } finally {
      setIsVerifying(false)
    }
  }

  if (isVerifying) {
    return (
      <AuthLayout
        title="Verifying Email"
        subtitle="Please wait while we verify your email address"
        quote="VERIFICATION IN PROGRESS"
      >
        <div className="text-center py-12">
          <svg
            className="animate-spin h-16 w-16 mx-auto mb-4 text-blue-600"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-600">Verifying your email...</p>
        </div>
      </AuthLayout>
    )
  }

  if (success) {
    return (
      <AuthLayout
        title="Email Verified!"
        subtitle="Your account has been successfully activated"
        quote="ACCOUNT ACTIVATED"
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
            <p className="text-gray-700 mb-2 font-medium">
              Your email has been verified!
            </p>
            <p className="text-sm text-gray-600">
              You can now sign in to your account.
            </p>
          </div>

          <Button type="button" fullWidth onClick={() => navigate({ to: '/login' })}>
            Continue to Sign In
          </Button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Verification Failed"
      subtitle="We couldn't verify your email address"
      quote="VERIFICATION ERROR"
    >
      <div className="space-y-6">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <svg
            className="w-12 h-12 mx-auto mb-4 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-red-800 text-center">{error}</p>
        </div>

        <Button type="button" variant="outline" fullWidth onClick={() => navigate({ to: '/login' })}>
          Back to Sign In
        </Button>
      </div>
    </AuthLayout>
  )
}
