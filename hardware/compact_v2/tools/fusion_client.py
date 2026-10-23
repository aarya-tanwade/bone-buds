"""Client for Autodesk's official local Fusion MCP endpoint. No GUI emulation."""
import urllib.request,json,sys,pathlib,base64
URL='http://127.0.0.1:27182/mcp'
def request(body,session=None):
    h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
    if session:h['MCP-Session-Id']=session
    r=urllib.request.urlopen(urllib.request.Request(URL,json.dumps(body).encode(),h),timeout=600)
    data=r.read().decode();return (json.loads(data) if data else {},r.headers.get('MCP-Session-Id'))
def call(name,args):
    _,sid=request({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'BoneBuds-Codex','version':'1.0'}}})
    request({'jsonrpc':'2.0','method':'notifications/initialized'},sid)
    result,_=request({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':name,'arguments':args}},sid)
    return result
if __name__=='__main__':
    if sys.argv[1]=='--script':res=call('fusion_mcp_execute',{'featureType':'script','object':{'script':pathlib.Path(sys.argv[2]).read_text(encoding='utf8')}})
    else:res=call(sys.argv[1],json.loads(sys.argv[2]))
    print(json.dumps(res,ensure_ascii=True))
