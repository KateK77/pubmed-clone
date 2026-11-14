import { expect, test } from '../../frontend/node_modules/@playwright/test/index.mjs'

const article = {
  pmid: '31452104', title: 'Fixture article', journal: 'Fixture journal', year: '2019',
  authors: [{ name: 'Ada Example' }], abstract: [{ label: 'Results', text: 'Fixture abstract.' }],
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/**', route => {
    const url = new URL(route.request().url())
    if (url.pathname === '/api/session/') return route.fulfill({ json: { user: null } })
    if (url.pathname === '/api/search/') {
      const isEmpty = url.searchParams.get('q') === 'no articles'
      return route.fulfill({ json: { count: isEmpty ? 0 : 41, accessible_count: isEmpty ? 0 : 41, results: isEmpty ? [] : [article], partial: false, translation: 'fixture' } })
    }
    if (url.pathname === '/api/publications/31452104/') return route.fulfill({ json: article })
    if (url.pathname.startsWith('/api/publications/31452104/')) return route.fulfill({ json: { results: [] } })
    if (url.pathname === '/api/advanced/') return route.fulfill({ json: { query: '(asthma)' } })
    return route.fulfill({ status: 404 })
  })
})

test('filter state, pagination, browser history, and article detail', async ({ page, isMobile }) => {
  await page.goto('/')
  await page.getByRole('search').getByRole('textbox').fill('asthma')
  await page.getByRole('button', { name: 'Search', exact: true }).click()
  await expect(page.getByRole('heading', { name: '41 results' })).toBeVisible()
  if (isMobile) await page.getByRole('button', { name: 'Filters', exact: true }).click()
  await page.getByText('Last 5 years', { exact: true }).click()
  await expect(page).toHaveURL(/years=5/)
  await page.getByText('Clinical Trial', { exact: true }).click()
  await expect(page).toHaveURL(/type=Clinical\+Trial/)
  await page.getByRole('button', { name: 'Clear all' }).click()
  await expect(page).toHaveURL(/\/search\?q=asthma$/)
  await page.goBack()
  await expect(page.getByRole('button', { name: 'Remove Clinical Trial' })).toBeVisible()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page).toHaveURL(/page=2/)
  await page.getByRole('link', { name: 'Fixture article' }).click()
  await expect(page.getByRole('heading', { name: 'Fixture article' })).toBeVisible()
  await expect(page.getByText('Fixture abstract.')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Similar publications' })).toBeVisible()
})

test('advanced builder and empty results', async ({ page }) => {
  await page.goto('/advanced')
  await page.getByRole('textbox', { name: 'Search term' }).first().fill('asthma')
  await page.getByRole('button', { name: 'Add condition' }).click()
  await page.getByLabel('Operator').selectOption('NOT')
  await page.getByLabel('Field').nth(1).selectOption('title')
  await page.getByRole('textbox', { name: 'Search term' }).nth(1).fill('preprint')
  await expect(page.getByText('((asthma) NOT ("preprint"[ti]))', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Search PubMed' }).click()
  await expect(page.getByRole('heading', { name: '41 results' })).toBeVisible()
  await page.goto('/search?q=no+articles')
  await expect(page.getByText('No publications match this search.')).toBeVisible()
})
