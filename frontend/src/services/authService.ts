import type {
  RegisterInput,
  LoginInput,
  PasswordResetRequestInput,
  PasswordResetInput,
  TokenRefreshInput,
  RegisterOutput,
  AuthOutput,
  TokenRefreshOutput,
  VerificationOutput,
  MessageOutput,
  SessionListOutput,
} from '../types/auth'
import { HttpClient } from './httpClient'
import { StorageService } from './storageService'
import { ApiConfig } from '../config/api.config'

export class AuthService {
  private static instance: AuthService
  private http: HttpClient
  private storage: StorageService
  private config: ApiConfig

  private constructor() {
    this.http = HttpClient.getInstance()
    this.storage = StorageService.getInstance()
    this.config = ApiConfig.getInstance()
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService()
    }
    return AuthService.instance
  }

  public async register(name: string, email: string, password: string): Promise<RegisterOutput> {
    const url = this.config.getAuthEndpoint('/register')
    const data: RegisterInput = { name, email, password }
    const response = await this.http.post<RegisterOutput>(url, data)

    // Store user data from register response
    this.storage.setUserData({
      user_id: response._uid,
      email: response._em,
      status: response._st,
    })

    return response
  }

  public async login(data: LoginInput, rememberMe = false): Promise<AuthOutput> {
    const url = this.config.getAuthEndpoint('/login')
    const response = await this.http.post<AuthOutput>(url, data)

    // Store access token and refresh token
    this.storage.setAccessToken(response._at)
    this.storage.setRefreshToken(response._rt)
    this.storage.setRememberMe(rememberMe)

    return response
  }

  public async logout(): Promise<void> {
    const url = this.config.getAuthEndpoint('/logout')

    try {
      await this.http.post<MessageOutput>(url, undefined, true)
    } finally {
      // Clear local storage regardless of API response
      this.storage.clearAll()
    }
  }

  public async refreshToken(): Promise<TokenRefreshOutput> {
    const refreshToken = this.storage.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const url = this.config.getTokenEndpoint('/refresh')
    const data: TokenRefreshInput = { refresh_token: refreshToken }
    const response = await this.http.post<TokenRefreshOutput>(url, data)

    // Update tokens
    this.storage.setAccessToken(response._at)
    this.storage.setRefreshToken(response._rt)

    return response
  }

  public async verifyEmail(token: string): Promise<VerificationOutput> {
    const url = this.config.getVerificationEndpoint('/verify-email')
    const response = await this.http.get<VerificationOutput>(
      `${url}?token=${encodeURIComponent(token)}`
    )
    return response
  }

  public async requestPasswordReset(email: string): Promise<VerificationOutput> {
    const url = this.config.getVerificationEndpoint('/forgot-password')
    const data: PasswordResetRequestInput = { email }
    return this.http.post<VerificationOutput>(url, data)
  }

  public async resetPassword(
    token: string,
    newPassword: string
  ): Promise<VerificationOutput> {
    const url = this.config.getVerificationEndpoint('/reset-password')
    const data: PasswordResetInput = { token, new_password: newPassword }
    return this.http.post<VerificationOutput>(url, data)
  }

  public async resendVerification(): Promise<VerificationOutput> {
    const url = this.config.getVerificationEndpoint('/resend-verification')
    return this.http.post<VerificationOutput>(url, undefined, true)
  }

  public async getSessions(): Promise<SessionListOutput> {
    const url = this.config.getSessionEndpoint('')
    return this.http.get<SessionListOutput>(url, true)
  }

  public async revokeSession(sessionId: string): Promise<MessageOutput> {
    const url = this.config.getSessionEndpoint(`/${sessionId}`)
    return this.http.delete<MessageOutput>(url, true)
  }

  public async revokeAllSessions(): Promise<MessageOutput> {
    const url = this.config.getSessionEndpoint('')
    return this.http.delete<MessageOutput>(url, true)
  }

  public isAuthenticated(): boolean {
    return this.storage.getAccessToken() !== null
  }

  public getCurrentUser(): { user_id: string; email: string; status?: string } | null {
    return this.storage.getUserData()
  }
}
