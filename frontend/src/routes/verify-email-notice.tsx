import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { AuthLayout } from '../components/Layout/AuthLayout'
import { Button } from '../components/UI/Button'

export const Route = createFileRoute('/verify-email-notice')({
  component: VerifyEmailNoticePage,
})

function VerifyEmailNoticePage() {
  const navigate = useNavigate()

  return (
    <AuthLayout
      title="Verify Your Email"
      subtitle="We've sent you a verification link"
      quote="CHECK YOUR INBOX"
    >
      <div className="space-y-6">
        <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg text-center">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
          <p className="text-gray-700 mb-2 font-medium">
            Check your email inbox
          </p>
          <p className="text-sm text-gray-600 mb-4">
            We've sent a verification link to your email address.
            Please click the link to activate your account.
          </p>
          <p className="text-xs text-gray-500">
            Didn't receive the email? Check your spam folder.
          </p>
        </div>

        <div className="space-y-3">
          <Button type="button" fullWidth onClick={() => navigate({ to: '/dashboard' })}>
            Continue to Dashboard
          </Button>
          <Button type="button" variant="outline" fullWidth onClick={() => navigate({ to: '/login' })}>
            Back to Sign In
          </Button>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> Your account is created but inactive until you verify your email.
            Some features may be restricted.
          </p>
        </div>
      </div>
    </AuthLayout>
  )
}
