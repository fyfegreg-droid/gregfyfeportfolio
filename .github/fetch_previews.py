
import json,re,os,urllib.request,html
C=json.load(open('.github/press-urls2.json'));L=C['pages'];KN=C['known'];prev=json.load(open('assets/press/manifest.json'))
UA='facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
BR='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
def get(u,ref=None,ua=None):
    h={'User-Agent':ua or UA,'Accept':'text/html,application/xhtml+xml,image/*,*/*','Accept-Language':'en-US,en;q=0.9'}
    if ref:h['Referer']=ref
    return urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=30)
os.makedirs('assets/press',exist_ok=True)
out=dict(prev)
for k,u in L.items():
    try:
        if k in KN:
            ir=get(KN[k],ref=u,ua=BR);data=ir.read(8_000_000);ct=ir.headers.get('Content-Type','')
            ext='.png' if 'png' in ct else '.webp' if 'webp' in ct else '.jpg'
            if ct.startswith('image') and len(data)>3000:
                p='assets/press/'+k+ext;open(p,'wb').write(data);out[k]=p;print('OKK',k,len(data));continue
    except Exception as e: print('KERR',k,str(e)[:60])
    try:
        r=get(u); page=r.read(2_000_000).decode('utf-8','ignore')
        m=None
        for pat in [r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]*content=["\']([^"\']+)',r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*property=["\']og:image',r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]*content=["\']([^"\']+)',r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*name=["\']twitter:image']:
            m=re.search(pat,page,re.I)
            if m:break
        if not m: print('NOIMG',k);continue
        iu=html.unescape(m.group(1))
        if iu.startswith('//'):iu='https:'+iu
        if iu.startswith('/'):iu=re.match(r'https?://[^/]+',r.geturl()).group(0)+iu
        ir=get(iu,ref=u); data=ir.read(8_000_000)
        ct=ir.headers.get('Content-Type','')
        ext='.png' if 'png' in ct else '.webp' if 'webp' in ct else '.gif' if 'gif' in ct else '.jpg'
        if len(data)<3000 or not ct.startswith('image'): print('SMALL',k,ct,len(data));continue
        p='assets/press/'+k+ext; open(p,'wb').write(data); out[k]=p; print('OK',k,len(data))
    except Exception as e:
        print('ERR',k,type(e).__name__,str(e)[:80])
json.dump(out,open('assets/press/manifest.json','w'),indent=1)
