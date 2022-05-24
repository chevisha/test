import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import xmlrpc.client
from flask_caching import Cache
import json 
import re
from operator import itemgetter

NEAREST = 100
NUM_RES = 40
SCREENFUL = 40
backend_port = 8101
rank_port = 8076
backend_address = "127.0.0.1"
DIST_THRESHOLD = 0.3
N_GRAM=10


most_common=set() 
cnt=dict()
kkk=0
with open("most_common.txt", "r") as f:
    
    for i in f:
        tmp=[]
        for h in i.split():
            if(h is not 'cnt:'):
                tmp.append(h)
            else:
                break
        
        most_common.add(' '.join(i.split()[0:len(tmp)-2]))


with open("most_common.txt", "r") as f:
    for i in f:
        tmp=[]
        for h in i.split():
            if(h is not 'cnt:'):
                tmp.append(h)
            else:
                break
        cnt[' '.join(i.split()[0:len(tmp)-2])]=int(i.split()[-1])


app = flask.Flask(__name__)
app.config["DEBUG"] = True

CORS(app, supports_credentials=True)

cache = Cache()

cache.init_app(app,
            config={'CACHE_TYPE': 'MemcachedCache',
                    'CACHE_DEFAULT_TIMEOUT': 0,
                    })



blacklist_file = open("/var/www/backendService/blacklist.json", "r")
blacklist = json.load(blacklist_file)
blacklist_file.close()

blacklist_nodes = set(blacklist)

def clear_puncts(text):
    return re.sub(" +", " ", re.sub(r'[^\w\s]', ' ', text.lower()))

# @cache.memoize()
def api_search(query):

    print(f"query: {query}")

    with xmlrpc.client.ServerProxy("http://" + backend_address + ":"+str(backend_port)+"/") as proxy:
        results = proxy.fetch_causes_effects(query, rank_port, True)
    
    read_edges = set()
    final_results = {"causes": [], "effects": []}
    
    for type, arr in results.items():
        for edges_data in arr:
            edge = str(edges_data["edge"])
            cause, effect = edge.split("\t")[:2]
            if clear_puncts(edge) in read_edges or cause in blacklist_nodes or effect in blacklist_nodes:
                continue
            edges_data["edge"] = edge
            edges_data['sent'] = str(edges_data['sent'])
            edges_data['link'] = str(edges_data['link'])
            edges_data['prev_sent'] = str(edges_data['prev_sent'])
            read_edges.add(clear_puncts(edge))
            final_results[type].append(edges_data) 

    

 

    
    for i in final_results['effects']:
        edge=i['edge']
        left=str(edge.split('\t')[0])
        right=str(edge.split('\t')[1])
        leftList=right.split()

        uSetu=[]
        for ii in range(N_GRAM):
            for j in range(len(leftList)-ii):
                if(' '.join(leftList[j:j+ii+1]).lower() in most_common):
                    #print(' '.join(leftList[j:j+i+1])+' je u setu')
                    uSetu.append(' '.join(leftList[j:j+ii+1]))
  
        ocu=list()
        candidates=list()
        for ii in uSetu:
            ocu=[m.start() for m in re.finditer(ii.lower(), right.lower())]
            for j in ocu:
                candidates.append([j+len(left)+1,j+len(ii)+len(left),cnt[ii.lower()]])
        candidates= sorted(candidates, key=itemgetter(2),reverse=True)    
        
        real=list()
        if(len(candidates)==0):continue
        real=[]
        real.append([candidates[0][0],candidates[0][1]])

        
        for ii in range(1,len(candidates)):
            trt=1
            for j in real:
                if(candidates[ii][1]>j[0] and candidates[ii][0]<j[1]):
                    trt=0
                    break
            if(trt):real.append([candidates[ii][0],candidates[ii][1]])
        link=[]
       
        for ii in real:

            link.append({'href':edge[ii[0]:ii[1]+1].replace(' ','-'),"idx":ii})
       ########################################
        leftList=left.split()

        uSetu=[]
        for ii in range(N_GRAM):
            for j in range(len(leftList)-ii):
                if(' '.join(leftList[j:j+ii+1]).lower() in most_common):
                    #print(' '.join(leftList[j:j+i+1])+' je u setu')
                    uSetu.append(' '.join(leftList[j:j+ii+1]))
  
        ocu=list()
        candidates=list()
        for ii in uSetu:
            ocu=[m.start() for m in re.finditer(ii.lower(), left.lower())]
            for j in ocu:
                candidates.append([j,j+len(ii)-1,cnt[ii.lower()]])
        candidates= sorted(candidates, key=itemgetter(2),reverse=True)    
        
        real=list()
        if(len(candidates)==0):continue
        real=[]
        real.append([candidates[0][0],candidates[0][1]])

        
        for ii in range(1,len(candidates)):
            trt=1
            for j in real:
                if(candidates[ii][1]>j[0] and candidates[ii][0]<j[1]):
                    trt=0
                    break
            if(trt):real.append([candidates[ii][0],candidates[ii][1]])
 
        
        for ii in real:

            link.append({'href':edge[ii[0]:ii[1]+1].replace(' ','-'),"idx":ii})

        
        
        i['links']=link



#############
    for i in final_results['causes']:
        edge=i['edge']
        left=str(edge.split('\t')[0])
        right=str(edge.split('\t')[1])
        leftList=right.split()

        uSetu=[]
        for ii in range(N_GRAM):
            for j in range(len(leftList)-ii):
                if(' '.join(leftList[j:j+ii+1]).lower() in most_common):
                    #print(' '.join(leftList[j:j+i+1])+' je u setu')
                    uSetu.append(' '.join(leftList[j:j+ii+1]))
  
        ocu=list()
        candidates=list()
        for ii in uSetu:
            ocu=[m.start() for m in re.finditer(ii.lower(), right.lower())]
            for j in ocu:
                candidates.append([j+len(left)+1,j+len(ii)+len(left),cnt[ii.lower()]])
        candidates= sorted(candidates, key=itemgetter(2),reverse=True)    
        
        real=list()
        if(len(candidates)==0):continue
        real=[]
        real.append([candidates[0][0],candidates[0][1]])

        
        for ii in range(1,len(candidates)):
            trt=1
            for j in real:
                if(candidates[ii][1]>j[0] and candidates[ii][0]<j[1]):
                    trt=0
                    break
            if(trt):real.append([candidates[ii][0],candidates[ii][1]])
        link=[]
       
        for ii in real:

            link.append({'href':edge[ii[0]:ii[1]+1].replace(' ','-'),"idx":ii})
       ########################################
        leftList=left.split()

        uSetu=[]
        for ii in range(N_GRAM):
            for j in range(len(leftList)-ii):
                if(' '.join(leftList[j:j+ii+1]).lower() in most_common):
                    #print(' '.join(leftList[j:j+i+1])+' je u setu')
                    uSetu.append(' '.join(leftList[j:j+ii+1]))
  
        ocu=list()
        candidates=list()
        for ii in uSetu:
            ocu=[m.start() for m in re.finditer(ii.lower(), left.lower())]
            for j in ocu:
                candidates.append([j,j+len(ii)-1,cnt[ii.lower()]])
        candidates= sorted(candidates, key=itemgetter(2),reverse=True)    
        
        real=list()
        if(len(candidates)==0):continue
        real=[]
        real.append([candidates[0][0],candidates[0][1]])

        
        for ii in range(1,len(candidates)):
            trt=1
            for j in real:
                if(candidates[ii][1]>j[0] and candidates[ii][0]<j[1]):
                    trt=0
                    break
            if(trt):real.append([candidates[ii][0],candidates[ii][1]])
 
        
        for ii in real:

            link.append({'href':edge[ii[0]:ii[1]+1].replace(' ','-'),"idx":ii})

        
        
        i['links']=link
    
        

        

        

    '''
    
    
    for i in final_results['effects']:
        t=i['edge']
        string=""
        for j in t.split():
            string+=j.lower()+' '
        string=' '+string+' '
        link=[]
        o=dict()
        string2=''
        for j in links:
            if(query==j.lower()):
                continue
            string2=' '+j.lower()+' '
            try:
                ocu=[m.start() for m in re.finditer(string2, string)]
            except:
                continue
            if(len(ocu)):
                print(string2+'<>',string,"   ",ocu)
                link.append({'href':'https://qaagi.com/causes-and-effects/'+string2[1:-1].replace(' ','-'),'idxA':ocu,'idxB': [x+len(string2)-3 for x in ocu]})
                i['links']=link
    
    for i in final_results['causes']:
        t=i['edge']
        string=""
        for j in t.split():
            string+=j.lower()+' '
        string=' '+string+' '
        link=[]
        o=dict()
        string2=''
        for j in links:
            if(query==j.lower()):
                continue
            string2=' '+j.lower()+' '
            
            ocu=[m.start() for m in re.finditer(string2, string)]
            if(len(ocu)):
                print(string2+'<>',string,"   ",ocu)
                link.append({'href':'https://qaagi.com/causes-and-effects/'+string2[1:-1].replace(' ','-'),'idxA':ocu,'idxB': [x+len(string2)-3 for x in ocu]})
                i['links']=link
    '''
  
   


    results = final_results
    #results['causes'].sort(key= lambda x: x['rank'], reverse=True)
    #results['effects'].sort(key= lambda x: x['rank'], reverse=True)


    results['causes'] = results['causes'][:SCREENFUL]
    results['effects'] = results['effects'][:SCREENFUL]
    
   
    
    return results

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Demo search API VUK</h1>
<p>Demo API.</p>'''

@app.route('/api/search', methods=['GET'])
@cross_origin()
def api_query():
    keep_keys = set(['sent','edge'])
    if 'query' in request.args:
        query = request.args['query']
    else:
        return "Error: No id field provided. Please specify an id."
    ret = {'effects':[], 'causes':[]}
    search_result = api_search(query)
    for x in search_result['effects']:
        tmp = {}
        for key in x:
            if key in keep_keys:
                tmp[key] = x[key]
        ret['effects'].append(tmp)
    for x in search_result['causes']:
        tmp = {}
        for key in x:
            if key in keep_keys:
                tmp[key] = x[key]
        ret['causes'].append(tmp)

    return jsonify(ret)

@app.route('/api/dev/search', methods=['GET'])
@cross_origin()
def api_query_dev():
    if 'query' in request.args:
        query = request.args['query']
    else:
        return "Error: No id field provided. Please specify an id."    
    search_result = api_search(query)
    return jsonify(search_result)


if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8889)

#####   legacy code(not in use)   ######
'''
def api_search_cause(query):
    global v
    seen = set()
    result = []
    #query = query[2:]
    print('CAUSES OF:%s' % query)
    em = embed_fn([query])
    sys.stderr.write('Query embedding completed ...\n')
    res,dst = zip(*v.search_by_vector(em[0],NEAREST,include_distances=True,ef_search=NEAREST*2))
    print_edge(res,dst,NUM_RES)
    em_causes_vecs = embed_fn([from_nodes[r]+' caused ' for r in res])
    sys.stderr.write('Query embedding of cause list completed ...\n')
    em_causes_distances = [numpy.dot(em[0],v) for v in em_causes_vecs]
    em_causes = list(zip(res,em_causes_distances,[from_nodes[r] for r in res]))
    em_causes.sort(key=lambda tup: tup[1], reverse=True)
    k = 0
    for r,d,_ in em_causes :
            if d <= DIST_THRESHOLD or k >= SCREENFUL: break
            if from_nodes[r] not in seen:
                # sys.stdout.write('V1:: %4.2f' % d+'::'+from_nodes[r])
                #sys.stdout.write('V1:: %4.2f' % d+'::'+from_nodes[r].rstrip()+' ==> '+to_nodes[r])
                result.append('V1:: %4.2f' % d+'::'+from_nodes[r].rstrip()+' ==> '+to_nodes[r])
                k = k+1
            seen.add(from_nodes[r])
    return result
def api_search_effect(query):
    global v
    seen = set()
    result = []
    #query = query[:-2]
    print('EFFECTS OF:%s' % query)
    em = embed_fn([query])
    sys.stderr.write('Query embedding completed ...\n')
    # res,dst = u.search_by_vector(em[0],NEAREST,include_distances=True)
    # res,dst = zip(*u.search_by_vector(em[0],NEAREST,include_distances=True))
    res,dst = zip(*u.search_by_vector(em[0],NEAREST,include_distances=True,ef_search=NEAREST*2))
    print_edge(res,dst,NUM_RES)
    em_effects_vecs = embed_fn([' caused '+to_nodes[r] for r in res])
    sys.stderr.write('Query embedding of effect list completed ...\n')
    em_effects_distances = [numpy.dot(em[0],v) for v in em_effects_vecs]
    em_effects = list(zip(res,em_effects_distances,[to_nodes[r] for r in res]))
    em_effects.sort(key=lambda tup: tup[1], reverse=True)
    k = 0
    for r,d,_ in em_effects :
            if d <= DIST_THRESHOLD or k >= SCREENFUL: break
            if to_nodes[r] not in seen:
                # sys.stdout.write('V1:: %4.2f' % d+'::'+to_nodes[r])
                #sys.stdout.write('V1:: %4.2f' % d+'::'+from_nodes[r].rstrip()+' ==> '+to_nodes[r])
                result.append('V1:: %4.2f' % d+'::'+from_nodes[r].rstrip()+' ==> '+to_nodes[r])
                k = k+1
            seen.add(to_nodes[r])
    return result
'''