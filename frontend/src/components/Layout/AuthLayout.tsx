import { type ReactNode } from 'react'

interface AuthLayoutProps {
  children: ReactNode
  title: string
  subtitle?: string
  quote?: string
}

export function AuthLayout({ children, title, subtitle, quote }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left Side - Hero/Gradient Section */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-900 via-purple-600 to-blue-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20" />

        <div className="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
          {quote && (
            <p className="text-sm font-medium uppercase tracking-wider mb-8 opacity-80">
              {quote}
            </p>
          )}

          <h1 className="text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            Get<br />
            Everything<br />
            You Want
          </h1>

          <p className="text-lg opacity-90 max-w-md">
            You can get everything you want if you work hard,
            trust the process, and stick to the plan.
          </p>
        </div>
      </div>

      {/* Right Side - Form Section */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-white lg:w-1/2">
        <div className="w-full max-w-md">
          {/* Logo for mobile */}
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold text-lg">
              KAuth
            </div>
          </div>

          {/* Title Section */}
          <div className="mb-8 text-center lg:text-left">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
              {title}
            </h2>
            {subtitle && (
              <p className="text-gray-600">
                {subtitle}
              </p>
            )}
          </div>

          {/* Form Content */}
          {children}
        </div>
      </div>
    </div>
  )
}
