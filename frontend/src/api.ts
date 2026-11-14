export type Author = { name: string; affiliations?: string[] }
export type Article = {
  pmid: string; title: string; authors: Author[]; journal: string; year: string
  pmcid?: string; doi?: string; date?: string; volume?: string; issue?: string; pages?: string
  abstract?: { label: string; text: string }[]; keywords?: string[]; mesh?: string[]; types?: string[]
  references?: { citation: string; pmid: string }[]
}
export type SearchResult = { count: number; accessible_count: number; results: Article[]; partial: boolean; translation: string }
export type User = { id: number; username: string; email: string; first_name: string; last_name: string }
export type Collection = { id: number; name: string; count: number }
export type HistoryEntry = { id: number; query: string; sort: string; filters: Record<string, string>; created: string; count?: number }

function csrfToken() {
  return document.cookie.split('; ').find(cookie => cookie.startsWith('csrftoken='))?.slice(10) ?? ''
}

export async function api<T>(path: string, method = 'GET', data?: unknown, signal?: AbortSignal): Promise<T> {
  if (method !== 'GET' && !csrfToken()) await fetch('/api/session/', { cache: 'no-store' })
  const response = await fetch('/api' + path, {
    method, signal, credentials: 'same-origin',
    headers: method === 'GET' ? {} : { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
    body: data === undefined ? undefined : JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    const message = error && (typeof error.detail === 'string' ? error.detail : Object.values(error).flat().join(' '))
    throw new Error(message || (response.status === 403 ? 'Your session could not authorize this action. Reload and try again.' : 'The request failed. Try again.'))
  }
  if (response.status === 204) return undefined as T
  return (response.headers.get('content-type')?.startsWith('text/plain') ? await response.text() : await response.json()) as T
}

export function searchLink(q: string, options: Record<string, string> = {}) {
  return '/search?' + new URLSearchParams({ q, ...options })
}

export const styles = { apa: 'APA', mla: 'MLA', vancouver: 'Vancouver', bibtex: 'BibTeX', ris: 'RIS' } as const
export type Style = keyof typeof styles
