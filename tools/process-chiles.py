#!/usr/bin/env python3
"""Turn chile-ristra photos into transparent, color-graded WebP cut-outs for the header.

Drop new photos (png/jpg/jpeg/webp, bunch on a plain light background) into assets/chiles/ and run:
    python3 tools/process-chiles.py
New files are moved into assets/chiles/src/ as ristra-NN-src.<ext> and rendered to assets/chiles/ristra-NN.webp.
Existing sources are re-rendered. If fewer than 6 cut-outs exist, composites of two sources fill the gap.
Then run tools/build-header.py to rebuild the pages.
"""
import glob, os, re, shutil, sys
import numpy as np
from PIL import Image, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,"assets","chiles"); SRC=os.path.join(D,"src"); os.makedirs(SRC,exist_ok=True)
OUT_H=1000; MIN_TOTAL=6
rng=np.random.default_rng(3)

def ramp(d,lo,hi): return np.clip((d-lo)/(hi-lo),0,1)
def cutout(path):
    im=Image.open(path).convert("RGB"); a=np.array(im).astype(float); R,G,B=a[...,0],a[...,1],a[...,2]
    h,w=R.shape; border=np.concatenate([a[:20].reshape(-1,3),a[-20:].reshape(-1,3),a[:,:20].reshape(-1,3),a[:,-20:].reshape(-1,3)])
    bg=np.median(border,axis=0)
    if bg.min()>200:            # white / light-gray studio background
        d=255-np.minimum(np.minimum(R,G),B); al=ramp(d,28,85)
    else:                       # plain colored wall: distance from the sampled background color
        d=np.sqrt(((a-bg)**2).sum(-1)); al=ramp(d,40,90)
    M=Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(.8))
    al=np.array(M)/255.
    red=(R>G*1.45)&(R>B*1.3)&(al>.5)
    rows=red.sum(1); top=int(np.where(rows>rows.max()*.12)[0].min())
    al[:max(top-4,0)]=0                                  # drop the photographed twine above the cluster
    stalk=(~red)&(np.maximum(np.maximum(R,G),B)>70)       # loose twine / stalk hanging below the tip: anything bright that isn't chile-red
    cut=int(h*.80); al[cut:][stalk[cut:]]=0
    M=Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.6))
    al=np.array(M)/255.
    ys,xs=np.where(al>.5); y0,y1,x0,x1=max(ys.min()-4,0),min(ys.max()+6,h),max(xs.min()-6,0),min(xs.max()+6,w)
    g=np.dstack([R*.94,G*.80,B*.88]); L=g.mean(-1); g*=np.where(L>150,.9,1.)[...,None]   # grade toward brick/oxblood
    out=np.dstack([np.clip(g,0,255),al*255])[y0:y1,x0:x1]
    im=Image.fromarray(out.astype(np.uint8),"RGBA")
    return im.resize((round(im.width*OUT_H/im.height),OUT_H),Image.LANCZOS)
def finish(im,name):
    a=np.array(im).astype(float); a[...,:3]=np.clip(a[...,:3]+rng.normal(0,5.5,a.shape[:2])[...,None],0,255)
    Image.fromarray(a.astype(np.uint8),"RGBA").filter(ImageFilter.UnsharpMask(radius=2,percent=55,threshold=3)).save(name,quality=84,method=6)
def composite(back,front,sb,sf,dx,dy):
    b=back.resize((round(back.width*sb),round(back.height*sb)),Image.LANCZOS); f=front.resize((round(front.width*sf),round(front.height*sf)),Image.LANCZOS)
    W=max(b.width,f.width+abs(dx))+abs(dx); H=max(b.height,f.height+dy); c=Image.new("RGBA",(W,H),(0,0,0,0)); bx=(W-b.width)//2
    c.alpha_composite(b,(bx,0)); arr=np.array(c).astype(float); arr[...,:3]*=.82; c=Image.fromarray(arr.astype(np.uint8),"RGBA"); c.alpha_composite(f,(bx+dx,dy))
    c=c.crop(c.getbbox()); return c.resize((round(c.width*OUT_H/c.height),OUT_H),Image.LANCZOS)

# 1. adopt any new photos dropped in assets/chiles/
existing=sorted(glob.glob(os.path.join(SRC,"ristra-*-src.*")))
n=max([int(re.search(r"ristra-(\d+)-src",p).group(1)) for p in existing],default=0)
for p in sorted(glob.glob(os.path.join(D,"*"))):
    if os.path.isdir(p) or re.search(r"ristra-\d+\.webp$",p) or os.path.basename(p).startswith("."): continue
    if not re.search(r"\.(png|jpe?g|webp)$",p,re.I): continue
    n+=1; dst=os.path.join(SRC,f"ristra-{n:02d}-src{os.path.splitext(p)[1].lower()}"); shutil.move(p,dst); existing.append(dst); print("adopted",os.path.basename(p),"->",os.path.basename(dst))
# 2. render every source
for p in glob.glob(os.path.join(D,"ristra-*.webp")): os.remove(p)
rendered=[]
for p in sorted(existing):
    i=int(re.search(r"ristra-(\d+)-src",p).group(1)); out=os.path.join(D,f"ristra-{i:02d}.webp")
    try: im=cutout(p); finish(im,out); rendered.append(im); print("rendered",os.path.basename(out),im.size)
    except Exception as e: print("FAILED",os.path.basename(p),e)
# 3. composites to reach MIN_TOTAL
k=len(rendered); pairs=[(2,3,1.0,.86,-60,40),(0,1,.92,.95,70,25),(1,2,1.0,.9,-50,30),(3,0,.95,.9,60,20)]
for a,b,sb,sf,dx,dy in pairs:
    if k>=MIN_TOTAL or len(rendered)<2: break
    k+=1; out=os.path.join(D,f"ristra-{k:02d}.webp"); c=composite(rendered[a%len(rendered)],rendered[b%len(rendered)].transpose(Image.FLIP_LEFT_RIGHT),sb,sf,dx,dy); finish(c,out); print("composite",os.path.basename(out),c.size)
