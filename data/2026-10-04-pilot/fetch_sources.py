"""Public read-only retrieval; downloaded material is never executed."""
import concurrent.futures
import hashlib
import json
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path('D:/Dev/HermesOTA')
OUT = ROOT / 'sources/2026-10-04-pilot'
TARGETS = {
'booking_archive':'https://ir.bookingholdings.com/news/default.aspx',
'expedia_archive':'https://ir.expediagroup.com/news-and-events/news/default.aspx',
'trip_archive':'https://investors.trip.com/news-releases',
'mmyt_archive':'https://investors.makemytrip.com/investors/press-releases',
'airbnb_archive':'https://investors.airbnb.com/press-releases/default.aspx',
'airbnb_fall':'https://news.airbnb.com/airbnb-2026-fall-update',
'lola_home':'https://www.lola.com/',
'lola_trade':'https://www.phocuswire.com/news/technology/steve-hafner-paul-english-launch-ai-assistant-lola',
'expedia_muse':'https://www.phocuswire.com/news/online/expedia-hotel-booking-meta-muse',
'airbnb_trade':'https://www.phocuswire.com/news/online/airbnb-expands-social-discovery-strategy-latest-app-updates-fall-2026',
'expedia_layla':'https://ir.expediagroup.com/news-and-events/news/news-details/2026/Expedia-Group-acquires-Layla-accelerating-its-AI-powered-trip-planning-and-booking-strategy/default.aspx',
'mmyt_cto':'https://inc42.com/buzz/ai-is-compressing-the-travel-booking-journey-makemytrip-cto/',
'mmyt_agm':'https://www.stocktitan.net/sec-filings/MMYT/6-k-make-my-trip-ltd-current-report-foreign-issuer-8858846b56a8.html',
'booking_cfo':'https://fortune.com/2026/10/02/booking-holdings-cfo-says-even-ai-hyperscalers-dont-know-their-roi-but-hes-learning-from-his-ai-coach/',
'trip_newsroom':'https://www.trip.com/newsroom/',
'airbnb_techcrunch':'https://techcrunch.com/2026/09/30/airbnb-adds-ai-search-more-social-features/',
}

def fetch(item):
    sid, url = item
    meta = {'source_id':sid,'accessed_url':url,'publication_date':None,'retrieval_timestamp':datetime.now().astimezone().isoformat(),'retrieval_date':datetime.now().astimezone().date().isoformat(),'provenance':'live'}
    try:
        r = requests.get(url, timeout=35, headers={'User-Agent':'OTAIntelligence public-source research'})
        meta.update(http_status=r.status_code, final_url=r.url)
        html_path = OUT / (sid + '.html')
        html_path.write_bytes(r.content)
        soup = BeautifulSoup(r.content, 'html.parser')
        meta['title'] = soup.title.get_text(' ',strip=True) if soup.title else None
        meta['date_metadata'] = [dict(x.attrs) for x in soup.find_all('meta') if any(t in str(x.attrs).lower() for t in ['date','published','modified'])]
        meta['json_ld'] = [x.get_text() for x in soup.find_all('script',type='application/ld+json')]
        meta['links'] = [{'text':a.get_text(' ',strip=True),'url':a.get('href')} for a in soup.find_all('a',href=True) if a.get_text(' ',strip=True)]
        for x in soup(['script','style','nav','footer']): x.decompose()
        text = soup.get_text('\n',strip=True)
        text_path = OUT / (sid + '.txt')
        text_path.write_text(text,encoding='utf-8')
        blocked = r.status_code >= 400 or 'just a moment' in str(meta['title']).lower() or ('cloudflare' in text.lower() and len(text)<2500)
        meta.update(access_status='blocked' if blocked else 'retrieved_needs_review',evidence_path=str(text_path),html_path=str(html_path),sha256=hashlib.sha256(r.content).hexdigest(),text_length=len(text))
    except Exception as e:
        meta.update(access_status='failed',error=str(e))
    (OUT / (sid + '.metadata.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta

if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    records = list(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(fetch,TARGETS.items()))
    (OUT/'fetch-index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for m in records:
        print(json.dumps({k:m.get(k) for k in ['source_id','http_status','access_status','title','text_length','error']},ensure_ascii=False))
