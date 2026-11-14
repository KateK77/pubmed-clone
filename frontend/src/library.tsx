import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FolderClosed, Plus } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, searchLink, type Article, type Collection, type HistoryEntry, type User } from './api'
import { ArticleCard, AuthGate, Busy, CitationTools, Confirm, Dialog, Empty, ErrorNote, PageTitle, SelectField, useSession } from './ui'

function values(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
  return Object.fromEntries(new FormData(event.currentTarget))
}

export function Profile() {
  const session=useSession()
  const client=useQueryClient()
  const [register,setRegister]=useState(false)
  const [updated,setUpdated]=useState(false)
  const mutation=useMutation({mutationFn:({path,method,data}:{path:string;method:string;data?:unknown})=>api<{user:User|null}>(path,method,data),
    onSuccess:data=>{
      for (const key of ['bookmarks','collections','history','saved-searches']) client.removeQueries({queryKey:[key]})
      client.setQueryData(['session'],data)
      setUpdated(true)
    }})
  const user=session.data?.user
  return <main className="shell page narrow"><PageTitle title={user?'Profile':register?'Create an account':'Sign in'}/>
    <ErrorNote error={session.error||mutation.error}/>
    {session.isPending?<Busy/>:user?<div className="panel stack">
      <h2>{user.username}</h2>
      <form className="stack" key={user.id} onSubmit={event=>{
        const form=event.currentTarget
        mutation.mutate({path:'/profile/',method:'PATCH',data:values(event)},{onSuccess:()=>{
          const current=form.elements.namedItem('current_password') as HTMLInputElement
          const password=form.elements.namedItem('password') as HTMLInputElement
          current.value='';password.value=''
        }})
      }}>
        <label>First name<input name="first_name" defaultValue={user.first_name} autoComplete="given-name" maxLength={150}/></label>
        <label>Last name<input name="last_name" defaultValue={user.last_name} autoComplete="family-name" maxLength={150}/></label>
        <label>Email<input name="email" type="email" defaultValue={user.email} autoComplete="email"/></label>
        <details><summary>Change password</summary><div className="stack">
          <label>Current password<input name="current_password" type="password" autoComplete="current-password" maxLength={128}/></label>
          <label>New password<input name="password" type="password" autoComplete="new-password" maxLength={128}/></label>
        </div></details>
        <button className="button primary align-start" disabled={mutation.isPending}>Save profile</button>
      </form>{updated&&mutation.variables?.path==='/profile/'&&<p role="status">Profile saved.</p>}
      <button className="button secondary align-start" disabled={mutation.isPending} onClick={()=>mutation.mutate({path:'/auth/logout/',method:'POST'})}>Sign out</button>
    </div>:<form className="panel stack" onSubmit={event=>mutation.mutate({path:register?'/auth/register/':'/auth/login/',method:'POST',data:values(event)})}>
      <label>Username<input name="username" autoComplete="username" required maxLength={150}/></label>
      {register&&<label>Email<input name="email" type="email" autoComplete="email"/></label>}
      <label>Password<input name="password" type="password" required maxLength={128} autoComplete={register?'new-password':'current-password'}/></label>
      <div className="actions"><button className="button primary" disabled={mutation.isPending}>{register?'Create account':'Sign in'}</button>
        <button type="button" className="link-button" onClick={()=>{setRegister(!register);mutation.reset()}}>{register?'Use an existing account':'Create an account'}</button></div>
    </form>}
  </main>
}

function LibraryItems({collection}:{collection?:number}) {
  const user=useSession().data?.user
  const client=useQueryClient()
  const navigate=useNavigate()
  const [q,setQ]=useState('')
  const [sort,setSort]=useState('added')
  const [rename,setRename]=useState(false)
  const [ids,setIds]=useState<string[]>([])
  const resource=collection?'/collections/'+collection+'/':'/bookmarks/'
  const params=new URLSearchParams({q,sort})
  const key=collection?'collections':'bookmarks'
  const result=useQuery({queryKey:[key,user?.id,resource+params],queryFn:()=>api<{results:Article[];name?:string;count?:number}>(resource+'?'+params)})
  const edit=useMutation({mutationFn:(name:FormDataEntryValue)=>api(resource,'PATCH',{name}),onSuccess:()=>{
    setRename(false);void client.invalidateQueries({queryKey:['collections']})
  }})
  async function remove(pmid:string) {
    await api(resource+(collection?'articles/':'')+pmid+'/','DELETE')
    setIds(previous=>previous.filter(id=>id!==pmid))
    await client.invalidateQueries({queryKey:[key]})
  }
  return <>
    {collection&&<><Link className="text-link" to="/collections">← All collections</Link><PageTitle title={result.data?.name??'Collection'}/>
      {result.data&&<div className="actions"><button className="button secondary" onClick={()=>{edit.reset();setRename(true)}}>Rename collection</button>
        <Confirm label="Delete collection" message={'Delete “'+result.data.name+'”?'} action={async()=>{
          await api(resource,'DELETE');await client.invalidateQueries({queryKey:['collections']});navigate('/collections')
        }}/></div>}
      {rename&&<Dialog title="Rename collection" onClose={()=>setRename(false)}><form className="stack" onSubmit={event=>edit.mutate(values(event).name)}>
        <label>Collection name<input name="name" defaultValue={result.data?.name} maxLength={120} required/></label>
        <ErrorNote error={edit.error}/><button className="button primary" disabled={edit.isPending}>Save name</button>
      </form></Dialog>}
    </>}
    <div className="library-tools"><label>Search articles<input type="search" value={q} onChange={event=>setQ(event.target.value)} placeholder="Title, journal, or PMID"/></label>
      <SelectField label="Sort by" options={{added:'Recently added',title:'Title',date:'Publication date'}} value={sort} onChange={setSort}/></div>
    {result.isPending&&<Busy/>}<ErrorNote error={result.error}/>
    {result.data&&<>
      {(result.data.results.length>0||q||ids.length>0)&&<div className="selection-bar"><span>{ids.length?ids.length+' selected':collection?'Export collection':'Export saved articles'}</span><CitationTools source={ids.length?{ids}:collection?{collection}:{bookmarks:true}}/></div>}
      {result.data.results.map(article=><ArticleCard key={article.pmid} article={article} selected={ids.includes(article.pmid)}
        select={()=>setIds(items=>items.includes(article.pmid)?items.filter(id=>id!==article.pmid):[...items,article.pmid])}
        action={<Confirm label="Remove article" message={'Remove “'+article.title+'” from '+(collection?'this collection?':'saved articles?')} action={()=>remove(article.pmid)}/>}/>)}
      {!result.data.results.length&&<Empty>{q?'No articles match your search.':collection?'Add publications from an article’s detail page.':'Save publications from their article detail pages.'}</Empty>}
    </>}
  </>
}

export function SavedPage() {
  return <main className="shell page"><PageTitle title="Saved articles"/><AuthGate><LibraryItems/></AuthGate></main>
}

function CollectionList() {
  const user=useSession().data?.user
  const client=useQueryClient()
  const [open,setOpen]=useState(false)
  const result=useQuery({queryKey:['collections',user?.id],queryFn:()=>api<{results:Collection[]}>('/collections/')})
  const create=useMutation({mutationFn:(name:FormDataEntryValue)=>api('/collections/','POST',{name}),onSuccess:()=>{
    setOpen(false);void client.invalidateQueries({queryKey:['collections']})
  }})
  return <><button className="button primary" onClick={()=>{create.reset();setOpen(true)}}><Plus size={17}/> New collection</button>
    {open&&<Dialog title="New collection" onClose={()=>setOpen(false)}><form className="stack" onSubmit={event=>create.mutate(values(event).name)}>
      <label>Collection name<input name="name" required maxLength={120}/></label>
      <ErrorNote error={create.error}/><button className="button primary" disabled={create.isPending}>Create collection</button>
    </form></Dialog>}
    {result.isPending&&<Busy/>}<ErrorNote error={result.error}/>
    {result.data?.results.length===0&&<Empty>Create a collection to organize your publications.</Empty>}
    <div className="collection-grid">{result.data?.results.map(item=><Link className="side-card stack" key={item.id} to={'/collections/'+item.id}><span className="section-icon"><FolderClosed size={20}/></span><h2>{item.name}</h2><p>{item.count} {item.count===1?'article':'articles'}</p></Link>)}</div>
  </>
}

export function CollectionsPage() {
  const {id}=useParams()
  return <main className="shell page">{!id&&<PageTitle title="Collections"/>}<AuthGate>{id?<LibraryItems key={id} collection={Number(id)}/>:<CollectionList/>}</AuthGate></main>
}

function HistoryLists() {
  const user=useSession().data?.user
  const client=useQueryClient()
  const history=useQuery({queryKey:['history',user?.id],queryFn:()=>api<HistoryEntry[]>('/history/')})
  const saved=useQuery({queryKey:['saved-searches',user?.id],queryFn:()=>api<HistoryEntry[]>('/saved-searches/')})
  const add=useMutation({mutationFn:(item:HistoryEntry)=>api('/saved-searches/','POST',{q:item.query,sort:item.sort,...item.filters}),
    onSuccess:()=>client.invalidateQueries({queryKey:['saved-searches']})})
  async function remove(key:string,id?:number) {
    await api('/'+key+'/'+(id?id+'/':''),'DELETE')
    await client.invalidateQueries({queryKey:[key]})
  }
  return <><ErrorNote error={history.error||saved.error||add.error}/>
    {[{title:'Recent searches',key:'history',data:history},{title:'Saved searches',key:'saved-searches',data:saved}].map(({title,key,data})=><section className="detail-section" key={key}>
      <div className="filter-heading"><h2>{title}</h2>{key==='history'&&!!data.data?.length&&<Confirm label="Clear history" message="Clear your search history?" action={()=>remove(key)}/>}</div>
      {data.isPending&&<Busy/>}{data.data?.length===0&&<Empty>{key==='history'?'Searches will appear here after you search while signed in.':'Save a query from your history or search results.'}</Empty>}
      {data.data?.map(item=><div className="history-row" key={item.id}><div>
        <Link to={searchLink(item.query,{...item.filters,sort:item.sort})} state={{record:true}}>{item.query}</Link>
        <p className="metadata">{new Date(item.created).toLocaleString()}{item.count!==undefined?' · '+item.count.toLocaleString()+' results':''}</p>
      </div><div className="actions">{key==='history'&&<button className="button secondary small" disabled={add.isPending||saved.data?.some(query=>query.query===item.query&&query.sort===item.sort&&JSON.stringify(query.filters)===JSON.stringify(item.filters))} onClick={()=>add.mutate(item)}>Save search</button>}
        <Confirm label="Remove" message={'Remove “'+item.query+'”?'} action={()=>remove(key,item.id)}/></div></div>)}
    </section>)}
  </>
}

export function HistoryPage() {
  return <main className="shell page"><PageTitle title="Search history"/><AuthGate><HistoryLists/></AuthGate></main>
}
