import os, sys
sys.path.append(os.path.dirname(__file__))
from tools.sql  import *
from tools.db_ses  import *


#
# *** API ***
# check login
#
# called from cgi.py

def login(u,p):
    a= find_in_sql({'table':'users','fld':'username','val':u,'what':'id,sis'})
    #print(f" a = {a}")
    if a==False:
        return False
    uid=a[0]
    sis=a[1]
    if sis==p:
        ses=create_new_ses(uid)
        if ses==0:
            return False
        return {'uid':uid, 'ses':ses}
    else:
        return False

def api_login(data):
    import sys
    out = sys.__stdout__
    out.write("[api_login] start\n"); out.flush()
    i = data["post"]["input"]
    out.write(f"[api_login] u={i.get('u')} p=***\n"); out.flush()
    u = i["u"]
    p = i["p"]
    out.write("[api_login] calling login()\n"); out.flush()
    a=login(u,p)
    out.write(f"[api_login] login() returned: {a}\n"); out.flush()
    print(f',"user":"{u}"')
    if a:
        print(',"allow":1')
        print(f',"ses":"{a["ses"]}"')
    else:
        print(',"allow":0')
    out.write("[api_login] done\n"); out.flush()
    return
    
