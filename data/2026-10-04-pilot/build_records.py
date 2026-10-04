"""Normalize provenance, register citations, and deduplicate pilot records."""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path('D:/Dev/HermesOTA')
EVIDENCE = ROOT/'sources/2026-10-04-pilot'
DATA = ROOT/'data/2026-10-04-pilot'
LEDGER = DATA/'citations.json'
SCRIPT = Path('C:/Users/kawas/AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py')
NOW = datetime.now().astimezone().isoformat()
SELECTED = [
('lola_launch','2026-09-29','Personalized Discovery Meets Member Access', 'Backed by Booking Holdings, Lola helps you discover and book hotels, restaurants, events, and activities in one AI-powered conversation.'),
('lola_home',None,'Frequently asked questions', 'Lola is opening to members in waves, and invitations generally go out in the order people join.'),
('expedia_qantas','2026-09-30','Build and integration work', 'Build and integration work between Qantas Loyalty and Expedia Group B2B is currently underway, with the upgraded Hotels and Holidays platform scheduled to launch in H1 2027.'),
('trip_uk_tours','2026-10-02','Opening paragraph', 'Trip.com Group, a leading global travel service provider, and social enterprise Women in Travel CIC have launched three new women-led tours in London, Edinburgh and Manchester, created by graduates of the Enterprising Tour Guiding Academy.'),
('mmyt_cto','2026-09-30','How Myra Handles Travel Queries', 'Myra comprises around 10-12 specialist AI agents covering different travel needs, including flights and accommodation.'),
('airbnb_fall','2026-09-30','Better AI-powered trip planning', 'Starting in the US, we are bringing AI into every step of a trip to help take you from planning to check-in in less time.'),
('booking_cfo','2026-10-02','Watching the token bill', 'Booking’s roughly 9,000 engineers are getting about 30% more code into production, counting only merge requests that pass testing and quality control.'),
('airbnb_techcrunch','2026-09-30','AI search interface', 'Now, users can switch on a toggle to search for properties via text or voice prompts.'),
('expedia_layla','2026-07-31','Dateline', 'July 31, 2026'),
('agoda_ai_report','2026-09-25','Displayed publication date at end of article', 'September 25, 2026'),
('booking_newsroom',None,'Innovation Across Booking Holdings', 'October 1, 2026'),
('sec_booking',None,'filings.recent; latest retrieved filing date', '2026-09-16'),
('sec_expedia',None,'filings.recent; latest retrieved filing date', '2026-08-25'),
('sec_trip',None,'filings.recent; latest retrieved filing date', '2026-09-16'),
('sec_mmyt',None,'filings.recent; accession 0001193125-26-403477', 'mmyt-6k-post_agm-sep_202.htm'),
('sec_airbnb',None,'filings.recent; Forms 4 and 144', '2026-09-30'),
('mmyt_agm_primary','2026-09-28','SEC refusal page; publication date from filing metadata',None),
('booking_archive',None,'Static archive shell; no release list',None),
('expedia_archive',None,'Static archive shell; no release list',None),
('trip_archive',None,'Timeout',None),
('mmyt_archive',None,'Timeout; browser navigation also failed',None),
('airbnb_archive',None,'Static archive shell; no release list',None),
('lola_trade','2026-09-29','Cloudflare 403; candidate date from search only',None),
('expedia_muse',None,'Cloudflare 403',None),
('airbnb_trade','2026-09-30','Cloudflare 403; candidate date from search only',None),
('lola_wit','2026-10-01','Cloudflare 403; candidate date from search only',None),
('trip_golden_trade','2026-09-29','Cloudflare 403; candidate date from search only',None),
('mmyt_agm',None,'HTTP 403',None),
('mmyt_agm_mirror','2026-09-28','Mirror only; does not replace inaccessible primary',None),
('trip_group_media_browser',None,'Browser-rendered archive; Golden Week publication listing', 'Golden Week 2026 Fuels Extended Breaks and New Travel Routes: Trip.com Group Reveals Rising Destinations and Regional Trends'),
('airbnb_form4_a','2026-09-30','Filing date from SEC metadata; body blocked',None),
('airbnb_form4_b','2026-09-30','Filing date from SEC metadata; body blocked',None),
('airbnb_form144','2026-09-28','Filing date from SEC metadata; body blocked',None),
]

def cmd(*args):
    p=subprocess.run(['python',str(SCRIPT),'--ledger',str(LEDGER),*args],capture_output=True,text=True,encoding='utf-8')
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()

cmd('reset')
manifest=[]
for expected,(sid,pub,locator,quote) in enumerate(SELECTED,1):
    m=json.loads((EVIDENCE/(sid+'.metadata.json')).read_text(encoding='utf-8'))
    m.update(publication_date=pub,evidence_locator=locator)
    if sid in {'booking_archive','expedia_archive','airbnb_archive'}: m['access_status']='partial_static_shell'
    if sid=='mmyt_cto': m['access_status']='article_text_retrieved_with_metered_access_notice'
    if sid.startswith('sec_'): m['access_status']='retrieved_json'
    m['citation_id']=expected
    registered=cmd('add',m['accessed_url'],'--title',m.get('title') or sid)
    assert registered.startswith(f'[{expected}]'),registered
    if quote:
        text_path=EVIDENCE/(sid+'.txt')
        if sid.startswith('sec_'):
            # Reformat the fetched JSON only; preserve values and raw evidence.
            fetched=json.loads((EVIDENCE/(sid+'.html')).read_text(encoding='utf-8'))
            text_path=EVIDENCE/(sid+'.pretty.json')
            text_path.write_text(json.dumps(fetched,ensure_ascii=False,indent=2),encoding='utf-8')
            first=fetched['filings']['recent']['filingDate'][0]
            quote='"filingDate": [\n        "'+first+'",'
            m['evidence_path']=str(text_path)
        cmd('quote',str(expected),'--text',quote,'--from',str(text_path))
        m['evidence_quote']=quote
    manifest.append(m)
(DATA/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

DEVS=[
('booking-lola-2026-09-29','Booking Holdings','Lola','strategy_ai','Lola membership and multi-category AI assistant','2026-09-29',[1,2],'reported_fact','Lola published an AI experiences assistant and membership announcement; current FAQ restricts access to invitation waves.','piloted','No independently measured outcome evidence; paid plans forthcoming.'),
('expedia-qantas-2026-09-30','Expedia Group','Expedia Group B2B','strategy_ai','Qantas Loyalty technology partnership','2026-09-30',[3],'reported_fact','Expedia published the Qantas partnership announcement; integration is underway.','announced','H1 2027 launch is a management schedule, not evidence of current availability.'),
('trip-uk-tours-2026-10-02','Trip.com Group','Trip.com','strategy','Women in Travel CIC UK tours','2026-10-02',[4],'reported_fact','Trip.com announced three women-led tours in London, Edinburgh and Manchester.',None,'No booking-volume or revenue data supplied.'),
('mmyt-myra-cto-2026-09-30','MakeMyTrip','Myra','strategy_ai','CTO describes multi-agent travel architecture',None,[5],'management_claim','CTO says Myra uses around 10-12 specialist agents and mixes model types.','launched','Existing deployed assistant according to CTO; no new launch verified or independently measured outcomes.'),
('airbnb-fall-2026-09-30','Airbnb','Airbnb','strategy_ai','Fall update: social discovery, AI search and services','2026-09-30',[6,8],'reported_fact','Airbnb published a fall update introducing US-first AI search, filters, listing descriptions, and home comparisons.','launched','Company-reported rollout, press corroboration, no hands-on test or independently measured business impact.'),
('booking-cfo-aiq-2026-10-01','Booking Holdings',None,'strategy_ai','CFO discusses AI cost routing and productivity','2026-10-01',[7],'management_claim','CFO reports roughly 30% more production code and early customer-service/conversion benefits.',None,'Measurement period, comparable baseline, methodology, and independent validation unavailable.'),
('mmyt-6k-0001193125-26-403477','MakeMyTrip',None,'governance','September 28 Form 6-K filing','2026-09-28',[15,17],'reported_fact','SEC submission metadata lists the 6-K; primary filing body was blocked.',None,'No verified voting outcome or new financial figures.'),
]
records=[]
for did,company,brand,topic,title,event_date,ids,ctype,claim,ai,limits in DEVS:
    src=[manifest[i-1] for i in ids]
    records.append(dict(development_id=did,company=company,brand=brand,topic=topic,title=title,event_date=event_date,reporting_period=None,claim_type=ctype,claim_text=claim,ai_status=ai,outcome_evidence_status='not_independently_evidenced' if ai or topic.endswith('ai') else 'not_applicable',source_ids=[m['source_id'] for m in src],source_url=src[0]['accessed_url'],publication_date=src[0]['publication_date'],retrieval_date=src[0]['retrieval_date'],evidence_path=src[0].get('evidence_path'),evidence_locator=src[0]['evidence_locator'],first_seen='2026-10-04',last_checked='2026-10-04',limitations=limits,status='pilot_reported',source_provenance=[{k:m.get(k) for k in ['source_id','accessed_url','publication_date','retrieval_date','evidence_path','citation_id']} for m in src]))
(DATA/'developments.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'financial-inputs.json').write_text(json.dumps({'status':'no_new_operating_result_inputs_verified_in_window','comparisons':[],'reason':'No in-window operating earnings release was verified. No currencies, GAAP/non-GAAP figures or missing metrics were synthesized.','filings_index':'sec-window-filings.json','original_price_disclosures':{'source_id':'lola_launch','symbol_as_published':'$','currency_code_explicitly_stated':None,'plus_per_month':'5','vip_per_month':'25','commitment_months':12,'status':'announced; current FAQ says paid plans forthcoming'}},indent=2),encoding='utf-8')
state=ROOT/'state/developments.json'
prior=json.loads(state.read_text(encoding='utf-8')) if state.exists() else {'developments':[]}
indexed={x['development_id']:x for x in prior['developments']}
for record in records:
    old=indexed.get(record['development_id'])
    if old:
        record['first_seen']=old['first_seen']
        record['history']=old.get('history',[])+[{'checked':NOW,'source_ids':record['source_ids']}]
    else:
        record['history']=[{'checked':NOW,'status':'first_pilot_record'}]
    indexed[record['development_id']]=record
prior.update(updated_at=NOW,developments=list(indexed.values()))
state.write_text(json.dumps(prior,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'state/coverage-2026-10-04-pilot.json').write_text(json.dumps({'cutoff':'2026-10-04T14:39:33+05:30','window_start':'2026-09-27T14:39:33+05:30','companies':['Booking Holdings','Expedia Group','Trip.com Group','MakeMyTrip','Airbnb'],'source_manifest':'data/2026-10-04-pilot/source-manifest.json','exclusions':[{'source_id':'expedia_layla','reason':'Primary publication July 31, outside window; recent recirculation is not a new acquisition.'},{'source_id':'agoda_ai_report','reason':'Primary article date September 25, outside window; Booking newsroom labels October 1. Date conflict unresolved.'}],'report':'reports/daily/2026-10-04-pilot.md','status':'draft_pending_validation','limitations':'Non-exhaustive public-source pilot; partial IR archives, blocked filing bodies, and no systematic HKEX/Nasdaq exchange sweep.'},indent=2),encoding='utf-8')
print(cmd('render','--only',','.join(str(i) for i in range(1,len(manifest)+1))))
print(json.dumps({'sources_registered':len(manifest),'development_records':len(records),'companies_covered':len({r['company'] for r in records}),'state_unique_records':len(indexed)},indent=2))
