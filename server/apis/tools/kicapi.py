    
#
# return ok message from python server side
#
def api_ok(more={}):
    print(f',"allow":1')
    print(mores(more))

#
# return Error message from python server side
#
def api_err(msg,more={}):
    print(f',"allow":0,"msg":"{msg}"')
    print(mores(more))
    return 0
    

#
# return more keys in an object string - as result coming back from python server side
# object -> to string
# { "price":100.40 , "mam" : 0.18 } ->   ,"price":"100.40","mam":"0.18" 
#
# so the answer from api will return more data from the server , for use or for logs
#
def mores(more):
    s = ""
    for o in more:
        s += f',"{o}":"{more[o]}"'
    return s