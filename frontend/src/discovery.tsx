import { useEffect, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, ArrowUpRight, BookOpen, ListFilter, Plus, X } from 'lucide-react'
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api, searchLink, type Article, type HistoryEntry, type SearchResult } from './api'
import { AddToCollection, ArticleCard, Busy, CitationTools, Empty, ErrorNote, PageTitle, SaveArticle, SearchBox, SelectField, useSession } from './ui'

const topics = ['Large language models in healthcare','Electronic health records','Clinical natural language processing','Retrieval augmented generation','Type 2 diabetes','Cardiovascular disease','Cancer immunotherapy']
export function Home() {
  const user = useSession().data?.user
  const reviews = useQuery({queryKey:['featured'],queryFn:() => api<SearchResult>('/search/?q=systematic%20review%5Bpt%5D&sort=publication&size=10')})
  const history = useQuery({queryKey:['history',user?.id],enabled:!!user,queryFn:() => api<HistoryEntry[]>('/history/')})
  return <main>
    <section className="hero"><div className="hero-orbit" aria-hidden="true"/><div className="shell hero-inner">
      <div className="source"><span/> LIVE PUBMED DATA</div>
      <h1>Biomedical literature.<br/><em>Within reach.</em></h1>
      <p>Search PubMed, explore the evidence, and organize the publications that matter to your work.</p>
      <SearchBox large/><Link className="advanced-link" to="/advanced"><ListFilter size={17}/> Advanced search <ArrowRight size={15}/></Link>
    </div></section>
    <div className="shell home-content"><section className="topics"><h2>Explore research topics</h2><div>
      {topics.map(term => <Link key={term} to={searchLink(term)} state={{record:true}}>{term}<ArrowUpRight size={14}/></Link>)}
    </div></section>
    <div className="home-grid"><section><div className="section-heading"><div className="section-icon"><BookOpen size={20}/></div><div><h2>Recently published reviews</h2><p>Systematic reviews from PubMed, ordered by publication date.</p></div></div>
      {reviews.isPending && <Busy>Retrieving publications…</Busy>}<ErrorNote error={reviews.error}/>
      {reviews.data?.results.slice(0,4).map(article => <ArticleCard article={article} key={article.pmid} compact/>)}
      {reviews.data?.results.length === 0 && <Empty>No reviews were returned.</Empty>}
      <Link className="text-link" to={searchLink('systematic review[pt]',{sort:'publication'})} state={{record:true}}>Browse reviews <ArrowRight size={15}/></Link>
    </section><aside className="stack">
      <div className="side-card stack"><h2>Research library</h2><p>Keep articles and citations together in collections.</p><Link className="button secondary" to="/collections">Browse collections <ArrowRight size={15}/></Link></div>
      {user && <div className="side-card stack"><h2>Recent searches</h2><ErrorNote error={history.error}/>{history.data?.slice(0,4).map(item => <Link key={item.id} to={searchLink(item.query,{...item.filters,sort:item.sort})} state={{record:true}}>{item.query}</Link>)}{history.data?.length === 0 && <p>Your searches will appear here.</p>}</div>}
    </aside></div></div>
  </main>
}

const choices = (values:string[]) => Object.fromEntries(values.map(value => [value,value]))
const filters: Record<string,{title:string;options:Record<string,string>}> = {
  years:{title:'Publication date',options:{'1':'Last 1 year','5':'Last 5 years','10':'Last 10 years'}},
  type:{title:'Article type',options:choices(['Clinical Trial','Randomized Controlled Trial','Review','Systematic Review','Meta-Analysis','Case Report'])},
  text:{title:'Text availability',options:{abstract:'Abstract available',free:'Free full text',full:'Full text available'}},
  language:{title:'Language',options:choices(['English','Chinese','French','German','Japanese','Spanish','Portuguese'])},
  species:{title:'Species',options:{humans:'Humans',animals:'Other animals'}},
  subset:{title:'Indexing',options:{medline:'MEDLINE','no-preprints':'Exclude preprints'}},
}

export function SearchPage() {
  const [params,setParams] = useSearchParams()
  const location = useLocation()
  const navigate = useNavigate()
  const client = useQueryClient()
  const user = useSession().data?.user
  const serialized = params.toString()
  const query = params.get('q') ?? ''
  const page = Number(params.get('page') ?? 1)
  const size = Number(params.get('size') ?? 20)
  const [mobile,setMobile] = useState(false)
  const [selected,setSelected] = useState<string[]>([])
  const [saved,setSaved] = useState(false)
  const [recordError,setRecordError] = useState<unknown>(null)
  const result = useQuery({queryKey:['search',serialized],enabled:!!query,queryFn:({signal}) => api<SearchResult>('/search/?'+serialized,'GET',undefined,signal)})
  const save = useMutation({mutationFn:() => api('/saved-searches/','POST',Object.fromEntries(params)),onSuccess:() => {setSaved(true);void client.invalidateQueries({queryKey:['saved-searches']})}})
  useEffect(() => {setSelected([]);setSaved(false);setRecordError(null)},[serialized])
  useEffect(() => {
    if (!location.state?.record || !user || !result.data) return
    navigate(location.pathname+location.search,{replace:true,state:null})
    void api('/search/record/','POST',Object.fromEntries(new URLSearchParams(serialized)))
      .then(() => client.invalidateQueries({queryKey:['history']})).catch(setRecordError)
  },[location,user,result.data,serialized,navigate,client])
  function change(values:Record<string,string>,record=true) {
    const next = new URLSearchParams(params)
    next.delete('page')
    for (const [key,value] of Object.entries(values)) {
      if (value) next.set(key,value)
      else next.delete(key)
    }
    setParams(next,{state:{record}})
  }
  function toggle(key:string,value:string) {
    const current = params.get(key)?.split(',') ?? []
    const exists = current.includes(value)
    if (key === 'years') change({years:exists ? '' : value,from:'',to:''})
    else change({[key]:(exists ? current.filter(item => item !== value) : [...current,value]).join(',')})
  }
  const active = Object.entries(filters).flatMap(([key,{options}]) => (params.get(key)?.split(',') ?? []).map(value => ({key,value,label:options[value] ?? value})))
  const hasDates = params.has('from') || params.has('to')
  const pages = Math.ceil((result.data?.accessible_count ?? 0)/size)
  return <main className="shell page"><PageTitle title="Search literature"/><SearchBox initial={query}/>
    <Link className="text-link" to="/advanced"><ListFilter size={16}/> Advanced search</Link>
    {!query ? <Empty>Enter a keyword, author, PMID, or PubMed query to begin.</Empty> : <>
      <button className="button secondary mobile-filter" aria-expanded={mobile} onClick={() => setMobile(!mobile)}><ListFilter size={16}/> Filters</button>
      <div className="search-layout"><aside className={'filters'+(mobile?' show':'')} aria-label="Search filters">
        <div className="filter-heading"><h2>Filters</h2><button className="link-button" disabled={!active.length&&!hasDates} onClick={() => change(Object.fromEntries([...Object.keys(filters),'from','to'].map(key => [key,''])))}>Clear all</button></div>
        {Object.entries(filters).map(([key,filter]) => <details key={key} open={['years','type','text'].includes(key)||params.has(key)}>
          <summary>{filter.title}</summary><div className="filter-options">
            {Object.entries(filter.options).map(([value,label]) => <label className="checkbox" key={value}><input type="checkbox" checked={params.get(key)?.split(',').includes(value) ?? false} onChange={() => toggle(key,value)}/>{label}</label>)}
          </div>
          {key === 'years' && <form key={serialized} className="date-filter" onSubmit={event => {
            event.preventDefault();const data=new FormData(event.currentTarget)
            change({years:'',from:String(data.get('from')),to:String(data.get('to'))})
          }}><label>From<input name="from" type="date" defaultValue={params.get('from') ?? ''}/></label>
          <label>To<input name="to" type="date" defaultValue={params.get('to') ?? ''}/></label><button className="button secondary small">Apply dates</button></form>}
        </details>)}
      </aside><section className="search-results" aria-label="Publications">
        <div className="result-heading"><div><h2>{result.data ? result.data.count.toLocaleString()+' results':'Results'}</h2><p>for “{query}”</p></div><div className="actions">
          <SelectField label="Sort by" value={params.get('sort') ?? 'best'} options={{best:'Best match',recent:'Most recent',publication:'Publication date'}} onChange={sort => change({sort})}/>
          <SelectField label="Per page" value={String(size)} options={{10:'10',20:'20',50:'50'}} onChange={size => change({size},false)}/>
        </div></div>
        <div className="chips" aria-label="Active filters">{active.map(({key,value,label}) => <button className="chip" key={key+value} aria-label={'Remove '+label} onClick={() => toggle(key,value)}>{label}<X size={13}/></button>)}
        {hasDates && <button className="chip" onClick={() => change({from:'',to:''})}>{params.get('from')||'Any'} – {params.get('to')||'Any'}<X size={13}/></button>}</div>
        {result.isPending && <Busy>Searching PubMed…</Busy>}<ErrorNote error={result.error||save.error||recordError}/>
        {result.error && <button className="button secondary" onClick={() => void result.refetch()}>Retry search</button>}
        {result.data && <>
          <div className="result-tools">{result.data.translation && <details><summary>PubMed query translation</summary><pre className="query-preview">{result.data.translation}</pre></details>}
          {user && <button className="link-button" disabled={save.isPending||saved} onClick={() => save.mutate()}>{saved?'Search saved':'Save this search'}</button>}</div>
          {result.data.count>result.data.accessible_count && <p className="notice">PubMed exposes the first 10,000 matches. Refine terms or dates to browse a different subset.</p>}
          {result.data.partial && <p className="notice">PubMed returned incomplete metadata for this page.</p>}
          {!!selected.length && <div className="selection-bar"><span>{selected.length} selected</span><CitationTools source={{ids:selected}}/></div>}
          {result.data.results.map(article => <ArticleCard key={article.pmid} article={article} selected={selected.includes(article.pmid)} select={() => setSelected(items => items.includes(article.pmid)?items.filter(id=>id!==article.pmid):[...items,article.pmid])}/>)}
          {!result.data.results.length && <Empty>{result.data.count?'No metadata is available on this page.':'No publications match this search.'}</Empty>}
          {pages>1 && <nav className="pagination" aria-label="Results pages"><button className="button secondary" disabled={page<=1} onClick={() => change({page:String(page-1)},false)}>Previous</button><span>Page {page} of {pages}</span><button className="button secondary" disabled={page>=pages} onClick={() => change({page:String(page+1)},false)}>Next</button></nav>}
        </>}
      </section></div>
    </>}
  </main>
}

const fields={all:'All fields',title:'Title',author:'Author',journal:'Journal',abstract:'Abstract',mesh:'MeSH terms',date:'Publication date'}
const tags:Record<string,string>={title:'ti',author:'au',journal:'ta',abstract:'ab',mesh:'mh',date:'dp'}
type Row={id:number;field:string;operator:string;term:string}
export function AdvancedPage() {
  const [rows,setRows]=useState<Row[]>([{id:0,field:'all',operator:'AND',term:''}])
  const [saved,setSaved]=useState(false)
  const user=useSession().data?.user
  const navigate=useNavigate()
  const client=useQueryClient()
  const submit=useMutation({mutationFn:async(save:boolean)=>{
    const {query}=await api<{query:string}>('/advanced/','POST',{rows})
    if (save) {
      await api('/saved-searches/','POST',{q:query})
      await client.invalidateQueries({queryKey:['saved-searches']})
      setSaved(true)
    } else navigate(searchLink(query),{state:{record:true}})
  }})
  function edit(id:number,patch:Partial<Row>) {
    setSaved(false)
    setRows(items=>items.map(row=>row.id===id?{...row,...patch}:row))
  }
  function send(event:FormEvent<HTMLFormElement>) {
    event.preventDefault()
    submit.mutate((event.nativeEvent as SubmitEvent).submitter?.getAttribute('value')==='save')
  }
  const preview=rows.reduce((acc,row)=>{
    if (!row.term.trim()) return acc
    const term=row.field==='all'?row.term.trim():row.field==='date'?row.term.trim()+'[dp]':'"'+row.term.trim().replace(/^"+|"+$/g,'')+'"['+tags[row.field]+']'
    return acc?'('+acc+' '+row.operator+' ('+term+'))':'('+term+')'
  },'')
  return <main className="shell page narrow"><PageTitle title="Advanced search">Combine fields and Boolean operators to construct a PubMed query.</PageTitle><form className="panel stack" onSubmit={send}>
    <h2>Search conditions</h2>
    {rows.map((row,index)=><div className="condition" key={row.id}>
      {index>0?<SelectField label="Operator" options={choices(['AND','OR','NOT'])} value={row.operator} onChange={operator=>edit(row.id,{operator})}/>:<span/>}
      <SelectField label="Field" options={fields} value={row.field} onChange={field=>edit(row.id,{field})}/>
      <label>Search term<input required maxLength={2500} value={row.term} onChange={event=>edit(row.id,{term:event.target.value})} placeholder={'e.g. ("large language models" OR LLM)'}/></label>
      <button className="icon-button" type="button" aria-label={'Remove condition '+(index+1)} disabled={rows.length===1} onClick={()=>setRows(items=>items.filter(item=>item.id!==row.id))}><X size={18}/></button>
    </div>)}
    <button type="button" className="button secondary align-start" disabled={rows.length>=20} onClick={()=>setRows(items=>[...items,{id:Math.max(...items.map(item=>item.id))+1,field:'all',operator:'AND',term:''}])}><Plus size={16}/> Add condition</button>
    <div><h2>Query preview</h2><pre className="query-preview">{preview||'Enter a term to preview the query.'}</pre></div>
    <ErrorNote error={submit.error}/>{saved&&<p role="status">Search saved.</p>}
    <div className="actions"><button className="button primary" disabled={submit.isPending}>Search PubMed</button>{user&&<button className="button secondary" value="save" disabled={submit.isPending||saved}>Save search</button>}</div>
  </form></main>
}

function Relationships({pmid,kind}:{pmid:string;kind:'related'|'cited-by'}) {
  const result=useQuery({queryKey:[kind,pmid],queryFn:()=>api<{results:Article[]}>('/publications/'+pmid+'/'+kind+'/')})
  return <section className="detail-section"><h2>{kind==='related'?'Similar publications':'Cited by'}</h2>
    {result.isPending&&<Busy/>}<ErrorNote error={result.error}/>
    {result.data?.results.map(article=><ArticleCard key={article.pmid} article={article} compact/>)}
    {result.data?.results.length===0&&<p className="muted">PubMed returned no publications for this relationship.</p>}
  </section>
}

export function ArticlePage() {
  const {pmid}=useParams()
  const result=useQuery({queryKey:['article',pmid],queryFn:()=>api<Article>('/publications/'+encodeURIComponent(pmid??'')+'/')})
  const item=result.data
  return <main className="shell page"><Link to="/search" className="text-link">← Literature search</Link>
    {result.isPending&&<Busy>Retrieving publication…</Busy>}<ErrorNote error={result.error}/>
    {item&&<><header className="detail-header"><div className="chips">{item.types?.map(type=><span className="chip" key={type}>{type}</span>)}</div>
      <h1>{item.title}</h1><p className="authors">{item.authors.map(author=>author.name).join(', ')}</p>
      <p className="metadata">{[item.journal,item.date,item.volume&&'Vol. '+item.volume,item.issue&&'Issue '+item.issue,item.pages&&'Pages '+item.pages].filter(Boolean).join(' · ')}</p>
      <p className="metadata">{['PMID '+item.pmid,item.pmcid,item.doi&&'DOI '+item.doi].filter(Boolean).join(' · ')}</p>
    </header><div className="detail-grid"><div>
      <section className="detail-section"><h2>Abstract</h2>{item.abstract?.length?item.abstract.map((section,index)=><p key={index}><strong>{section.label} </strong>{section.text}</p>):<p className="muted">An abstract is unavailable for this record.</p>}</section>
      {item.authors.some(author=>author.affiliations?.length)&&<section className="detail-section"><h2>Author affiliations</h2><ul>{item.authors.filter(author=>author.affiliations?.length).map((author,index)=><li key={index}><strong>{author.name}</strong> · {author.affiliations?.join(' · ')}</li>)}</ul></section>}
      {Object.entries({Keywords:item.keywords,'MeSH terms':item.mesh}).map(([label,values])=>!!values?.length&&<section className="detail-section" key={label}><h2>{label}</h2><div className="chips">{values.map((value,index)=><Link className="chip" key={index} to={searchLink('"'+value+'"'+(label==='MeSH terms'?'[mh]':''))} state={{record:true}}>{value}</Link>)}</div></section>)}
      {!!item.references?.length&&<section className="detail-section"><h2>References</h2><ol>{item.references.map((ref,index)=><li key={index}>{ref.pmid?<Link to={'/article/'+ref.pmid}>{ref.citation||'PMID '+ref.pmid}</Link>:ref.citation}</li>)}</ol></section>}
      <Relationships pmid={item.pmid} kind="related"/><Relationships pmid={item.pmid} kind="cited-by"/>
    </div><aside className="stack"><div className="side-card stack"><h2>Article actions</h2><SaveArticle pmid={item.pmid}/><AddToCollection pmid={item.pmid}/><CitationTools source={{ids:[item.pmid]}} copy/></div>
      <div className="side-card stack"><h2>Access</h2>
        {item.pmcid&&<a className="button primary" href={'https://pmc.ncbi.nlm.nih.gov/articles/'+encodeURIComponent(item.pmcid)+'/'} target="_blank" rel="noreferrer">Free full text in PMC <ArrowUpRight size={15}/></a>}
        {item.doi&&<a className="button secondary" href={'https://doi.org/'+encodeURI(item.doi)} target="_blank" rel="noreferrer">Publisher via DOI <ArrowUpRight size={15}/></a>}
        {!item.pmcid&&!item.doi&&<p className="muted">{item.abstract?.length?'Abstract-only record.':'Publication metadata available.'}</p>}
        <a className="text-link" href={'https://pubmed.ncbi.nlm.nih.gov/'+item.pmid+'/'} target="_blank" rel="noreferrer">Open in PubMed <ArrowUpRight size={15}/></a>
      </div>
    </aside></div></>}
  </main>
}
