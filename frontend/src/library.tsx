import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FolderClosed, Plus } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, searchLink, type Article, type Collection, type HistoryEntry } from './api'
import { ArticleCard, AuthGate, Busy, CitationTools, Confirm, Dialog, Empty, ErrorNote, PageTitle, SelectField, useSession } from './ui'

function values(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
  return Object.fromEntries(new FormData(event.currentTarget))
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
