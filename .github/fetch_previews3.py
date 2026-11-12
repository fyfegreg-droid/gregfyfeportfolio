import json,re,os,urllib.request,urllib.parse,html
L=json.load(open('.github/press-urls.json')); out=json.load(open('assets/press/manifest.json'))
miss={k:u for k,u in L.items() if k not in out}
KN={'purewow-brunch':'https://assets.purewow.com/wp-content/uploads/2025/06/cheesecake-factory-brunch-menu-review_fb.jpg',
'purewow-happyhour':'https://assets.purewow.com/wp-content/uploads/2025/03/cheesecake-factory-happy-hour-appetizers_uni.jpg',
'purewow-peach':'https://assets.purewow.com/wp-content/uploads/2025/07/the-cheesecake-factory-peach-perfect-cheesecake-review_uni.jpg',
'purewow-tbb':'https://assets.purewow.com/wp-content/uploads/2024/07/cheesecake-factory-new-flavor-triple-berry-cheesecake_uni.jpg'}
UAS=['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)','Twitterbot/1.0','Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)']
def get(u,ua,extra=None):
    h={'User-Agent':ua,'Accept':'*/*'}
    if extra:h.update(extra)
    return urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=40)
def save(k,iu):
    for src in [iu,'https://wsrv.nl/?url='+urllib.parse.quote(iu,safe='')+'&w=1200&output=jpg']:
        try:
            r=get(src,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0');d=r.read(8_000_000);ct=r.headers.get('Content-Type','')
            if ct.startswith('image') and len(d)>3000:
                ext='.png' if 'png' in ct else '.webp' if 'webp' in ct else '.jpg'
                p='assets/press/'+k+ext;open(p,'wb').write(d);out[k]=p;print('OK',k,src[:40],len(d));return True
        except Exception as e:print('  imgerr',k,src[:40],str(e)[:60])
    return False
def ogfrom(page):
    for pat in [r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)',r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image',r'name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)']:
        m=re.search(pat,page,re.I)
        if m:return html.unescape(m.group(1))
for k,u in miss.items():
    if k in KN and save(k,KN[k]):continue
    iu=None
    for ua in UAS:
        try:
            pg=get(u,ua).read(2_000_000).decode('utf-8','ignore');iu=ogfrom(pg)
            if iu:break
        except Exception as e:print('  pgerr',k,ua[:12],str(e)[:50])
    if not iu:
        try:
            md=get('https://r.jina.ai/'+u,'Mozilla/5.0',{'X-Return-Format':'html'}).read(3_000_000).decode('utf-8','ignore');iu=ogfrom(md)
            if not iu:
                m=re.search(r'<img[^>]+src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)',md,re.I);iu=m and m.group(1)
        except Exception as e:print('  jina',k,str(e)[:60])
    if iu and save(k,iu):continue
    print('FAIL',k,iu)
json.dump(out,open('assets/press/manifest.json','w'),indent=1)
