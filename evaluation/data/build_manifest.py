"""Independent NCBI fixture preparation only. Never imports or requests MedResearch."""
import argparse, datetime as dt, hashlib, json, os, re, time
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
import xml.etree.ElementTree as ET
import requests

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'rawcache'
ENDPOINT='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
QUERIES=['cancer','diabetes','clinical trial','journal article','"Jr"[Author]','"III"[Author]','"electronic publication"','"preprint"[Publication Type]']
META_FIELDS=['title','authors','affiliations','journal','publication_date','volume','issue','pages','pmid','pmcid','doi','abstract','keywords','mesh_terms','publication_types','full_text_links']
CATALOG=[]
LAST_REQUEST=0.0
CONTACT=os.getenv('NCBI_EMAIL','')
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(data): return hashlib.sha256(data).hexdigest()
def save(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def public_provenance(value):
    if isinstance(value,list):return[public_provenance(x) for x in value]
    if not isinstance(value,dict):return value
    cleaned={key:public_provenance(item) for key,item in value.items()}
    if 'request_parameters' in cleaned:
        cleaned['request_parameters']=[pair for pair in cleaned['request_parameters'] if pair[0]!='email']
        cleaned['redacted_request_parameters']=['email (operator contact; exact value retained only in ignored local cache)']
        parsed=urlsplit(cleaned['request_url']);cleaned['request_url']=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode([(k,v) for k,v in parse_qsl(parsed.query) if k!='email']),parsed.fragment))
    return cleaned
def text(node): return '' if node is None else ''.join(node.itertext()).strip()
def val(node,path): return text(node.find(path))
def obtain(kind,parameters):
    global LAST_REQUEST
    if not CONTACT:raise RuntimeError('Set the approved NCBI_EMAIL operator contact in the process environment; do not hardcode it into public artifacts')
    params=list(parameters)+[('tool','medresearch_final_evaluation'),('email',CONTACT)]
    encoded=urlencode(params)
    key=digest((kind+'?'+encoded).encode())[:20]
    file=RAW/(kind+'-'+key+'.xml'); meta=RAW/(kind+'-'+key+'.request.json')
    if file.exists() and meta.exists():
        record=json.loads(meta.read_text(encoding='utf-8'))
        payload=file.read_bytes()
        if digest(payload)!=record['sha256']: raise RuntimeError('Raw cache hash mismatch '+str(file))
    else:
        time.sleep(max(0,0.6-(time.monotonic()-LAST_REQUEST)))
        LAST_REQUEST=time.monotonic(); started=utc()
        response=requests.get(ENDPOINT+kind+'.fcgi',params=params,timeout=(10,30))
        payload=response.content
        record={'utility':kind,'request_parameters':params,'request_url':response.url,'retrieved_at_utc':started,'completed_at_utc':utc(),'http_status':response.status_code,'raw_file':str(file.relative_to(ROOT)).replace('\\','/'),'sha256':digest(payload),'bytes':len(payload)}
        file.write_bytes(payload);save(meta,record)
        response.raise_for_status()
    CATALOG.append(record)
    root=ET.fromstring(payload)
    errors=[text(e) for e in root.findall('.//ERROR')]
    if errors: raise RuntimeError('NCBI XML error: '+'; '.join(errors))
    return root,record
def parse_records(root,source):
    out={}
    for record in list(root):
        citation=record.find('MedlineCitation'); article=record.find('MedlineCitation/Article')
        if citation is None: citation=record.find('BookDocument');article=citation
        if citation is None or article is None:continue
        pmid=val(citation,'PMID')
        if not pmid.isdigit():continue
        authors=[]
        for a in article.findall('./AuthorList/Author'):
            authors.append({'last_name':val(a,'LastName'),'fore_name':val(a,'ForeName'),'initials':val(a,'Initials'),'suffix':val(a,'Suffix'),'collective_name':val(a,'CollectiveName'),'affiliations':[text(e) for e in a.findall('./AffiliationInfo/Affiliation')]})
        ids={a.get('IdType'):text(a) for a in record.findall('.//ArticleIdList/ArticleId')}
        doi=ids.get('doi') or next((text(e) for e in article.findall('./ELocationID') if e.get('EIdType')=='doi'),'')
        pubdate=article.find('./Journal/JournalIssue/PubDate')
        date={e.tag:text(e) for e in list(pubdate)} if pubdate is not None else {}
        abstract=[{'label':e.get('Label'),'category':e.get('NlmCategory'),'text':text(e)} for e in article.findall('./Abstract/AbstractText')]
        electronic=[{'source':'ArticleDate','date_type':e.get('DateType'),**{child.tag:text(child) for child in list(e)}} for e in article.findall('./ArticleDate') if (e.get('DateType') or '').lower()=='electronic']
        electronic += [{'source':'PubmedData/History','pub_status':e.get('PubStatus'),**{child.tag:text(child) for child in list(e)}} for e in record.findall('./PubmedData/History/PubMedPubDate') if e.get('PubStatus')=='epublish']
        refs=[{'citation':val(e,'Citation'),'ids':{i.get('IdType'):text(i) for i in e.findall('./ArticleIdList/ArticleId')}} for e in record.findall('.//ReferenceList/Reference')]
        row={'pmid':pmid,'record_kind':record.tag,'title':val(article,'ArticleTitle') or val(article,'Book/BookTitle'),'authors':authors,'journal':val(article,'Journal/Title') or val(article,'Book/BookTitle'),'journal_abbreviation':val(article,'Journal/ISOAbbreviation'),'publication_date':date,'year':date.get('Year') or (re.search(r'\b\d{4}\b',date.get('MedlineDate','')).group(0) if re.search(r'\b\d{4}\b',date.get('MedlineDate','')) else ''),'volume':val(article,'Journal/JournalIssue/Volume'),'issue':val(article,'Journal/JournalIssue/Issue'),'pages':val(article,'Pagination/MedlinePgn'),'doi':doi,'pmcid':ids.get('pmc',''),'publication_types':[text(e) for e in article.findall('./PublicationTypeList/PublicationType')],'languages':[text(e) for e in article.findall('./Language')],'abstract':abstract,'keywords':[text(e) for e in citation.findall('./KeywordList/Keyword')],'mesh':[text(e) for e in citation.findall('./MeshHeadingList/MeshHeading/DescriptorName')],'references':refs,'electronic_dates':electronic,'source_response_sha256':source['sha256'],'source_raw_file':source['raw_file'],'record_xml_serialization_sha256':digest(ET.tostring(record,encoding='utf-8'))}
        row['presence']={f:bool(row.get({'affiliations':'authors','mesh_terms':'mesh'}.get(f,f))) for f in META_FIELDS}
        row['presence']['affiliations']=any(a['affiliations'] for a in authors)
        row['presence']['abstract']=any(s['text'] for s in abstract)
        out[pmid]=row
    return out
def public(row):
    value={k:v for k,v in row.items() if k not in ['abstract','references']}
    value['abstract_section_count']=len(row['abstract']);value['abstract_sha256']=digest(json.dumps(row['abstract'],sort_keys=True,ensure_ascii=False).encode())
    value['reference_count']=len(row['references']);value['reference_pmids']=[r['ids']['pubmed'] for r in row['references'] if r['ids'].get('pubmed')]
    return value
def mincover(rows,fields,predicate):
    masks={}
    for row in rows:
        mask=sum(1<<i for i,f in enumerate(fields) if predicate(row,f))
        if mask and (mask not in masks or int(row['pmid'])<int(masks[mask])):masks[mask]=row['pmid']
    dp={0:()}
    for mask,pmid in sorted(masks.items(),key=lambda pair:int(pair[1])):
        for existing,sequence in list(dp.items()):
            union=existing|mask; candidate=tuple(sorted(sequence+(int(pmid),)))
            if union not in dp or (len(candidate),candidate)<(len(dp[union]),dp[union]):dp[union]=candidate
    target=(1<<len(fields))-1
    if target not in dp:return None
    return [str(n) for n in dp[target]]
def slot(rows,predicate,description):
    eligible=[r for r in rows if predicate(r)]
    if not eligible:return{'status':'missing','pmid':None,'predicate':description,'reason':'No qualifying record in frozen bounded candidate pool'}
    chosen=min(eligible,key=lambda r:int(r['pmid']))
    return {'status':'ready','pmid':chosen['pmid'],'predicate':description,'metadata':public(chosen)}
def build(baseline_only=False):
    RAW.mkdir(parents=True,exist_ok=True)
    root,source=obtain('efetch',[('db','pubmed'),('id','31452104'),('retmode','xml')]);base=parse_records(root,source).get('31452104')
    if not base:raise RuntimeError('BASE is absent from official EFetch')
    save(ROOT/'baseline.json',public_provenance({'status':'ready','pmid':'31452104','metadata':public(base),'source':source}))
    if baseline_only:return
    candidates={};queries=[]
    for rank,q in enumerate(QUERIES):
        root,source=obtain('esearch',[('db','pubmed'),('term',q),('retmax','200'),('retstart','0'),('sort','pub_date'),('retmode','xml')])
        ids=[text(e) for e in root.findall('./IdList/Id')];queries.append({'query':q,'rank':rank,'count':int(val(root,'Count')),'pmids':ids,'source':source})
        for pmid in ids:candidates.setdefault(pmid,[]).append(rank)
        print('ESearch',rank+1,len(ids),flush=True)
    records={};ids=sorted(candidates,key=int)
    for start in range(0,len(ids),200):
        root,source=obtain('efetch',[('db','pubmed'),('id',','.join(ids[start:start+200])),('retmode','xml')]);records.update(parse_records(root,source));print('EFetch',start+len(ids[start:start+200]),'of',len(ids),flush=True)
    for pmid,row in records.items():row['candidate_query_ranks']=candidates[pmid]
    save(RAW/'candidate-metadata-full.json',records)
    rows=[records[p] for p in ids if p in records]
    manifest={'manifest_version':1,'created_at_utc':utc(),'purpose':'Independent official PubMed fixture oracle; no application or CUA test execution','candidate_contract':{'queries':QUERIES,'per_query_retmax':200,'sort_semantics':'descending publication date','sort_parameter':'pub_date','sort_alias_clarification':'M1 pub date is mapped to the current official documented pub_date parameter','selection_order':'numeric PMID ascending; duplicates use earliest fixed query rank'},'candidate_count':len(ids),'parsed_record_count':len(rows),'missing_fetch_pmids':[p for p in ids if p not in records],'queries':queries,'BASE':{'status':'ready','pmid':'31452104','predicate':'fixed authoritative baseline','metadata':public(base)}}
    predicates={
      'DOI':(lambda r:bool(r['doi']),'nonempty structured DOI identifier'),
      'ABSENT_ABSTRACT':(lambda r:not r['presence']['abstract'],'no nonempty EFetch AbstractText'),
      'SUFFIX':(lambda r:any(a['suffix'] for a in r['authors']),'nonempty structured Author/Suffix'),
      'LONG':(lambda r:len(r['authors'])>=20,'at least 20 structured authors'),
      'UNICODE':(lambda r:any(ord(ch)>127 and ch.isalpha() for ch in r['title']+' '.join(a['last_name']+' '+a['fore_name'] for a in r['authors'])),'non-ASCII letter in title or personal author name'),
      'EDATE':(lambda r:bool(r['electronic_dates']),'explicit ArticleDate DateType=Electronic or History PubStatus=epublish'),
      'PREPRINT':(lambda r:any(t.lower()=='preprint' for t in r['publication_types']),'official PublicationType exactly Preprint')}
    for name,(predicate,description) in predicates.items():manifest[name]=slot(rows,predicate,description)
    for name,fields,predicate in [('ABSENT_FIELDS',['doi','issue','pages'],lambda r,f:not r.get(f))]:
        selected=mincover(rows,fields,predicate);manifest[name]={'status':'ready' if selected else 'missing','pmids':selected or [],'target_fields':fields,'predicate':'minimum-cardinality field cover; numeric sorted PMID tuple lexicographic tie-break','records':[public(records[p]) for p in selected or []]}
    save(ROOT/'manifest.partial.json',manifest);print('Basic slots selected',flush=True)
    linkouts={};linktypes={}
    for start in range(0,len(ids),200):
        batch=ids[start:start+200]
        root,source=obtain('elink',[('dbfrom','pubmed'),('db','pubmed'),('cmd','acheck'),('id',','.join(batch))])
        for item in root.findall('.//IdLinkSet'):linktypes[val(item,'Id')]={'names':[text(e) for e in item.findall('./LinkInfo/LinkName')],'source':source}
        root,source=obtain('elink',[('dbfrom','pubmed'),('cmd','llinks'),('id',','.join(batch))])
        for item in root.findall('.//IdUrlSet'):
            links=[]
            for o in item.findall('./ObjUrl'):links.append({'url':val(o,'Url'),'categories':[text(e) for e in o.findall('./Category')],'attributes':[text(e) for e in o.findall('./Attribute')],'provider':val(o,'Provider/Name'),'provider_abbreviation':val(o,'Provider/NameAbbr')})
            linkouts[val(item,'Id')]={'links':links,'source':source}
        print('ELink check/linkout',start+len(batch),'of',len(ids),flush=True)
    for row in rows:
        item=linkouts.get(row['pmid']);row['full_text_links']=[x for x in (item or {}).get('links',[]) if any('full text' in category.lower() for category in x['categories'])]
        row['linkout_checked']=item is not None;row['linkout_source_sha256']=(item or {}).get('source',{}).get('sha256')
        row['link_names']=linktypes.get(row['pmid'],{}).get('names',[])
        row['presence']['full_text_links']=bool(row['full_text_links']) or bool(row['pmcid'])
    available_fields=[f for f in META_FIELDS if any(r['presence'].get(f,False) for r in rows)]
    selected=mincover(rows,available_fields,lambda r,f:r['presence'].get(f,False))
    manifest['META']={'status':'ready' if selected else 'missing','pmids':selected or [],'field_vocabulary':META_FIELDS,'target_fields':available_fields,'predicate':'minimum-cardinality cover of candidate-available fields; numeric sorted PMID tuple lexicographic tie-break','records':[public(records[p]) for p in selected or []],'uncovered_fields':[f for f in META_FIELDS if f not in available_fields]}
    free=lambda r:bool(r['pmcid']) or any(any(a.lower()=='free resource' for a in x['attributes']) for x in r['full_text_links'])
    manifest['FREE']=slot(rows,free,'PMC identifier or official Full Text Sources link marked free resource')
    manifest['PUBLISHER']=slot(rows,lambda r:r['linkout_checked'] and not free(r) and any(x['provider'] and x['url'] and not any(a.lower()=='free resource' for a in x['attributes']) for x in r['full_text_links']),'official non-library Full Text Sources provider link not marked free and no known free source; access price is not inferred')
    manifest['ABSTRACT_ONLY']=slot(rows,lambda r:r['presence']['abstract'] and r['linkout_checked'] and not r['full_text_links'] and not r['pmcid'],'nonempty abstract, successfully checked LinkOut with no Full Text Sources URLs, and no PMC identifier; DOI absence alone never qualifies')
    for name,linkname,want in [('RELATED','pubmed_pubmed',True),('NO_RELATED','pubmed_pubmed',False),('REFERENCES','pubmed_pubmed_refs',True),('CITED_BY','pubmed_pubmed_citedin',True)]:
        chosen=[r for r in rows if r['pmid'] in linktypes and ((linkname in r['link_names'])==want)]
        if not chosen:manifest[name]={'status':'missing','pmid':None,'predicate':f'ELink {linkname} has other PMID IDs = {want}','reason':'No qualifying acheck candidate in bounded pool'};continue
        row=min(chosen,key=lambda r:int(r['pmid']))
        root,source=obtain('elink',[('dbfrom','pubmed'),('db','pubmed'),('cmd','neighbor'),('linkname',linkname),('id',row['pmid'])])
        linked=[text(e) for group in root.findall('./LinkSet/LinkSetDb') if val(group,'LinkName')==linkname for e in group.findall('./Link/Id') if text(e)!=row['pmid']]
        manifest[name]={'status':'ready' if bool(linked)==want else 'missing','pmid':row['pmid'],'predicate':f'ELink {linkname} has other PMID IDs = {want}','linked_pmids':linked,'source':source,'metadata':public(row)}
        if bool(linked)!=want:manifest[name]['reason']='acheck existence did not confirm desired neighbor predicate; no replacement selected without reviewed selection rule'
    library=[]
    for p in [manifest['BASE']['pmid'],manifest['DOI']['pmid'],manifest['FREE']['pmid']]+ids:
        if p and p not in library:library.append(p)
        if len(library)==3:break
    manifest['LIBRARY3']={'status':'ready' if len(library)==3 else 'missing','pmids':library,'predicate':'BASE, DOI, FREE in that order, deduplicated; supplement from numeric ascending frozen candidates'}
    library55=list(dict.fromkeys(queries[1]['pmids']))[:55]
    manifest['LIBRARY55']={'status':'ready' if len(library55)==55 and all(p in records for p in library55) else 'missing','pmids':library55,'predicate':'first 55 distinct PMIDs in the fixed diabetes ESearch ordered by descending publication date','query_source_sha256':queries[1]['source']['sha256']}
    manifest['sources']=CATALOG;manifest['completed_at_utc']=utc()
    manifest['selection_protocol_sha256']=digest((ROOT/'data-manifest-selection.json').read_bytes())
    manifest['builder_sha256']=digest(Path(__file__).read_bytes())
    save(RAW/'candidate-metadata-full.json',records)
    save(ROOT/'candidate-metadata.json',{p:public(r) for p,r in records.items()})
    save(ROOT/'manifest.json',public_provenance(manifest));save(ROOT/'source-responses.json',public_provenance(CATALOG))
    print('Manifest slots:',json.dumps({k:v.get('pmid',v.get('pmids')) for k,v in manifest.items() if isinstance(v,dict) and 'status'in v}),flush=True)
    print('Manifest SHA256:',digest((ROOT/'manifest.json').read_bytes()),flush=True)
def query_preflight():
    RAW.mkdir(parents=True,exist_ok=True)
    queries=[('diabetes',['T018','T056'],100,None),('cancer',['T056'],1,None),('hypertension',['T056'],1,None),('"medresearch_evaluation_20261115_zero_7f4d99"[Title]',['T020'],0,0),('electronic health records',['T063'],10,None),('(diabetes AND therapy) AND ("2020/01/01"[Date - Publication] : "2025/12/31"[Date - Publication]) AND review[Publication Type] AND english[Language]',['T097'],150,None)]
    result={'purpose':'Official query prerequisites only; not application tests; does not alter M1 candidate pool','created_at_utc':utc(),'queries':[]}
    for query,test_ids,minimum,maximum in queries:
        root,source=obtain('esearch',[('db','pubmed'),('term',query),('retmax','0'),('sort','pub_date'),('retmode','xml')]);count=int(val(root,'Count'))
        result['queries'].append({'query':query,'test_ids':test_ids,'count':count,'required_minimum':minimum,'required_maximum':maximum,'prerequisite_ready':count>=minimum and (maximum is None or count<=maximum),'source':source})
        print('Query prerequisite',test_ids,'count',count,flush=True)
    save(ROOT/'query-preflight.json',public_provenance(result))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline-only',action='store_true');parser.add_argument('--query-preflight',action='store_true');parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
    if args.query_preflight:query_preflight()
    else:
        if (ROOT/'manifest.json').exists() and not args.baseline_only and not args.rebuild:raise SystemExit('Existing manifest is preserved; explicit --rebuild required. Never rebuild after evaluation begins.')
        build(args.baseline_only)
