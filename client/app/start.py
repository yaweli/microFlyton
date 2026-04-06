import os, sys
sys.path.append(os.path.dirname(__file__))
from tools.sql  import *



# import header,body,footer  
from admin.header import *
from admin.footer import *
from admin.body   import * 


# note: multi header here: /Neeman/server/cgi-bin/p4web.py

# #global base
# base = {
#     "soft_lang" : "en_us",
#     "targ_lang" : "he_il"
# } 



def main(data):
    # session
    ses = data["ses"]
    # session data saved on our side
    # sdata is out side session data
    # first time , it's empty
    
    w=find_in_sql({'table':'ses','fld':'id','val':ses,'what':'user_id,is_active',"is_active":1})

    if type(w) is bool and w==False:
        print("unothorized")
        return ""

    my_user_id   = w[0]

    sdata = get_data("ses",ses)
    sdata["my_user_id"] = my_user_id

    data["s"]=sdata

    # redirect page
    if "rpage" in data:
        data["s"]["page"]=data["rpage"]
    # default first time page
    if not "page" in data["s"]:
        data["s"]["page"]="dashboard"
    header(data)
    body_admin(data)
    footer(data)
 

