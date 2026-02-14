# KAuth Frontend - OOP Architecture

Modern authentication frontend built with **TanStack Start** (React + TanStack Router + SSR), following strict OOP principles and mobile-first design.

## Architecture Overview

### OOP Design Pattern

This frontend follows **Object-Oriented Programming** principles:

- **Singleton Services**: AuthService, HttpClient, StorageService, ApiConfig
- **Separation of Concerns**: Clear boundaries between services, UI, and state
- **Dependency Injection**: Services injected via getInstance() pattern
- **Type Safety**: Strict TypeScript with no `any` types

### Project Structure

```
frontend/src/
├── config/
│   └── api.config.ts              # API configuration (Singleton)
├── services/                       # OOP Services Layer
│   ├── authService.ts             # Authentication business logic (Singleton)
│   ├── httpClient.ts              # HTTP abstraction layer (Singleton)
│   └── storageService.ts          # LocalStorage wrapper (Singleton)
├── types/
│   └── auth.ts                    # TypeScript interfaces matching backend DTOs
├── contexts/
│   └── authContext.tsx            # React Context for global auth state
├── components/
│   ├── UI/                        # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Checkbox.tsx
│   │   └── Link.tsx
│   └── Layout/                    # Layout components
│       ├── AuthLayout.tsx         # Split-screen auth layout
│       └── DashboardLayout.tsx    # Authenticated pages layout
└── routes/                        # File-based routing (TanStack Router)
    ├── __root.tsx                 # Root layout + AuthProvider wrapper
    ├── index.tsx                  # Homepage (redirects to login/dashboard)
    ├── login.tsx                  # POST /auth/login
    ├── register.tsx               # POST /auth/register
    ├── forgot-password.tsx        # POST /auth/password-reset-request
    ├── reset-password.tsx         # POST /auth/password-reset
    ├── verify-email.tsx           # POST /auth/verify-email
    ├── verify-email-notice.tsx    # Email verification pending notice
    ├── _authenticated.tsx         # Protected routes layout
    └── _authenticated/
        ├── dashboard.tsx          # GET /auth/me
        ├── profile.tsx            # User profile display
        └── settings.tsx           # POST /auth/password-change
```

## Backend Endpoints Mapping

All endpoints under `/api/auth/*` (routed via nginx):

| Route | Backend Endpoint | Method | Description |
|-------|-----------------|--------|-------------|
| `/login` | `/api/auth/login` | POST | User login |
| `/register` | `/api/auth/register` | POST | User registration |
| `/forgot-password` | `/api/auth/password-reset-request` | POST | Request password reset |
| `/reset-password?token=xxx` | `/api/auth/password-reset` | POST | Reset password with token |
| `/verify-email?token=xxx` | `/api/auth/verify-email` | POST | Verify email with token |
| `/dashboard` | `/api/auth/me` | GET | Get user profile (protected) |
| `/profile` | `/api/auth/me` | GET | Get user profile (protected) |
| `/settings` | `/api/auth/password-change` | POST | Change password (protected) |
| - | `/api/auth/logout` | POST | Logout (called on logout button) |
| - | `/api/auth/refresh` | POST | Refresh token (automatic) |

## OOP Services

### 1. AuthService (Singleton)

Main authentication service handling all auth operations.

```typescript
const authService = AuthService.getInstance()

// Register
await authService.register({ username, email, password })

// Login
await authService.login({ email, password }, rememberMe)

// Logout
await authService.logout()

// Get profile
const profile = await authService.getProfile()

// Change password
await authService.changePassword(oldPassword, newPassword)

// Check auth status
const isAuth = authService.isAuthenticated()
```

### 2. HttpClient (Singleton)

HTTP wrapper with automatic token injection and error handling.

```typescript
const http = HttpClient.getInstance()

// GET request (authenticated)
const data = await http.get<UserProfile>('/api/auth/me', true)

// POST request
const response = await http.post<AuthOutput>('/api/auth/login', { email, password })
```

### 3. StorageService (Singleton)

LocalStorage abstraction for token and user data management.

```typescript
const storage = StorageService.getInstance()

// Store token
storage.setAccessToken(token)

// Get token
const token = storage.getAccessToken()

// Store user data
storage.setUserData({ user_id, email, username })

// Clear all
storage.clearAll()
```

### 4. ApiConfig (Singleton)

Centralized API configuration.

```typescript
const config = ApiConfig.getInstance()

// Get full endpoint URL
const url = config.getAuthEndpoint('/login')
// Returns: http://localhost/api/auth/login
```

## Design System

### Split-Screen Auth Layout

- **Left Side**: Gradient hero section with motivational text
- **Right Side**: Auth forms (mobile-first, responsive)
- **Mobile**: Stacked layout, hero hidden on small screens

### Colors

- Primary: Purple-Blue gradient (`from-purple-900 via-purple-600 to-blue-600`)
- Accent: Black buttons, gray inputs
- States: Green (success), Red (error), Yellow (warning)

### Components

All UI components follow consistent patterns:
- **Button**: 4 variants (primary, secondary, outline, ghost), loading states
- **Input**: Label, error, helper text, left/right icons
- **Checkbox**: Custom styled with label
- **Link**: TanStack Router Link with variant styles

## Authentication Flow

1. **User visits `/`** → Redirects to `/login` or `/dashboard` based on auth state
2. **Login** → Stores access token + user data → Redirect to `/dashboard`
3. **Register** → Creates account → Redirect to `/verify-email-notice`
4. **Protected Routes** → `_authenticated.tsx` checks token → Redirect to `/login` if unauthorized
5. **Token Refresh** → Automatic via httpOnly cookie (handled by backend)
6. **Logout** → Clears local storage → Invalidates session → Redirect to `/login`

## State Management

### AuthContext

Global authentication state using React Context:

```typescript
const {
  isAuthenticated,   // Boolean auth status
  user,              // Basic user info (username, email, user_id)
  profile,           // Full profile (from GET /auth/me)
  isLoading,         // Loading state
  login,             // Login function
  register,          // Register function
  logout,            // Logout function
  refreshProfile     // Refresh profile data
} = useAuth()
```

## Protected Routes

Use TanStack Router's `beforeLoad` for route protection:

```typescript
// routes/_authenticated.tsx
beforeLoad: async () => {
  const authService = AuthService.getInstance()
  if (!authService.isAuthenticated()) {
    throw redirect({ to: '/login' })
  }
}
```

All routes under `_authenticated/` are automatically protected.

## Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
VITE_API_BASE_URL=http://localhost
```

## Development

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

**Important**: Backend must be running on port 8001/8002 with nginx on port 80.

## Security Features

- **HttpOnly Cookies**: Refresh token stored in httpOnly cookie (backend managed)
- **Access Token**: Stored in localStorage, short-lived
- **Automatic Token Refresh**: On 401 errors, attempts token refresh
- **CSRF Protection**: Credentials include mode for cookie handling
- **Password Validation**: Min 8 characters, client-side validation
- **Protected Routes**: Server-side validation via bearer token

## Mobile-First Design

- Responsive breakpoints: `sm:` (640px), `md:` (768px), `lg:` (1024px)
- Touch-friendly tap targets (min 44px)
- Optimized forms for mobile keyboards
- Hidden hero section on mobile for focus on forms

## Type Safety

- All API responses typed via interfaces in `types/auth.ts`
- Matches backend DTOs exactly (RegisterInput, LoginInput, AuthOutput, etc.)
- No `any` types allowed
- Strict TypeScript configuration

## Error Handling

- API errors displayed in red banners
- Form validation errors shown below inputs
- Network errors caught and displayed
- Graceful fallbacks for failed requests

## Next Steps

1. **Test authentication flow** - Login, register, password reset
2. **Add profile editing** - Update first_name, last_name, phone
3. **Implement 2FA** - Two-factor authentication
4. **Session management** - View active sessions
5. **Login history** - Audit log of logins

---

Built with TanStack Start, React, TypeScript, and Tailwind CSS.
