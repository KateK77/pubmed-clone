import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowUpRight, Bookmark, BookOpen, ChevronDown, Clipboard, Download, FolderPlus, Search, X } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { signInLink } from './auth-navigation'
import { api, searchLink, styles, type Article, type Collection, type Style, type Session } from './api'

export function useSession() {
  return useQuery({ queryKey: ['session'], queryFn: ({ signal }) => api<Session>('/session/', 'GET', undefined, signal), staleTime: 0, refetchOnWindowFocus: true })
}

export function ErrorNote({ error }: { error: unknown }) {
  return error ? <p className="notice error" role="alert">{error instanceof Error ? error.message : 'Something went wrong. Try again.'}</p> : null
}

export function Busy({ children = 'Loading…' }: { children?: ReactNode }) {
  return <p className="loading" role="status"><span />{children}</p>
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty"><BookOpen size={23} /><p>{children}</p></div>
}

export function SearchBox({ initial = '', large = false }: { initial?: string; large?: boolean }) {
  const navigate = useNavigate()
  const [term, setTerm] = useState(initial)
  useEffect(() => setTerm(initial), [initial])
  function submit(event: FormEvent) {
    event.preventDefault()
    if (term.trim()) navigate(searchLink(term.trim()), { state: { record: true } })
  }
  return <form className={'searchbox' + (large ? ' searchbox-large' : '')} role="search" onSubmit={submit}>
    <Search aria-hidden="true" size={21} />
    <input aria-label="Search biomedical literature" placeholder="Search by keyword, title, author, PMID, or DOI" required maxLength={2500} value={term} onChange={event => setTerm(event.target.value)} />
    <button className="button primary" type="submit">Search</button>
  </form>
}

export function AuthGate({ children }: { children: ReactNode }) {
  const location = useLocation()
  const session = useSession()
  if (session.isPending) return <Busy />
  if (session.error) return <ErrorNote error={session.error} />
  return session.data?.user ? children : <Empty>Sign in to use your research library. <Link to={signInLink(location)}>Go to sign in</Link></Empty>
}

export function Dialog({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const element = ref.current
    element?.showModal()
    return () => element?.close()
  }, [])
  return <dialog ref={ref} aria-labelledby="dialog-title" onCancel={event => { event.preventDefault(); onClose() }}>
    <div className="dialog-heading"><h2 id="dialog-title">{title}</h2><button type="button" className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={20} /></button></div>
    {children}
  </dialog>
}

export function Confirm({ message, action, label = 'Delete' }: { message: string; action: () => Promise<unknown>; label?: string }) {
  const [open, setOpen] = useState(false)
  const mutation = useMutation({ mutationFn: action, onSuccess: () => setOpen(false) })
  return <><button type="button" className="button secondary small" onClick={() => { mutation.reset(); setOpen(true) }}>{label}</button>
    {open && <Dialog title={label} onClose={() => setOpen(false)}><p>{message}</p><ErrorNote error={mutation.error} />
      <div className="actions"><button className="button secondary" onClick={() => setOpen(false)}>Cancel</button><button className="button danger" disabled={mutation.isPending} onClick={() => mutation.mutate()}>{label}</button></div>
    </Dialog>}</>
}

export function CitationTools({ source, copy = false }: { source: { ids?: string[]; collection?: number; bookmarks?: boolean }; copy?: boolean }) {
  const [style, setStyle] = useState<Style>('apa')
  const [copied, setCopied] = useState(false)
  const mutation = useMutation({ mutationFn: async (action: 'copy' | 'download') => {
    setCopied(false)
    const result = await api<string>('/citations/', 'POST', { ...source, format: style })
    if (action === 'copy') {
      await navigator.clipboard.writeText(result.trim())
      setCopied(true)
    } else {
      const url = URL.createObjectURL(new Blob([result], { type: 'text/plain;charset=utf-8' }))
      const link = document.createElement('a')
      link.href = url
      link.download = 'medresearch.' + (style === 'bibtex' ? 'bib' : style === 'ris' ? 'ris' : 'txt')
      link.click()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    }
  } })
  return <div><div className="actions">
    <select aria-label="Citation format" value={style} onChange={event => { setStyle(event.target.value as Style); setCopied(false) }}>
      {Object.entries(styles).map(([key, name]) => <option key={key} value={key}>{name}</option>)}
    </select>
    {copy && <button className="button secondary" disabled={mutation.isPending} onClick={() => mutation.mutate('copy')}><Clipboard size={16} /> Copy citation</button>}
    <button className="button secondary" disabled={mutation.isPending || source.ids?.length === 0} onClick={() => mutation.mutate('download')}><Download size={16} /> Export {copy ? 'citation' : 'citations'}</button>
    {copied && <span role="status">Copied</span>}
  </div><ErrorNote error={mutation.error} /></div>
}

export function SaveArticle({ pmid }: { pmid: string }) {
  const location = useLocation()
  const user = useSession().data?.user
  const client = useQueryClient()
  const bookmarks = useQuery({ queryKey: ['bookmarks', user?.id, ''], enabled: !!user,
    queryFn: () => api<{ results: Article[] }>('/bookmarks/') })
  const saved = bookmarks.data?.results.some(article => article.pmid === pmid)
  const mutation = useMutation({ mutationFn: () => saved ? api('/bookmarks/' + pmid + '/', 'DELETE') : api('/bookmarks/', 'POST', { pmid }),
    onSuccess: () => client.invalidateQueries({ queryKey: ['bookmarks'] }) })
  if (!user) return <Link className="button secondary" to={signInLink(location)}><Bookmark size={16} /> Sign in to save</Link>
  return <div><button className="button secondary" disabled={mutation.isPending || bookmarks.isPending || !!bookmarks.error} onClick={() => mutation.mutate()}>
    <Bookmark size={16} fill={saved ? 'currentColor' : 'none'} /> {saved ? 'Remove saved article' : 'Save article'}
  </button><ErrorNote error={mutation.error || bookmarks.error} /></div>
}

export function AddToCollection({ pmid }: { pmid: string }) {
  const user = useSession().data?.user
  const client = useQueryClient()
  const [open, setOpen] = useState(false)
  const [selection, setSelection] = useState('')
  const collections = useQuery({ queryKey: ['collections', user?.id], enabled: !!user && open,
    queryFn: () => api<{ results: Collection[] }>('/collections/') })
  const mutation = useMutation({ mutationFn: () => api('/collections/' + selection + '/articles/', 'POST', { pmid }),
    onSuccess: () => { setOpen(false); void client.invalidateQueries({ queryKey: ['collections'] }) } })
  if (!user) return null
  return <><button className="button secondary" onClick={() => { mutation.reset(); setOpen(true) }}><FolderPlus size={16} /> Add to collection</button>
    {open && <Dialog title="Add to collection" onClose={() => setOpen(false)}>
      <ErrorNote error={collections.error || mutation.error} />
      {collections.isPending ? <Busy /> : collections.data?.results.length ? <form className="stack" onSubmit={event => { event.preventDefault(); mutation.mutate() }}>
        <label>Collection<select required value={selection} onChange={event => setSelection(event.target.value)}><option value="">Choose a collection</option>
          {collections.data.results.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <button className="button primary" disabled={mutation.isPending}>Add article</button>
      </form> : <p><Link to="/collections">Create a collection</Link> to organize articles.</p>}
    </Dialog>}</>
}

export function ArticleCard({ article, select, selected, action, compact = false }: { article: Article; select?: () => void; selected?: boolean; action?: ReactNode; compact?: boolean }) {
  const authors = article.authors.map(author => author.name)
  const preview = article.abstract?.map(section => section.text).join(' ')
  return <article className={'article-card' + (compact ? ' compact' : '')}>
    {select && <input type="checkbox" className="article-check" aria-label={'Select ' + article.title} onChange={select} checked={selected} />}
    <div className="article-content">
      {article.types?.[0] && <span className="eyebrow">{article.types[0]}</span>}
      <h3><Link to={'/article/' + article.pmid}>{article.title}</Link></h3>
      {authors.length > 0 && <p className="authors">{authors.slice(0, 4).join(', ')}{authors.length > 4 ? ', et al.' : ''}</p>}
      <p className="metadata">{[article.journal, article.year, 'PMID ' + article.pmid].filter(Boolean).join(' · ')}</p>
      {!compact && article.doi && <p className="metadata">DOI {article.doi}</p>}
      {!compact && preview && <p className="abstract-preview">{preview}</p>}
      {!compact && <p className="availability">{article.pmcid ? 'Free full text in PMC' : article.doi ? 'Publisher link' : article.abstract?.length ? 'Abstract available' : 'PubMed record'}</p>}
      {action}
    </div>
    {compact && <Link className="card-arrow" aria-label={'Open ' + article.title} to={'/article/' + article.pmid}><ArrowUpRight size={17} /></Link>}
  </article>
}

export function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: Record<string, string> }) {
  return <label className="select-field"><span>{label}</span><span className="select-wrap"><select value={value} onChange={event => onChange(event.target.value)}>{Object.entries(options).map(([key, name]) => <option key={key} value={key}>{name}</option>)}</select><ChevronDown size={14} aria-hidden="true" /></span></label>
}

export function PageTitle({ title, children }: { title: string; children?: ReactNode }) {
  return <header className="page-title"><h1>{title}</h1>{children && <p>{children}</p>}</header>
}
