export class ApiConfig {
  private static instance: ApiConfig

  public readonly baseUrl: string
  public readonly timeout: number

  private constructor() {
    // In development: Vite proxy forwards to backend
    // In production: nginx routes to backend
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || ''
    this.timeout = 30000 // 30 seconds
  }

  public static getInstance(): ApiConfig {
    if (!ApiConfig.instance) {
      ApiConfig.instance = new ApiConfig()
    }
    return ApiConfig.instance
  }

  public getAuthEndpoint(path: string): string {
    return `${this.baseUrl}/v1/auth${path}`
  }

  public getTokenEndpoint(path: string): string {
    return `${this.baseUrl}/v1/token${path}`
  }

  public getVerificationEndpoint(path: string): string {
    return `${this.baseUrl}/v1${path}`
  }

  public getSessionEndpoint(path: string): string {
    return `${this.baseUrl}/v1/sessions${path}`
  }
}
