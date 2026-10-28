#!/usr/bin/env python3
"""Bundle the teaching site and example files into a dependency-free Worker."""
import base64
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
EXAMPLE=ROOT.parent/'security-incident-ontology'
DIST=ROOT/'dist'
shutil.copytree(EXAMPLE, DIST/'files', dirs_exist_ok=True)
(DIST/'download').mkdir(exist_ok=True)
shutil.copy2(ROOT.parent/'security-incident-ontology.zip',DIST/'download/security-incident-ontology.zip')
results=json.loads((EXAMPLE/'output/results.json').read_text())
def portable(value):
    if isinstance(value,dict): return {k:portable(v) for k,v in value.items()}
    if isinstance(value,list): return [portable(v) for v in value]
    if isinstance(value,str): return value.replace(str(EXAMPLE),'example')
    return value
(DIST/'data.json').write_text(json.dumps({'public':(EXAMPLE/'public-vocabulary.ttl').read_text(),'ontology':(EXAMPLE/'ontology.ttl').read_text(),'facts':(EXAMPLE/'facts.ttl').read_text(),'shapes':(EXAMPLE/'shapes.ttl').read_text(),'queries':{p.name:p.read_text() for p in sorted((EXAMPLE/'queries').glob('*.rq'))},'results':portable(results)},indent=2)+'\n')
MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.ttl':'text/turtle; charset=utf-8','.rq':'application/sparql-query; charset=utf-8','.md':'text/plain; charset=utf-8','.py':'text/plain; charset=utf-8','.tsv':'text/tab-separated-values; charset=utf-8','.sha256':'text/plain; charset=utf-8','.zip':'application/zip'}
files={}
for p in sorted(DIST.rglob('*')):
    if p.is_file():
        raw=p.read_bytes()
        binary=p.suffix=='.zip'
        files['/'+str(p.relative_to(DIST))]={'body':base64.b64encode(raw).decode() if binary else raw.decode(),'type':MIME.get(p.suffix,'text/plain; charset=utf-8'),'binary':binary,'etag':'"'+hashlib.sha256(raw).hexdigest()[:24]+'"'}
worker='const FILES = '+json.dumps(files,separators=(',',':'))+';\n'+'''export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed', {status:405,headers:{Allow:'GET, HEAD'}});
    let path = url.pathname;
    if (path === '/') path = url.searchParams.has('lesson') ? '/lab.html' : '/index.html';
    if (path === '/lab' || path === '/lab/') path = '/lab.html';
    const asset = FILES[path];
    if (!asset) return new Response('Not found', {status:404,headers:{'Content-Type':'text/plain; charset=utf-8','X-Content-Type-Options':'nosniff'}});
    const headers = new Headers({
      'Content-Type':asset.type, 'ETag':asset.etag,
      'Cache-Control':'no-cache',
      'X-Content-Type-Options':'nosniff', 'Referrer-Policy':'strict-origin-when-cross-origin',
      'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
      'Permissions-Policy':'camera=(), microphone=(), geolocation=()'
    });
    if(path.startsWith('/download/')) headers.set('Content-Disposition','attachment; filename="'+path.split('/').pop()+'"');
    if(request.headers.get('If-None-Match')===asset.etag) return new Response(null,{status:304,headers});
    const body = request.method==='HEAD'?null:asset.binary?Uint8Array.from(atob(asset.body),c=>c.charCodeAt(0)):asset.body;
    return new Response(body,{headers});
  }
};\n'''
(ROOT/'worker.mjs').write_text(worker)
print(json.dumps({'files':len(files),'worker_bytes':len(worker.encode()),'source':str(ROOT/'worker.mjs')}))
