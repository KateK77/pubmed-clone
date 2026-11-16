export type Author = { name: string; affiliations?: string[] }
export type Article = {
  pmid: string; title: string; authors: Author[]; journal: string; year: string
  pmcid?: string; doi?: string; date?: string; volume?: string; issue?: string; pages?: string
  abstract?: { label: string; text: string }[]; keywords?: string[]; mesh?: string[]; types?: string[]
  references?: { citation: string; pmid: string }[]
}
export type SearchResult = { count: number; accessible_count: number; results: Article[]; partial: boolean; translation: string }
export type User = { id: number; username: string; email: string; first_name: string; last_name: string; email_verified?: boolean }
export type Session = { user: User | null; email_verification_required?: boolean; email_delivery_available?: boolean }
export type Collection = { id: number; name: string; count: number }
export type HistoryEntry = { id: number; query: string; sort: string; filters: Record<string, string>; created: string; count?: number }

function csrfToken() {
  const prefix = 'medresearch_csrftoken='
  return document.cookie.split('; ').find(cookie => cookie.startsWith(prefix))?.slice(prefix.length) ?? ''
}

const fieldNames: Record<string, string> = {
  first_name: 'First name', last_name: 'Last name', current_password: 'Current password',
  password: 'Password', email: 'Email', code: 'Verification code', username: 'Username',
  password_confirmation: 'Confirm password',
}

export class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string) {
    super(message)
  }
}

export async function api<T>(path: string, method = 'GET', data?: unknown, signal?: AbortSignal): Promise<T> {
  if (method !== 'GET' && !csrfToken()) await fetch('/api/session/', { cache: 'no-store' })
  const response = await fetch('/api' + path, {
    method, signal, credentials: 'same-origin', cache: 'no-store',
    headers: method === 'GET' ? {} : { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
    body: data === undefined ? undefined : JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    const message = error && (typeof error.detail === 'string' ? error.detail : Object.entries(error)
      .filter(([key]) => key !== 'code' || error.code !== 'authentication_required')
      .map(([key, value]) => (Array.isArray(error) || key === 'non_field_errors' ? '' : (fieldNames[key] ?? key) + ': ') + [value].flat().join(' '))
      .join('\n'))
    if (error?.code === 'authentication_required') window.dispatchEvent(new Event('medresearch-session-expired'))
    throw new ApiError(message || (response.status === 403 ? 'Your session could not authorize this action. Reload and try again.' : 'The request failed. Try again.'), response.status, error?.code)
  }
  if (response.status === 204) return undefined as T
  return (response.headers.get('content-type')?.startsWith('text/plain') ? await response.text() : await response.json()) as T
}

export function searchLink(q: string, options: Record<string, string> = {}) {
  return '/search?' + new URLSearchParams({ q, ...options })
}

export const styles = { apa: 'APA', mla: 'MLA', vancouver: 'Vancouver', bibtex: 'BibTeX', ris: 'RIS' } as const
export type Style = keyof typeof styles
