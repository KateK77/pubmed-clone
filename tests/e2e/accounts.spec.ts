import { randomUUID } from 'node:crypto'
import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { expect, test, type Page } from '../../frontend/node_modules/@playwright/test/index.mjs'

const password = 'abcdefgh'

async function mailCode(email: string) {
  let code = ''
  await expect.poll(async () => {
    for (const file of await readdir(join(process.env.MEDRESEARCH_TEST_STATE!, 'mail'))) {
      const contents = await readFile(join(process.env.MEDRESEARCH_TEST_STATE!, 'mail', file), 'utf8')
      if (contents.includes('To: ' + email)) code = contents.match(/code is (\d{6})/)?.[1] ?? ''
    }
    return code.length
  }).toBe(6)
  return code
}

async function requestCode(page: Page, email: string) {
  await page.getByRole('button', { name: 'Send verification code' }).click()
  await expect(page.getByRole('status')).toContainText('A code was sent')
  return mailCode(email)
}

async function register(page: Page, checkIncorrectCode = false) {
  const username = 'browser-' + randomUUID().slice(0, 8)
  const email = username + '@example.org'
  await page.goto('/profile')
  await page.getByRole('button', { name: 'Create an account', exact: true }).click()
  await expect(page.getByText('Use 8–128 characters. No uppercase letters, numbers or symbols are required.')).toBeVisible()
  await page.getByLabel('Username', { exact: true }).fill(username)
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByLabel('Confirm password', { exact: true }).fill('different')
  await expect(page.getByRole('alert')).toContainText('Passwords do not match')
  await page.getByLabel('Confirm password', { exact: true }).fill(password)
  await expect(page.getByRole('alert')).toHaveCount(0)
  const code = await requestCode(page, email)
  if (checkIncorrectCode) {
    await page.getByLabel('Verification code', { exact: true }).fill(code === '000000' ? '111111' : '000000')
    await page.getByRole('button', { name: 'Verify and create account' }).click()
    await expect(page.getByRole('alert')).toContainText('Verification code: The verification code is incorrect.')
  }
  await page.getByLabel('Verification code', { exact: true }).fill(code)
  await page.getByRole('button', { name: 'Verify and create account' }).click()
  await expect(page).toHaveURL(/\/search$/)
  await page.goto('/profile')
  await expect(page.getByRole('heading', { name: username, exact: true })).toBeVisible()
  await expect(page.getByLabel('First name')).toHaveCount(0)
  await expect(page.getByLabel('Last name')).toHaveCount(0)
  await expect(page.getByText('Email verified.', { exact: true })).toBeVisible()
  return username
}

async function login(page: Page, username: string, destination = '/search', secret = password) {
  await page.getByLabel('Username', { exact: true }).fill(username)
  await page.getByLabel('Password', { exact: true }).fill(secret)
  await expect(page.getByLabel('Confirm password')).toHaveCount(0)
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page).toHaveURL('http://127.0.0.1:5417' + destination)
}

test('simple registration, verified email persistence, isolated cookies and session recovery', async ({ page, context }) => {
  const username = await register(page, true)
  await context.addCookies([{ name: 'sessionid', value: 'unrelated-local-app', url: 'http://127.0.0.1:5417' }])
  const savedEmail = username + '-saved@example.org'
  await page.getByLabel('Email', { exact: true }).fill(savedEmail)
  await page.getByLabel('Verification code').fill(await requestCode(page, savedEmail))
  await page.getByRole('button', { name: 'Save email', exact: true }).click()
  await expect(page.getByText('Email saved.', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByLabel('Email', { exact: true })).toHaveValue(savedEmail)
  await page.getByRole('button', { name: 'Sign out', exact: true }).click()
  await login(page, username)
  await page.goto('/profile')
  await expect(page.getByLabel('Email', { exact: true })).toHaveValue(savedEmail)
  const draftEmail = username + '-draft@example.org'
  await page.getByLabel('Email', { exact: true }).fill(draftEmail)
  const code = await requestCode(page, draftEmail)
  await page.getByLabel('Verification code').fill(code)
  await context.clearCookies({ name: 'medresearch_sessionid' })
  await page.getByRole('button', { name: 'Save email', exact: true }).click()
  await expect(page.getByText('Your unsaved email edit is kept', { exact: false })).toBeVisible()
  await expect(page.getByText('Email saved.', { exact: true })).toHaveCount(0)
  await login(page, username, '/profile')
  await expect(page.getByLabel('Email', { exact: true })).toHaveValue(draftEmail)
  await page.getByLabel('Verification code').fill(code)
  await page.getByRole('button', { name: 'Save email', exact: true }).click()
  await expect(page.getByText('Email saved.', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByLabel('Email', { exact: true })).toHaveValue(draftEmail)
})

test('password confirmation, return after login and private collection isolation', async ({ page, context }) => {
  const first = await register(page)
  await page.getByText('Change password', { exact: true }).click()
  await page.getByLabel('Current password', { exact: true }).fill(password)
  await page.getByLabel('New password', { exact: true }).fill('12345678')
  await page.getByLabel('Confirm password', { exact: true }).fill('wrong123')
  await expect(page.getByRole('alert')).toContainText('Passwords do not match')
  await page.getByRole('button', { name: 'Update password' }).click()
  await expect(page.getByText('Password changed.')).toHaveCount(0)
  await page.getByLabel('Confirm password', { exact: true }).fill('12345678')
  await page.getByRole('button', { name: 'Update password' }).click()
  await expect(page.getByText('Password changed.', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Sign out', exact: true }).click()
  await page.goto('/saved?q=asthma&sort=title')
  await page.getByRole('link', { name: 'Go to sign in' }).click()
  await login(page, first, '/saved?q=asthma&sort=title', '12345678')
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
