/** Infrastructure hooks only. No model calls, selectors, browser tasks, or verdicts. */
import { spawn } from 'node:child_process'
import { readFile, writeFile, mkdir, appendFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createConnection } from 'node:net'

const HERE = dirname(fileURLToPath(import.meta.url))
const SCRIPT = join(HERE, 'environment.py')
const RUNTIME = join(HERE, '.runtime')
const COMMIT = '03a7dc2a349a3f26bc1712c79d77957cf9338a1a'
const childrenKey = Symbol('evaluation-owned-children')
const supported = new Set(['anonymous', 'empty_database', 'synthetic_accounts',
  'empty_private_collections', 'live_ncbi', 'email_file_mailbox', 'authenticated',
  'seeded_library', 'seeded_history', 'seeded_saved_searches', 'demo_account', 'email_unavailable', 'trusted_browser_navigation', 'smtp_mailbox'])

function childEnv() {
  const result = { ...process.env, PYTHONUNBUFFERED: '1' }
  for (const key of Object.keys(result)) {
    if (/^(OPENAI_|POSTGRES_|DJANGO_|EMAIL_|NCBI_|RENDER_)/.test(key) ||
        ['DATABASE_URL', 'DEFAULT_FROM_EMAIL'].includes(key)) delete result[key]
  }
  return result
}

function processChild(python, args, logFile, extraEnv = {}) {
  const child = spawn(python, ['-u', SCRIPT, ...args], {
    windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'], env: { ...childEnv(), ...extraEnv },
  })
  let spawnError
  child.on('error', error => { spawnError = error })
  const pendingLogs = []
  const record = chunk => pendingLogs.push(appendFile(logFile, chunk).catch(() => {}))
  child.stdout.on('data', record)
  child.stderr.on('data', record)
  return { child, get error() { return spawnError }, logFile,
    async flushed() { await Promise.all(pendingLogs) } }
}

async function stop(process) {
  if (!process) return
  const { child } = process
  if (child.exitCode === null && child.signalCode === null && !process.error) {
    await new Promise(resolveStop => {
      child.once('close', resolveStop)
      child.kill('SIGTERM') // Only the direct ChildProcess object created here.
      setTimeout(() => {
        if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL')
        resolveStop()
      }, 5000).unref()
    })
  }
  await process.flushed()
}

async function command(python, args, logFile, extraEnv = {}) {
  const owned = processChild(python, args, logFile, extraEnv)
  await new Promise((ok, fail) => {
    const timer = setTimeout(() => { owned.child.kill('SIGTERM'); fail(new Error('Environment command timed out')) }, 90000)
    owned.child.once('error', error => { clearTimeout(timer); fail(error) })
    owned.child.once('close', code => {
      clearTimeout(timer)
      if (code === 0) ok()
      else fail(new Error(`Environment command exited ${code}; inspect sanitized setup log`))
    })
  })
  await owned.flushed()
}

async function waitReady(owned, url, predicate) {
  for (let attempt = 0; attempt < 60; attempt++) {
    if (owned.error) throw owned.error
    if (owned.child.exitCode !== null) throw new Error('Evaluation service exited during startup')
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1000) })
      if (response.ok && predicate(await response.text())) return
    } catch { /* bounded readiness wait, never a test retry */ }
    await new Promise(resolveWait => setTimeout(resolveWait, 250))
  }
  throw new Error('Evaluation service readiness timeout')
}

async function waitSMTP(owned) {
  for (let attempt = 0; attempt < 60; attempt++) {
    if (owned.error || owned.child.exitCode !== null) throw new Error('Local SMTP receiver exited')
    const ready = await new Promise(resolveReady => {
      const socket = createConnection({ host: '127.0.0.1', port: 8127 })
      socket.setTimeout(500)
      let done = false
      const finish = result => { if (!done) { done = true; socket.destroy(); resolveReady(result) } }
      socket.on('data', chunk => finish(chunk.toString().startsWith('220 ')))
      socket.on('error', () => finish(false))
      socket.on('timeout', () => finish(false))
    })
    if (ready) return
    await new Promise(resolveWait => setTimeout(resolveWait, 250))
  }
  throw new Error('Local SMTP receiver readiness timeout')
}

export function validateProfile(profile, test) {
  if (!profile || profile.ready !== true) return profile?.reason || 'No reviewed precondition profile for ' + test.id
  if (profile.reviewed_against_frozen_suite !== true) return 'Preconditions have not been explicitly reviewed against the frozen case'
  if (!['standard', 'mail', 'smtp', 'unavailable'].includes(profile.mode)) return 'Unsupported email mode'
  if (!['empty', 'accounts', 'demo'].includes(profile.fixture)) return 'Unsupported fixture'
  if (!Array.isArray(profile.requires)) return 'Precondition capabilities must be explicit'
  const unsupported = profile.requires.filter(key => !supported.has(key))
  if (unsupported.length) return 'Unsupported preconditions: ' + unsupported.join(', ')
  if (profile.requires.includes('empty_database') && profile.fixture !== 'empty') return 'Empty database conflicts with seeded accounts'
  if (profile.requires.some(key => ['synthetic_accounts', 'empty_private_collections'].includes(key)) && profile.fixture !== 'accounts') return 'Required synthetic accounts are not provisioned'
  if (profile.requires.includes('email_file_mailbox') && profile.mode !== 'mail') return 'Mailbox precondition requires mail mode'
  if (profile.requires.includes('smtp_mailbox') && profile.mode !== 'smtp') return 'SMTP capture precondition requires smtp mode'
  if (profile.requires.includes('demo_account') && profile.fixture !== 'demo') return 'Demo account precondition requires the explicit demo fixture'
  if (profile.requires.includes('email_unavailable') && profile.mode !== 'unavailable') return 'Unavailable-email precondition requires the unavailable mode'
  if (profile.auth_user && (!['eva_a', 'eva_b'].includes(profile.auth_user) || profile.fixture !== 'accounts')) return 'Unsupported preauthenticated user'
  if (profile.requires.includes('authenticated') && !profile.auth_user) return 'Authenticated precondition needs an explicit synthetic auth_user'
  if (profile.requires.includes('anonymous') && profile.auth_user) return 'Anonymous and authenticated preconditions conflict'
  if (profile.requires.some(key => ['seeded_library', 'seeded_history', 'seeded_saved_searches'].includes(key)) && (profile.fixture !== 'accounts' || !profile.seed_state_file)) return 'Seeded research preconditions require synthetic accounts and an explicit reviewed state file'
  if (typeof profile.start_path !== 'string' || !profile.start_path.startsWith('/') || profile.start_path.startsWith('//')) return 'An explicit local starting path is required'
  if (new URL(profile.start_path, 'http://127.0.0.1:8124').origin !== 'http://127.0.0.1:8124') return 'Starting path escapes the isolated origin'
  if (typeof profile.instructions !== 'string') return 'Reviewed precondition instructions are required'
  if (profile.viewport && (!Number.isInteger(profile.viewport.width) || !Number.isInteger(profile.viewport.height) || profile.viewport.width < 320 || profile.viewport.width > 1920 || profile.viewport.height < 480 || profile.viewport.height > 1440)) return 'Unsupported viewport dimensions'
  return null
}

export async function prepare({ test, config, run_directory }) {
  const owned = []
  if (!/^T\d{3}$/.test(test.id)) return { ready: false, reason: 'Invalid frozen test ID' }
  if (!config.environment_python || !config.preconditions_file) return { ready: false, reason: 'Local interpreter and reviewed case_preconditions mapping are required' }
  let mapping, profile, initialPassword
  try {
    mapping = JSON.parse(await readFile(resolve(config.preconditions_file), 'utf8'))
    if (mapping.suite_sha256 !== config.frozen_suite_sha256) return { ready: false, reason: 'Precondition mapping does not match the frozen suite hash' }
    profile = mapping.cases?.[test.id]
    const invalid = validateProfile(profile, test)
    if (invalid) return { ready: false, reason: invalid }
    if (['mail', 'smtp'].includes(profile.mode) && (!config.allowed_local_origins?.includes('http://127.0.0.1:8125') || config.mailbox_navigation_supported !== true)) {
      return { ready: false, reason: 'Mail preconditions require an explicitly allowlisted local mailbox origin and native CUA mailbox navigation support' }
    }
    if (profile.requires.includes('trusted_browser_navigation') && !config.allowed_local_origins?.includes('http://127.0.0.1:8126')) return { ready: false, reason: 'Trusted native navigation fixture origin is not explicitly allowlisted' }
    const manifest = JSON.parse(await readFile(join(RUNTIME, 'source-manifest.json'), 'utf8'))
    if (manifest.application_commit !== COMMIT) return { ready: false, reason: 'Prepared application revision mismatch' }
    if (new URL(config.base_url).origin !== 'http://127.0.0.1:8124') return { ready: false, reason: 'Environment origin must be http://127.0.0.1:8124' }
    if (profile.fixture === 'accounts') {
      if (!config.synthetic_credentials_file) return { ready: false, reason: 'Local-only synthetic AUTH.initial credentials fixture is not configured' }
      const privateFixture = JSON.parse(await readFile(resolve(config.synthetic_credentials_file), 'utf8'))
      initialPassword = privateFixture.initial_password
      if (typeof initialPassword !== 'string' || initialPassword.length < 8 || initialPassword.length > 128) return { ready: false, reason: 'Synthetic initial password fixture is invalid' }
    }
    if (profile.seed_state_file) {
      const seed = JSON.parse(await readFile(resolve(profile.seed_state_file), 'utf8'))
      if (seed.reviewed_preconditions !== true || seed.suite_sha256 !== config.frozen_suite_sha256) return { ready: false, reason: 'Private library seed does not match the reviewed frozen suite' }
    }
  } catch {
    return { ready: false, reason: 'Preconditions or pinned local source snapshot are unavailable; no setup or model request was attempted' }
  }
  const logs = join(resolve(run_directory), 'logs')
  await mkdir(logs, { recursive: true })
  const setupLog = join(logs, test.id + '-environment.log')
  const python = resolve(config.environment_python)
  try {
    await command(python, ['reset', '--case', test.id, '--mode', profile.mode, '--fixture', profile.fixture,
      ...(profile.auth_user ? ['--auth-user', profile.auth_user] : []),
      ...(profile.seed_state_file ? ['--state-file', resolve(profile.seed_state_file)] : [])], setupLog,
      initialPassword ? { EVALUATION_INITIAL_PASSWORD: initialPassword } : {})
    const beforeState = join(logs, test.id + '-state-before.json')
    await command(python, ['capture', '--case', test.id, '--output', beforeState], setupLog)
    if (profile.mode === 'smtp') {
      const smtp = processChild(python, ['smtp', '--case', test.id], setupLog)
      owned.push(smtp)
      await waitSMTP(smtp)
    }
    const app = processChild(python, ['serve', '--case', test.id], setupLog)
    owned.push(app)
    await waitReady(app, config.base_url + '/api/health/', body => {
      try { return JSON.parse(body).status === 'ok' } catch { return false }
    })
    const secrets = []
    const notes = [profile.instructions, 'Synthetic isolated local environment; only use data for this test.']
    if (profile.collection_targets?.length) {
      const state = JSON.parse(await readFile(beforeState, 'utf8'))
      for (const target of profile.collection_targets) {
        const owner = state.users.find(user => user.username === target.owner)
        const collection = state.collections.find(row => row.user_id === owner?.id && row.name === target.name)
        if (!collection) throw new Error('Required known collection target was not established by the fixture')
        notes.push(`${target.label}: ${config.base_url}/collections/${collection.id}; collection ID=${collection.id}. This URL was obtained solely from synthetic preconditions.`)
      }
    }
    const extraPages = []
    if (profile.fixture === 'accounts') {
      const credentials = JSON.parse(await readFile(join(RUNTIME, 'cases', test.id, 'credentials.local.json'), 'utf8'))
      for (const account of credentials) {
        secrets.push(account.password)
        notes.push(`Existing synthetic account: username=${account.username}; password=${account.password}; email=${account.email}.`)
      }
    }
    if (profile.fixture === 'demo') {
      const readme = await readFile(join(RUNTIME, 'source', 'README.md'), 'utf8')
      const demo = readme.match(/The local demo account is `([^`]+)` with password `([^`]+)`/)
      if (!demo) throw new Error('Delivered local demo credentials could not be located; do not guess them')
      secrets.push(demo[2])
      notes.push(`The pinned delivery README labels a local demo account: username=${demo[1]}, password=${demo[2]}. This excerpt is supplied as the documented local setup prerequisite, not proof that login works.`)
    }
    if (['mail', 'smtp'].includes(profile.mode)) {
      const mailbox = processChild(python, ['mail', '--case', test.id], setupLog)
      owned.push(mailbox)
      await waitReady(mailbox, 'http://127.0.0.1:8125/', body => body.includes('Isolated evaluation mailbox'))
      notes.push('A second tab is the synthetic local inbox at http://127.0.0.1:8125/. Use native Ctrl+Tab or Ctrl+Shift+Tab to switch between the application and inbox; refresh the inbox with Ctrl+R after requesting a code. Observe the message screenshot, then type the code yourself into the application. File delivery does not prove external SMTP.')
      if (profile.mode === 'smtp') notes.push('This case uses the real Django SMTP backend talking to an isolated loopback SMTP receiver. Captured messages demonstrate that SMTP transport, not external real-person inbox delivery.')
      extraPages.push('http://127.0.0.1:8125/')
    }
    let navigationStateFile
    if (profile.requires.includes('trusted_browser_navigation')) {
      navigationStateFile = join(RUNTIME, 'cases', test.id, 'browser-current-url.local.json')
      await writeFile(navigationStateFile, JSON.stringify({ url: new URL(profile.start_path, config.base_url).href }))
      await writeFile(join(RUNTIME, 'cases', test.id, 'navigation-config.local.json'), JSON.stringify({ external_hosts: config.external_hosts || [] }))
      const navigation = processChild(python, ['navigator', '--case', test.id], setupLog)
      owned.push(navigation)
      await waitReady(navigation, 'http://127.0.0.1:8126/', body => body.includes('Evaluation browser navigation'))
      extraPages.push('http://127.0.0.1:8126/')
      notes.push('A trusted evaluation navigation tab is open at http://127.0.0.1:8126/. Use native Ctrl+Tab to reach it, type the exact known URL into Destination URL and click Go or Open in new tab. It is browser infrastructure, not a product feature. Refresh it to read/copy the last observed application URL. Its clipboard pad accepts native Ctrl+V; do not type fabricated clipboard contents. All destination choices remain yours.')
    }
    const prepared = { ready: true, instructions: notes.join('\n'), secrets,
      start_url: new URL(profile.start_path, config.base_url).href,
      extra_pages: extraPages,
      ...(navigationStateFile ? { navigation_state_file: navigationStateFile } : {}),
      ...(profile.viewport ? { viewport: profile.viewport } : {}),
      evidence: [setupLog, beforeState], python, logs, case: test.id }
    if (profile.auth_user) {
      prepared.storage_state = JSON.parse(await readFile(join(RUNTIME, 'cases', test.id, 'browser-state.local.json'), 'utf8'))
      secrets.push(...prepared.storage_state.cookies.map(cookie => cookie.value))
      prepared.instructions += `\nThe isolated browser begins authenticated as ${profile.auth_user}; this is synthetic precondition setup, not evidence that the login workflow passed.`
    }
    prepared[childrenKey] = owned
    return prepared
  } catch (error) {
    for (const child of owned.reverse()) await stop(child)
    return { ready: false, reason: 'Environment precondition setup failed: ' + error.message, evidence: [setupLog] }
  }
}

export async function verify({ test, prepared, result }) {
  const target = join(prepared.logs, test.id + '-state-after.json')
  await command(prepared.python, ['capture', '--case', test.id, '--output', target], join(prepared.logs, test.id + '-environment.log'))
  result.evidence.push(...prepared.evidence, target)
  // Independent human/agent review must compare frozen criteria to evidence.
  // A model's self-report or successful capture is never an automatic PASS.
  return undefined
}

export async function cleanup({ test, prepared }) {
  try {
    if (prepared.ready) {
      await command(prepared.python, ['capture', '--case', test.id, '--output', join(prepared.logs, test.id + '-state-cleanup.json')], join(prepared.logs, test.id + '-environment.log'))
    }
  } finally {
    for (const child of [...(prepared[childrenKey] || [])].reverse()) await stop(child)
  }
}
