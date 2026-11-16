import { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BookOpen, Menu, X } from 'lucide-react'
import { AdvancedPage, ArticlePage, Home, SearchPage } from './discovery'
import { CollectionsPage, HistoryPage, SavedPage } from './library'
import { Profile } from './profile'
import type { Session } from './api'
import { Empty, useSession } from './ui'
import './styles.css'

const links=[['/','Home'],['/search','Search'],['/advanced','Advanced Search'],['/saved','Saved Articles'],['/collections','Collections'],['/history','Search History']]
const client=new QueryClient({defaultOptions:{queries:{retry:false,staleTime:60_000,refetchOnWindowFocus:false}}})

function App() {
  const [open,setOpen]=useState(false)
  const [sessionExpired, setSessionExpired] = useState(false)
  const location=useLocation()
  const user=useSession().data?.user
  const previousUser = useRef<number | null | undefined>(undefined)
  useEffect(() => {
    function expired() {
      setSessionExpired(true)
      client.setQueryData<Session>(['session'], current => ({ ...current, user: null }))
    }
    window.addEventListener('medresearch-session-expired', expired)
    return () => window.removeEventListener('medresearch-session-expired', expired)
  }, [])
  useEffect(() => {
    if (previousUser.current !== undefined && previousUser.current !== user?.id) {
      for (const key of ['bookmarks', 'collections', 'history', 'saved-searches']) {
        void client.cancelQueries({ queryKey: [key, previousUser.current] })
        client.removeQueries({ queryKey: [key, previousUser.current] })
      }
    }
    previousUser.current = user?.id
    if (user) setSessionExpired(false)
  }, [user?.id])
  useEffect(()=>{setOpen(false);window.scrollTo(0,0)},[location.pathname])
  return <><a className="skip-link" href="#content">Skip to content</a>
    <header className="site-header"><div className="shell nav-shell">
      <Link to="/" className="brand"><span><BookOpen size={22}/></span>MedResearch</Link>
      <button className="icon-button menu" type="button" aria-label={open?'Close navigation':'Open navigation'} aria-controls="primary-nav" aria-expanded={open} onClick={()=>setOpen(!open)}>{open?<X/>:<Menu/>}</button>
      <nav id="primary-nav" className={open?'open':''} aria-label="Primary navigation">
        {links.map(([path,label])=><NavLink key={path} to={path} end={path==='/'}>{label}</NavLink>)}
        <NavLink className="profile-link" to="/profile">{user?'Profile':'Sign in'}</NavLink>
      </nav>
    </div></header>
    {sessionExpired && <p className="shell notice" role="alert">Your session has ended. <Link to="/profile">Sign in again</Link> to continue.</p>}
    <div id="content" tabIndex={-1}><Routes>
      <Route path="/" element={<Home/>}/><Route path="/search" element={<SearchPage/>}/><Route path="/advanced" element={<AdvancedPage/>}/>
      <Route path="/article/:pmid" element={<ArticlePage/>}/><Route path="/saved" element={<SavedPage/>}/>
      <Route path="/collections/:id?" element={<CollectionsPage/>}/><Route path="/history" element={<HistoryPage/>}/>
      <Route path="/profile" element={<Profile/>}/><Route path="*" element={<main className="shell page"><Empty>Page unavailable. <Link to="/">Go home</Link></Empty></main>}/>
    </Routes></div>
    <footer><div className="shell footer"><div><Link to="/" className="brand"><span><BookOpen size={19}/></span>MedResearch</Link><p>Independent research prototype. Literature provided by PubMed.</p></div>
      <div className="actions"><a href="https://pubmed.ncbi.nlm.nih.gov/">PubMed</a><a href="https://www.ncbi.nlm.nih.gov/books/NBK25501/">NCBI E-utilities</a><a href="/api/schema/">API schema</a></div>
    </div></footer>
  </>
}

createRoot(document.getElementById('root')!).render(<QueryClientProvider client={client}><BrowserRouter><App/></BrowserRouter></QueryClientProvider>)
