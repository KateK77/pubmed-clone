const permittedDestination = /^\/(?:search|advanced|saved|history|article\/[1-9]\d*|collections(?:\/[1-9]\d*)?)\/?$/

export function signInLink(location: { pathname: string; search: string; hash: string }) {
  return '/profile?next=' + encodeURIComponent(location.pathname + location.search + location.hash)
}

export function signInDestination(search: string) {
  const next = new URLSearchParams(search).get('next')
  if (!next || !next.startsWith('/') || next.startsWith('//') || /[\\\u0000-\u0020]/.test(next)) return '/search'
  const url = new URL(next, 'https://medresearch.invalid')
  return url.origin === 'https://medresearch.invalid' && permittedDestination.test(url.pathname)
    ? url.pathname + url.search + url.hash : '/search'
}
