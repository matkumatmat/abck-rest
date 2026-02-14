import type { ApiError, ApiResponse } from '../types/auth'
import { ApiConfig } from '../config/api.config'
import { StorageService } from './storageService'

export class HttpClient {
  private static instance: HttpClient
  private config: ApiConfig
  private storage: StorageService

  private constructor() {
    this.config = ApiConfig.getInstance()
    this.storage = StorageService.getInstance()
  }

  public static getInstance(): HttpClient {
    if (!HttpClient.instance) {
      HttpClient.instance = new HttpClient()
    }
    return HttpClient.instance
  }

  private getHeaders(includeAuth = false): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (includeAuth) {
      const token = this.storage.getAccessToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    return headers
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'Network error occurred',
        status: response.status,
      }))
      throw error
    }

    // Backend wraps all responses in {success, data, meta}
    // Unwrap and return only the data field
    const wrapped: ApiResponse<T> = await response.json()
    return wrapped.data
  }

  public async get<T>(url: string, authenticated = false): Promise<T> {
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(authenticated),
      credentials: 'include', // Important for cookies (refresh token)
    })

    return this.handleResponse<T>(response)
  }

  public async post<T>(
    url: string,
    data?: unknown,
    authenticated = false
  ): Promise<T> {
    const response = await fetch(url, {
      method: 'POST',
      headers: this.getHeaders(authenticated),
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  public async put<T>(
    url: string,
    data?: unknown,
    authenticated = false
  ): Promise<T> {
    const response = await fetch(url, {
      method: 'PUT',
      headers: this.getHeaders(authenticated),
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  public async delete<T>(url: string, authenticated = false): Promise<T> {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: this.getHeaders(authenticated),
      credentials: 'include',
    })

    return this.handleResponse<T>(response)
  }
}
