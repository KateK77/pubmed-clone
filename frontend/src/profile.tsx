import { useEffect, useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import { signInDestination } from './auth-navigation'
import { PasswordFields } from './password-fields'
import { api, type Session, type User } from './api'
import { Busy, ErrorNote, PageTitle, useSession } from './ui'

type ProfileFields = Pick<User, 'email'>
type Draft = { userId: number; fields: ProfileFields }

function formData(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
  return Object.fromEntries(new FormData(event.currentTarget))
}

function EmailCode({ email, purpose, available, required, onCode }: {
  email: string; purpose: 'register' | 'profile'; available: boolean; required: boolean; onCode: (code: string) => void
}) {
  const [sentAt, setSentAt] = useState(0)
  const [waiting, setWaiting] = useState(false)
  useEffect(() => {
    if (!sentAt) return
    setWaiting(true)
    const timer = window.setTimeout(() => setWaiting(false), 60_000)
    return () => window.clearTimeout(timer)
  }, [sentAt])
  const request = useMutation({
    mutationFn: () => api<{ detail: string }>('/auth/email-code/', 'POST', { email, purpose }),
    onSuccess: () => {
      setSentAt(Date.now())
    },
  })
  return <div className="stack">
    {!available && <p className="notice">Email verification is awaiting the site operator’s email-service configuration.</p>}
    <div className="actions">
      <button type="button" className="button secondary" disabled={!available || !email || request.isPending || waiting}
        onClick={() => request.mutate()}>{request.isPending ? 'Sending…' : waiting ? 'Resend available in one minute' : sentAt ? 'Resend code' : 'Send verification code'}</button>
    </div>
    {request.isSuccess && <p role="status">A code was sent to {email}. It expires in 10 minutes.</p>}
    <ErrorNote error={request.error} />
    <label>Verification code<input name="code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6}
      required={required} onChange={event => onCode(event.target.value)} placeholder="6-digit code" /></label>
  </div>
}

function AccountForm({ session, onAuthenticated }: { session: Session; onAuthenticated: (user: User) => void }) {
  const [register, setRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const client = useQueryClient()
  const verification = !!session.email_verification_required
  const mutation = useMutation({
    mutationFn: (data: Record<string, FormDataEntryValue>) => api<Session>(register ? '/auth/register/' : '/auth/login/', 'POST', data),
    onSuccess: data => {
      client.setQueryData<Session>(['session'], current => ({ ...current, ...data }))
      if (data.user) onAuthenticated(data.user)
    },
  })
  function submit(event: FormEvent<HTMLFormElement>) {
    const data = formData(event)
    if (!code) delete data.code
    mutation.mutate(data)
  }
  return <>
    <PageTitle title={register ? 'Create an account' : 'Sign in'} />
    <form key={register ? 'register' : 'login'} className="panel stack" onSubmit={submit} onChange={() => mutation.reset()}>
      <fieldset className="stack form-fields" disabled={mutation.isPending}>
      <label>Username<input name="username" autoComplete={register ? 'section-signup username' : 'username'} required maxLength={150} /></label>
      {register && <label>Email<input name="email" type="email" autoComplete="section-signup email" required={verification}
        value={email} onChange={event => { setEmail(event.target.value); setCode('') }} /></label>}
      {register ? <PasswordFields id="signup" /> : <label>Password<input name="password" type="password" required maxLength={128} autoComplete="current-password" /></label>}
      {register && verification && <EmailCode key={email} email={email} purpose="register" available={!!session.email_delivery_available} required onCode={setCode} />}
      <ErrorNote error={mutation.error} />
      <div className="actions">
        <button className="button primary" disabled={mutation.isPending || (register && verification && !session.email_delivery_available)}>
          {mutation.isPending ? 'Please wait…' : register ? (verification ? 'Verify and create account' : 'Create account') : 'Sign in'}
        </button>
        <button type="button" className="link-button" onClick={() => { mutation.reset(); setCode(''); setRegister(!register) }}>
          {register ? 'Use an existing account' : 'Create an account'}
        </button>
      </div>
      </fieldset>
    </form>
  </>
}

function PasswordForm() {
  const [open, setOpen] = useState(false)
  const mutation = useMutation({ mutationFn: (data: Record<string, FormDataEntryValue>) => api('/profile/', 'PATCH', data) })
  return <details open={open} onToggle={event => setOpen(event.currentTarget.open)}>
    <summary>Change password</summary>
    {open && <form className="stack password-form" onChange={() => mutation.reset()} onSubmit={event => {
      const form = event.currentTarget
      mutation.mutate(formData(event), { onSuccess: () => form.reset() })
    }}>
      <fieldset className="stack form-fields" disabled={mutation.isPending}>
      <label>Current password<input name="current_password" type="password" required maxLength={128} autoComplete="current-password" /></label>
      <PasswordFields id="change-password" label="New password" />
      <ErrorNote error={mutation.error} />
      {mutation.isSuccess && <p role="status">Password changed.</p>}
      <button className="button secondary align-start" disabled={mutation.isPending}>Update password</button>
      </fieldset>
    </form>}
  </details>
}

function ProfileEditor({ user, session, draft, onDraft }: {
  user: User; session: Session; draft: Draft | null; onDraft: (draft: Draft | null) => void
}) {
  const client = useQueryClient()
  const [fields, setFields] = useState<ProfileFields>(() => draft?.userId === user.id ? draft.fields : {
    email: user.email,
  })
  const [code, setCode] = useState('')
  const [verify, setVerify] = useState(false)
  const emailChanged = fields.email.trim().toLowerCase() !== user.email.toLowerCase()
  const requiresCode = !!session.email_verification_required && emailChanged
  const save = useMutation({
    mutationFn: () => api<Session>('/profile/', 'PATCH', { ...fields, ...(code ? { code } : {}) }),
    onSuccess: data => {
      client.setQueryData<Session>(['session'], current => ({ ...current, ...data }))
      onDraft(null)
      setCode('')
      setVerify(false)
    },
  })
  const logout = useMutation({
    mutationFn: () => api<Session>('/auth/logout/', 'POST'),
    onSuccess: data => {
      onDraft(null)
      client.setQueryData<Session>(['session'], current => ({ ...current, ...data }))
    },
  })
  function edit(name: keyof ProfileFields, value: string) {
    const next = { ...fields, [name]: value }
    setFields(next)
    onDraft({ userId: user.id, fields: next })
    save.reset()
    if (name === 'email') setCode('')
  }
  return <>
    <PageTitle title="Account" />
    <div className="panel stack">
      <div><p className="muted">Username</p><h2>{user.username}</h2></div>
      <form className="stack" autoComplete="on" onSubmit={event => { event.preventDefault(); save.mutate() }}>
        <fieldset className="stack form-fields" disabled={save.isPending || logout.isPending}>
        <label>Email<input name="email" type="email" value={fields.email} onChange={event => edit('email', event.target.value)} autoComplete="section-profile email" /></label>
        {user.email_verified && !emailChanged && <p className="muted">Email verified.</p>}
        {!user.email_verified && !!fields.email && !verify && !requiresCode && <button type="button" className="link-button" onClick={() => setVerify(true)}>Verify this email</button>}
        {(requiresCode || verify) && <EmailCode key={fields.email} email={fields.email} purpose="profile" available={!!session.email_delivery_available}
          required={requiresCode || verify} onCode={value => { setCode(value); save.reset() }} />}
        <ErrorNote error={save.error} />
        {save.isSuccess && <p role="status">Email saved.</p>}
        <button className="button primary align-start" disabled={save.isPending}>{save.isPending ? 'Saving…' : 'Save email'}</button>
        </fieldset>
      </form>
      <PasswordForm />
      <ErrorNote error={logout.error} />
      <button className="button secondary align-start" disabled={logout.isPending || save.isPending} onClick={() => logout.mutate()}>Sign out</button>
    </div>
  </>
}

export function Profile() {
  const navigate = useNavigate()
  const location = useLocation()
  const session = useSession()
  const [draft, setDraft] = useState<Draft | null>(null)
  const user = session.data?.user
  return <main className="shell page narrow">
    <ErrorNote error={session.error} />
    {session.isPending ? <Busy /> : session.data && (user
      ? <ProfileEditor key={user.id} user={user} session={session.data} draft={draft} onDraft={setDraft} />
      : <>
        {draft && <p className="notice">Your unsaved email edit is kept while this page stays open. Sign in to the same account to continue.</p>}
        <AccountForm session={session.data} onAuthenticated={signedIn => {
          if (draft?.userId === signedIn.id) navigate('/profile', { replace: true })
          else {
            setDraft(null)
            navigate(signInDestination(location.search), { replace: true })
          }
        }} />
      </>)}
  </main>
}
