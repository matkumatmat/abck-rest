export class StorageService {
  private static instance: StorageService
  private readonly prefix = 'kauth_'

  private constructor() {}

  public static getInstance(): StorageService {
    if (!StorageService.instance) {
      StorageService.instance = new StorageService()
    }
    return StorageService.instance
  }

  public setAccessToken(token: string): void {
    localStorage.setItem(`${this.prefix}access_token`, token)
  }

  public getAccessToken(): string | null {
    return localStorage.getItem(`${this.prefix}access_token`)
  }

  public removeAccessToken(): void {
    localStorage.removeItem(`${this.prefix}access_token`)
  }

  public setRefreshToken(token: string): void {
    localStorage.setItem(`${this.prefix}refresh_token`, token)
  }

  public getRefreshToken(): string | null {
    return localStorage.getItem(`${this.prefix}refresh_token`)
  }

  public removeRefreshToken(): void {
    localStorage.removeItem(`${this.prefix}refresh_token`)
  }

  public setUserData(user: { user_id: string; email: string; status?: string }): void {
    localStorage.setItem(`${this.prefix}user`, JSON.stringify(user))
  }

  public getUserData(): { user_id: string; email: string; status?: string } | null {
    const data = localStorage.getItem(`${this.prefix}user`)
    return data ? JSON.parse(data) : null
  }

  public removeUserData(): void {
    localStorage.removeItem(`${this.prefix}user`)
  }

  public setRememberMe(value: boolean): void {
    localStorage.setItem(`${this.prefix}remember_me`, String(value))
  }

  public getRememberMe(): boolean {
    return localStorage.getItem(`${this.prefix}remember_me`) === 'true'
  }

  public clearAll(): void {
    this.removeAccessToken()
    this.removeRefreshToken()
    this.removeUserData()
    localStorage.removeItem(`${this.prefix}remember_me`)
  }
}
