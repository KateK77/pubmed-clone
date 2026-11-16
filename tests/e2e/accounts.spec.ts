import { randomUUID } from 'node:crypto'
import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { expect, test, type Page } from '../../frontend/node_modules/@playwright/test/index.mjs'

const password = 'ResearchBrowser!9376'

async function register(page: Page, checkIncorrectCode = false) {
  const username = 'browser-' + randomUUID().slice(0, 8)
  const email = username + '@example.org'
  await page.goto('/profile')
  await page.getByRole('button', { name: 'Create an account', exact: true }).click()
  await page.getByLabel('Username', { exact: true }).fill(username)
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Send verification code' }).click()
  await expect(page.getByRole('status')).toContainText('A code was sent')
  let code = ''
  await expect.poll(async () => {
    const directory = join(process.env.MEDRESEARCH_TEST_STATE!, 'mail')
    for (const file of await readdir(directory)) {
      const contents = await readFile(join(directory, file), 'utf8')
      if (contents.includes('To: ' + email)) code = contents.match(/code is (\d{6})/)?.[1] ?? ''
    }
    return code.length
  }).toBe(6)
  if (checkIncorrectCode) {
    await page.getByLabel('Verification code', { exact: true }).fill(code === '000000' ? '111111' : '000000')
    await page.getByRole('button', { name: 'Verify and create account' }).click()
    await expect(page.getByRole('alert')).toContainText('Verification code: The verification code is incorrect.')
  }
  await page.getByLabel('Verification code', { exact: true }).fill(code)
  await page.getByRole('button', { name: 'Verify and create account' }).click()
  await expect(page.getByRole('heading', { name: username, exact: true })).toBeVisible()
  await expect(page.getByText('Email verified.', { exact: true })).toBeVisible()
  return username
}

async function login(page: Page, username: string) {
  await page.getByLabel('Username', { exact: true }).fill(username)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('heading', { name: username, exact: true })).toBeVisible()
}

test('verified registration, real profile persistence, isolated cookies and session recovery', async ({ page, context }) => {
  const username = await register(page, true)
  await context.addCookies([{ name: 'sessionid', value: 'unrelated-local-app', url: 'http://127.0.0.1:5417' }])
  await page.getByLabel('First name', { exact: true }).fill('Test')
  await page.getByRole('button', { name: 'Save profile', exact: true }).click()
  await expect(page.getByText('Profile saved.', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByLabel('First name', { exact: true })).toHaveValue('Test')
  await page.getByRole('button', { name: 'Sign out', exact: true }).click()
  await login(page, username)
  await expect(page.getByLabel('First name', { exact: true })).toHaveValue('Test')
  await page.getByLabel('First name', { exact: true }).fill('Recoverable draft')
  await context.clearCookies({ name: 'medresearch_sessionid' })
  await page.getByRole('button', { name: 'Save profile', exact: true }).click()
  await expect(page.getByText('Your unsaved profile edits are kept', { exact: false })).toBeVisible()
  await expect(page.getByText('Profile saved.', { exact: true })).toHaveCount(0)
  await login(page, username)
  await expect(page.getByLabel('First name', { exact: true })).toHaveValue('Recoverable draft')
  await page.getByRole('button', { name: 'Save profile', exact: true }).click()
  await expect(page.getByText('Profile saved.', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByLabel('First name', { exact: true })).toHaveValue('Recoverable draft')
})

test('profile validation labels and collection isolation across real accounts', async ({ page, context }) => {
  const first = await register(page)
  await page.route('**/api/profile/', route => route.fulfill({ status: 400, json: { first_name: ['Validation fixture error.'] } }))
  await page.getByLabel('First name', { exact: true }).fill('Invalid')
  await page.getByRole('button', { name: 'Save profile' }).click()
  await expect(page.getByRole('alert')).toContainText('First name: Validation fixture error.')
  await expect(page.getByText('Profile saved.', { exact: true })).toHaveCount(0)
  await page.unroute('**/api/profile/')
  await page.getByLabel('First name', { exact: true }).fill('Valid')
  await expect(page.getByRole('alert')).toHaveCount(0)
  await page.getByRole('button', { name: 'Save profile' }).click()
  await expect(page.getByText('Profile saved.', { exact: true })).toBeVisible()
  await page.getByLabel('First name', { exact: true }).fill('Edited again')
  await expect(page.getByText('Profile saved.', { exact: true })).toHaveCount(0)
  await page.goto('/collections')
  await page.getByRole('button', { name: 'New collection' }).click()
  await page.getByLabel('Collection name').fill('Private collection ' + first)
  await page.getByRole('button', { name: 'Create collection', exact: true }).click()
  await page.getByRole('link', { name: 'Private collection ' + first, exact: false }).click()
  const collectionUrl = page.url()
  await context.clearCookies()
  await register(page)
  await page.goto(collectionUrl)
  await expect(page.getByRole('alert')).toContainText('No Collection matches')
  await expect(page.getByRole('heading', { name: 'Private collection ' + first })).toHaveCount(0)
})
