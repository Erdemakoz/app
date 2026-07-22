from __future__ import annotations
import json,re,shutil,subprocess,uuid
from pathlib import Path
from typing import Any
from fastapi import FastAPI,BackgroundTasks,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,HttpUrl
BASE=Path(__file__).resolve().parent.parent; DATA=BASE/'data'; OUT=BASE/'outputs'; STATIC=Path(__file__).resolve().parent/'static'
DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
app=FastAPI(title='StreamScout'); app.mount('/static',StaticFiles(directory=STATIC),name='static'); app.mount('/outputs',StaticFiles(directory=OUT),name='outputs')
JOBS:dict[str,dict[str,Any]]={}
class AnalyzeRequest(BaseModel):
    url:HttpUrl; amount:int=20; clip_seconds:int=45; model_size:str='small'; vertical:bool=True
def run(cmd):
    p=subprocess.run(cmd,check=True,capture_output=True,text=True); return p.stdout
def duration(path):
    return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)]).strip())
def download(url,jobdir):
    run(['yt-dlp','--no-playlist','-f','bv*+ba/b','--merge-output-format','mp4','-o',str(jobdir/'source.%(ext)s'),url])
    m=list(jobdir.glob('source.*'))
    if not m: raise RuntimeError('Download mislukt')
    return m[0]
def audio(video,audiofile):
    run(['ffmpeg','-y','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(audiofile)])
def transcribe(audiofile,size):
    from faster_whisper import WhisperModel
    device='cuda' if shutil.which('nvidia-smi') else 'cpu'; compute='float16' if device=='cuda' else 'int8'
    model=WhisperModel(size,device=device,compute_type=compute)
    segs,_=model.transcribe(str(audiofile),vad_filter=True,beam_size=3)
    return [{'start':float(s.start),'end':float(s.end),'text':s.text.strip()} for s in segs if s.text.strip()]
HYPE={'oh my god':2.2,'no way':2.0,'crazy':1.6,'police':2.0,'fight':2.0,'help':2.0,'lmao':1.5,'haha':1.0,'bro':1.2,'stop':1.2,'what':1.0,'fuck':1.0,'shit':1.0,'wait':.8,'yo':.8}
def score(segs):
    out=[]
    for i,s in enumerate(segs):
        t=s['text'].lower(); words=re.findall(r'\w+',t); density=min(len(words)/max(s['end']-s['start'],1),4)*.25
        hype=sum(v for k,v in HYPE.items() if k in t); novelty=.4 if i and s['start']-segs[i-1]['end']>3 else 0
        out.append({**s,'score':round(density+hype+novelty,3)})
    return sorted(out,key=lambda x:x['score'],reverse=True)
def choose(scored,amount,seconds,total):
    picked=[]; gap=max(seconds*.8,25)
    for s in scored:
        c=(s['start']+s['end'])/2; st=max(0,c-seconds*.35); en=min(total,st+seconds); st=max(0,en-seconds)
        if all(abs(st-p['start'])>=gap for p in picked): picked.append({'start':round(st,2),'end':round(en,2),'score':s['score'],'reason':s['text'][:180]})
        if len(picked)>=amount: break
    return sorted(picked,key=lambda x:x['start'])
def clip(video,dest,start,length,vertical):
    vf=['-vf',"crop='ih*9/16:ih',scale=1080:1920"] if vertical else []
    run(['ffmpeg','-y','-ss',str(start),'-i',str(video),'-t',str(length),*vf,'-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-b:a','160k','-movflags','+faststart',str(dest)])
def process(jid,req):
    jd=DATA/jid; od=OUT/jid; jd.mkdir(parents=True,exist_ok=True); od.mkdir(parents=True,exist_ok=True); j=JOBS[jid]
    try:
        j.update(status='downloading',progress=5,message='VOD downloaden'); video=download(str(req.url),jd)
        j.update(status='audio',progress=20,message='Audio voorbereiden'); wav=jd/'audio.wav'; audio(video,wav)
        j.update(status='transcribing',progress=30,message='Volledige stream uitschrijven'); segs=transcribe(wav,req.model_size)
        (jd/'transcript.json').write_text(json.dumps(segs,ensure_ascii=False,indent=2),encoding='utf-8')
        j.update(status='scoring',progress=72,message='Beste momenten beoordelen'); moments=choose(score(segs),req.amount,req.clip_seconds,duration(video)); results=[]
        for i,m in enumerate(moments,1):
            j.update(progress=75+int(23*i/max(len(moments),1)),message=f'Clip {i}/{len(moments)} exporteren'); dest=od/f'clip_{i:02d}.mp4'; clip(video,dest,m['start'],m['end']-m['start'],req.vertical); results.append({**m,'url':f'/outputs/{jid}/{dest.name}'})
        j.update(status='done',progress=100,message='Klaar',results=results)
    except Exception as e: j.update(status='error',progress=0,message=str(e))
@app.get('/')
def home(): return FileResponse(STATIC/'index.html')
@app.post('/api/analyze')
def analyze(req:AnalyzeRequest,bg:BackgroundTasks):
    if not 1<=req.amount<=100: raise HTTPException(400,'Aantal clips moet 1-100 zijn')
    jid=uuid.uuid4().hex[:12]; JOBS[jid]={'id':jid,'status':'queued','progress':0,'message':'In wachtrij'}; bg.add_task(process,jid,req); return JOBS[jid]
@app.get('/api/jobs/{jid}')
def job(jid:str):
    if jid not in JOBS: raise HTTPException(404,'Niet gevonden')
    return JOBS[jid]
