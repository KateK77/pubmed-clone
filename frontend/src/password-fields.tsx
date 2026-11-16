import { useRef, useState } from 'react'

export function PasswordFields({ id, label = 'Password' }: { id: string; label?: string }) {
  const password = useRef<HTMLInputElement>(null)
  const confirmation = useRef<HTMLInputElement>(null)
  const [mismatch, setMismatch] = useState(false)
  function compare() {
    const different = !!confirmation.current?.value && password.current?.value !== confirmation.current.value
    confirmation.current?.setCustomValidity(different ? 'Passwords do not match. Enter the same password in both fields.' : '')
    setMismatch(different)
  }
  return <>
    <label>{label}<input ref={password} name="password" type="password" required minLength={8} maxLength={128}
      autoComplete="new-password" aria-describedby={id + '-rules'} onChange={compare} /></label>
    <p id={id + '-rules'} className="muted password-help">Use 8–128 characters. No uppercase letters, numbers or symbols are required.</p>
    <label>Confirm password<input ref={confirmation} name="password_confirmation" type="password" required maxLength={128}
      autoComplete="new-password" aria-invalid={mismatch} aria-describedby={mismatch ? id + '-match' : undefined} onChange={compare} /></label>
    {mismatch && <p id={id + '-match'} className="notice error" role="alert">Passwords do not match. Enter the same password in both fields.</p>}
  </>
}
