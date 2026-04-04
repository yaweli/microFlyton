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
    i = data["post"]["input"]
    u = i["u"]
    p = i["p"]
    a=login(u,p)
    print(f',"user":"{u}"')
    if a:
        print(',"allow":1')
        print(f',"ses":"{a["ses"]}"')
    else:
        print(',"allow":0')
    return
    
