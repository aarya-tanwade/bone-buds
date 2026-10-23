import adsk.core,adsk.fusion,json

def run(_context: str):
 app=adsk.core.Application.get(); print('Fusion version',app.version)
 print([(l.name,l.appearances.count,l.materials.count) for l in app.materialLibraries])
 for l in app.materialLibraries:
  if l.appearances.count:
   print(l.name,[a.name for a in l.appearances if any(s in a.name.lower() for s in ['plastic - matte','rubber','steel - satin','aluminum - satin'])][:25])
