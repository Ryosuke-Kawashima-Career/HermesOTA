"""Offline pilot validation; no financial values are estimated."""
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path('D:/Dev/HermesOTA')
DATA=ROOT/'data/2026-10-04-pilot'
SRC=ROOT/'sources/2026-10-04-pilot'
REPORT=ROOT/'reports/daily/2026-10-04-pilot.md'
start='2026-09-27'
end='2026-10-04'
counts={}
window=[]
for company in ['booking','expedia','trip','mmyt','airbnb']:
    raw=json.loads((SRC/('sec_'+company+'.html')).read_text(encoding='utf-8'))
    recent=raw['filings']['recent']
    rows=[dict(zip(recent,vals)) for vals in zip(*recent.values())]
    chosen=[dict(company=company,**r) for r in rows if start<=r['filingDate']<=end]
    assert not any(r['filingDate']==start for r in chosen), 'Boundary-day timestamps require review'
    counts[company]=dict(Counter(r['form'] for r in chosen))
    window.extend(chosen)
existing=json.loads((DATA/'sec-window-filings.json').read_text())
assert window==existing
records=json.loads((DATA/'developments.json').read_text(encoding='utf-8'))
manifest=json.loads((DATA/'source-manifest.json').read_text(encoding='utf-8'))
state=json.loads((ROOT/'state/developments.json').read_text(encoding='utf-8'))
assert len(records)==7 and len({r['development_id'] for r in records})==7
assert len({r['company'] for r in records})==5
assert len({r['development_id'] for r in state['developments']})==len(state['developments'])
assert len(manifest)==33
for m in manifest:
    assert m['retrieval_date']=='2026-10-04'
    assert m['accessed_url'].startswith('https://')
    if m.get('evidence_path'): assert Path(m['evidence_path']).is_file()
    if m.get('evidence_quote'):
        original=Path(m['evidence_path']).read_text(encoding='utf-8')
        norm=lambda s: re.sub(r'\s+',' ',s).strip()
        assert norm(m['evidence_quote']) in norm(original),m['source_id']
for record in records:
    for key in ['source_url','retrieval_date','claim_type','evidence_path','evidence_locator','limitations']:
        assert record.get(key), (record['development_id'],key)
financial=json.loads((DATA/'financial-inputs.json').read_text())
assert financial['comparisons']==[]
text=REPORT.read_text(encoding='utf-8')
for heading in ['Executive summary','Strategy developments','Financial updates','AI developments','Implications','Exclusions, inaccessible sources','Source provenance','## Sources']:
    assert heading in text,heading
assert len(set(map(int,re.findall(r'\[(\d+)\]',text))))==33
p=subprocess.run(['python','C:/Users/kawas/AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py','--ledger',str(DATA/'citations.json'),'verify',str(REPORT)],capture_output=True,text=True,encoding='utf-8')
assert p.returncode==0,p.stdout+p.stderr
result={'status':'passed','validated_at':datetime.now().astimezone().isoformat(),'companies_covered':5,'unique_development_records':7,'source_records':33,'in_window_sec_filing_count':len(window),'sec_filing_counts_by_company_and_form':counts,'financial_comparisons':0,'citation_verification':p.stdout+p.stderr,'limitations':'Schema, provenance, quotation, file, date-window, deduplication, and citation checks are not independent verification of company claims.'}
(DATA/'validation-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
checkpoint=ROOT/'state/coverage-2026-10-04-pilot.json'
coverage=json.loads(checkpoint.read_text(encoding='utf-8'))
coverage.update(status='pilot_report_validated',validated_at=result['validated_at'],validation_path='data/2026-10-04-pilot/validation-results.json')
checkpoint.write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
