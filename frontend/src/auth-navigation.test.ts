import { expect, test } from 'vitest'
import { signInDestination, signInLink } from './auth-navigation'

test('login returns to a permitted page with its search and hash intact', () => {
  const location = { pathname: '/search', search: '?q=asthma&type=Review&page=2', hash: '#results' }
  const link = signInLink(location)
  expect(signInDestination(link.slice(link.indexOf('?')))).toBe(location.pathname + location.search + location.hash)
  expect(signInDestination('?next=%2Farticle%2F31452104')).toBe('/article/31452104')
})

test.each(['', '/profile', '/api/auth/logout/', '//example.org', '/\\example.org', 'https://example.org', '/search\n', '/unknown'])(
  'untrusted or unhelpful login destination %s falls back to search', next => {
    expect(signInDestination('?next=' + encodeURIComponent(next))).toBe('/search')
  },
)
