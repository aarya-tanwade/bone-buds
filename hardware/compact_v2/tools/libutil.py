"""Reproducible Bone Buds cable-module carrier. Run with KiCad bundled Python."""
from pathlib import Path
import json, re, uuid, math, csv, pcbnew
ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'pcb'; NAME='bone_buds_carrier'
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad')
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s))
def parse(s):
    toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[]; root=None
    for t in toks:
        if t=='(':
            a=[]
            if stack: stack[-1].append(a)
            else: root=a
            stack.append(a)
        elif t==')': stack.pop()
        else: stack[-1].append(t)
    return root
def dump(x): return '('+' '.join(dump(t) if isinstance(t,list) else t for t in x)+')'
def children(n,k): return [x for x in n if isinstance(x,list) and x and x[0]==k]
def child(n,k): return next(iter(children(n,k)),None)
def val(t): return json.loads(t) if t.startswith('"') else t
cache={}
def symbol(lib,name):
    if lib not in cache: cache[lib]=parse((LIB/'symbols'/f'{lib}.kicad_sym').read_text(encoding='utf8'))
    import copy
    n=copy.deepcopy(next(x for x in children(cache[lib],'symbol') if val(x[1])==name))
    ext=child(n,'extends')
    if ext:
        base=symbol(lib,val(ext[1])); base[1]=q(name)
        for sub in children(base,'symbol'): sub[1]=q(name+val(sub[1])[len(val(ext[1])):])
        for prop in children(n,'property'):
            old=next((p for p in children(base,'property') if p[1]==prop[1]),None)
            if old: base.remove(old)
            base.append(prop)
        return base
    return n

