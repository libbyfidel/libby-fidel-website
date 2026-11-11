#!/usr/bin/env python3
"""Regenerates the chile-ristra header on every page.
Edit SCENE / NAV below, then run: python3 tools/build-header.py
Chile cut-outs come from assets/chiles/ristra-NN.webp (see tools/process-chiles.py); bows are drawn by tools/sketchbow.py."""
import re, glob, os, sys
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from sketchbow import sketch_bow
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV=[("/writing/","Writing"),("/sf/","Life in SF"),("/games/","Games"),("/#about","About"),("/#contact","Contact")]
# (kind, image#, chile height px, twine px, tilt deg, flip) — nav links are the "n" slots, in NAV order
SCENE=[("d",5,440,36,-1.6,0),("d",3,400,64,1.2,1),("d",6,430,48,-.7,0),
       ("n",2,400,48,-.8,0),("n",4,440,58,1.5,1),("n",1,380,44,-1.9,1),("n",5,420,56,.6,1),("n",3,390,46,1.1,0),
       ("d",6,420,68,-1.3,1),("d",2,380,40,1.7,1),("d",4,460,52,-1.1,0)]
# per-tab bow variation: (mirror, tilt deg, extra long-tail length, short-tail length nudge) — keeps the five sketches from looking stamped
BOWVAR=[(0,-2.5,0,0),(1,1.5,8,-6),(0,-1,14,10),(1,2.5,0,0),(0,-2,6,-4)]
IMGS=sorted(glob.glob(ROOT+"/assets/chiles/ristra-*.webp")); SIZES={i+1:Image.open(p).size for i,p in enumerate(IMGS)}
def bow(label,k):
    m,rot,extra,short=BOWVAR[k]
    return sketch_bow(label,k+1,bool(m),extra,short).replace('class="bow"',f'class="bow" style="--brot:{rot}deg"',1)
def ristra(i,spec,on_href):
    kind,img,h,tw,rot,flip=spec; img=(img-1)%len(SIZES)+1; w,hh=SIZES[img]
    style=f'--img:url(/assets/chiles/ristra-{img:02d}.webp);--rh:{h}px;--tw:{tw}px;--rot:{rot}deg;--dur:{3.2+(i*.37)%1.4:.2f}s;--delay:-{(i*.9)%3:.1f}s'
    tag=f'<img src="/assets/chiles/ristra-{img:02d}.webp" alt="" width="{w}" height="{hh}" decoding="async"{" fetchpriority=high" if i<5 else ""}>'
    if kind=="d": return f'<span class="ristra{" flip" if flip else ""}" style="{style}" aria-hidden="true">{tag}</span>'
    k=[s[0] for s in SCENE[:i]].count("n"); href,label=NAV[k]
    cls="ristra nav-item"+(" flip" if flip else "")+(" on" if href==on_href else "")
    return f'<a class="{cls}" href="{href}" style="{style}">{tag}{bow(label,k)}<span class="lbl">{label}</span></a>'
def header(on_href):
    items="".join(ristra(i,s,on_href) for i,s in enumerate(SCENE))
    return ('<div class="hdr-top"><a class="hdr-logo" href="/"><img src="/brand/libby-mark-teal.svg" alt="Libby Fidel home"></a></div>'
            f'<nav class="hdr-nav" aria-label="Main">{items}</nav>')
LINK='<link rel="stylesheet" href="/assets/header.css">'
def ensure_link(s):
    if LINK in s: return s
    if '<link rel="stylesheet" href="/assets/site.css">' in s: return s.replace('<link rel="stylesheet" href="/assets/site.css">','<link rel="stylesheet" href="/assets/site.css">'+LINK,1)
    return s.replace("</head>",LINK+"\n</head>",1)
main=re.compile(r'(?:<svg class="bowdefs".*?)?<div class="(?:wrap sh|hdr-top)">.*?</nav>(?:</div>(?=<div class="wrap (?:hero|post-hero|page-hero)"))?',re.S)
sub=re.compile(r'(?:<header class="topbar progress-holder".*?</header>)?<div class="band hdr">.*?</nav></div>|<header(?: class="topbar")?>.*?</header>',re.S)
for f in sorted(glob.glob(ROOT+"/**/*.html",recursive=True)):
    if "/design-ref/" in f: continue
    s=open(f).read(); rel=f.replace(ROOT,"")
    m=main.search(s)
    if m:   # main site pages: header lives inside <div class="band">
        on=re.search(r'<a href="([^"]+)" class="?on"?',m.group(0)) or re.search(r'<a class="[^"]*\bon\b[^"]*" href="([^"]+)"',m.group(0)); on=on.group(1) if on else None
        s=s[:m.start()]+header(on)+s[m.end():]
        s=re.sub(r'<div class="band">(?=<svg class="bowdefs"|<div class="hdr-top">)','<div class="band hdr">',s,count=1)
        if rel=="/index.html" and "TODO: replace placeholder" not in s:
            s=s.replace('<div class="wrap hero"><h1>','<div class="wrap hero"><!-- TODO: replace placeholder title/company below with the real ones --><span class="eyebrow">Your title · Your company</span><h1>',1)
    else:   # brand page + lab-to-term-sheet sub-site: their own <header> is replaced by a standalone band
        m=sub.search(s)
        if not m: print("skip",rel); continue
        keep='<header class="topbar progress-holder" style="height:0;border:0"><div class="progress"></div></header>' if 'class="progress"' in m.group(0) else ''
        s=s[:m.start()]+keep+'<div class="band hdr">'+header(None)+'</div>'+s[m.end():]
    s=ensure_link(s); open(f,"w").write(s); print("ok",rel)
