// Auth-related TypeScript types matching backend DTOs

// Backend Response Wrapper
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  meta?: Record<string, any> | null
}

// === Request DTOs ===
export interface RegisterInput {
  name: string
  email: string
  password: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface TokenRefreshInput {
  refresh_token: string
}

export interface PasswordResetRequestInput {
  email: string
}

export interface PasswordResetInput {
  token: string
  new_password: string
}

export interface PasswordChangeInput {
  old_password: string
  new_password: string
}

// === Response DTOs (obfuscated with underscore prefix) ===
export interface RegisterOutput {
  _uid: string    // user_id
  _em: string     // email
  _st: string     // status
}

export interface AuthOutput {
  _at: string     // access_token
  _rt: string     // refresh_token
  _exp: number    // expires_in
}

export interface TokenRefreshOutput {
  _at: string     // access_token
  _rt: string     // refresh_token
  _exp: number    // expires_in
}

export interface VerificationOutput {
  success: boolean
  _m: string      // message
}

export interface MessageOutput {
  message: string
}

export interface SessionItem {
  _sid: string          // session_id
  _ip: string           // ip_address
  _ua: string           // user_agent
  _la: string           // last_activity (datetime)
  _ca: string           // created_at (datetime)
}

export interface SessionListOutput {
  sessions: SessionItem[]
  total: number
}

// === Error Response ===
export interface ApiError {
  detail: string
  code?: string
  status?: number
}
