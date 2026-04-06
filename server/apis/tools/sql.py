#
#
# kicdev 
# 
# Version 2.03 - support insert_to_sql return "id"
# Version 2.04 - minor, bool01 type
# Version 2.05 - search_in_sql addd "where" as object
# Version 2.06 - zne - gen_data add "data"
# Version 2.07 - ra - support join
# Version 2.08 - ra - unicode heb text , org "\uxyz" 
# Version 2.09 - ra - search in data + more than 1 cond same key
# Version 2.10 - ra - gtoup by + join  with And
# Version 2.11 - ra - in (list) as array
# Version 2.12 - ra - multi join
# Version 2.13 - ra - sql_what - select from data 
# Version 2.14 - ra - sql_sort
# Version 2.15 - bri - where={}
# Version 2.16 - support microFlyton sqlite , t.b.c
#
import os, sys, json, re
from datetime import datetime
sys.path.insert(0, '/usr/local/lib/python3.10/dist-packages')

import importlib.util
import mysql.connector

sql_v =2.16

def find_in_sql(r):
    import sys
    out = sys.__stdout__
    config = kic_config()
    # if_mic = config.get("sys_mic",0) # flyton = 0   , microFlyton=1

    connection = None
    cursor = None
    try:
      out.write(f"[sql] host={config.hostname} user={config.username} db={config.database}\n"); out.flush()
      out.write(f"[sql] calling connect()...\n"); out.flush()
      connection = mysql.connector.connect(
          host=config.hostname,
          user=config.username,
          password=config.password,
          database=config.database
      )
      out.write(f"[sql] connect() returned ok\n"); out.flush()
      cursor = connection.cursor()
      c = 0
      table=r['table']
      tableas=table if " " not in table else table.split(" ")[1]
      q = f"SELECT {sql_what(r['what'])} FROM {table} {sql_join(tableas,r)} WHERE "
      if "fld" in r:
        fld = r["fld"]
        g="`"
        if "." in fld:
          g=""
        q += f"{g}{fld}{g}={kic_geresh(r['val'])}"
        c=c+1
      if "where" in r and r["where"]!={}:
        if c:
          q += " AND "
        q1,c1 = sql_where(r['where'])
        q += q1
        c=c+c1
      if "is_active" in r:
        if c:
          q += " AND "
        q += f"""is_active={r["is_active"]} """
        c=c+1
      if 'grp' in r:
        q += f' GROUP BY {r["grp"]}'
      if 'sortj' in r and r["sortj"]!="":
        q += f' ORDER BY {sql_sortj(r["sortj"])}'
      if 'sort' in r:
        q += f' ORDER BY `{r["sort"]}`'
      if 'desc' in r:
        q += ' DESC'
      if 'limit' in r:
        q += f' LIMIT {r["limit"]}'
      if "debug" in r:
        print(f"<br> sql={q} <br>")
      cursor.execute(q)
      results = cursor.fetchall()
      cursor.close()
      connection.close()
      if results==[]:
        return False
      if "all" in r:
        return results
      return results[0]
    except BaseException as err:
      import sys, traceback
      out = sys.__stdout__
      out.write(f"\n[sql] find_in_sql ERROR: {type(err).__name__}: {err}\n"); out.flush()
      traceback.print_exc(file=out); out.flush()
      if cursor:
        cursor.close()
      if connection:
        connection.close()
      return {"status":err}


# insert or update sql 
#
# r=insert_to_sql({'table':'cust_cont_occ','id':{'cont_id':cont_id,'occ_id':occ_id}'set':'is_active=0'})
# if r["status"]:
#   print("ok")
# update example: w=insert_to_sql({'table':'cust_cont_occ','id':id,'set':'is_active=0'})
# insert example: t=insert_to_sql({'table':'import','set':f"type='cust',count={count}",'data':newdata})


def insert_to_sql(r):

    config = kic_config()
    tera_id= -1
    try:
      connection = mysql.connector.connect(
          host=config.hostname,
          user=config.username,
          password=config.password,
          database=config.database
      )
      cursor = connection.cursor()
      setdata=''
      set1=sql_set(r["set"])
      
      if "data" in r:
        x=r["data"]
        y=json.dumps(x,ensure_ascii=False)
        z=y.replace("'","\\'")    # hebrew fixes
        z=z.replace('ש\\"ח','שח')
        z=z.replace('\\"' ,'')
        z=z.replace('\\\\','/')
        setdata=f",data='{z}'"
      query = f"INSERT INTO {r['table']} SET {set1}{setdata}"
      # print("query",query)
      if "id" in r:
        # g=""
        # if type(r["id"]) is str:
        #   g='"'
        #query = f"""UPDATE {r['table']} SET {set1} WHERE id={g}{r['id']}{g} """
        query = f"""UPDATE {r['table']} SET {set1} WHERE {sql_var('id',r['id'])} """
        if setdata!="":
          err="r['data'] support only new records!!! "
          print(err)
          return {"err":err,"status":False} 
      if "debug" in r:
        print(f"<br>sql={query}<br>")
      cursor.execute(query)
      tera_id = cursor.lastrowid
      connection.commit()
    except mysql.connector.Error as err:
      return {"err":err,"status":False,"query":query}
    finally:
      if cursor:
        cursor.close()
      if connection:
        connection.close()
    return {"results":[],"status":True,"ver":sql_v,"id":tera_id}


def count_in_sql(r):
    file_path = "../config.py"
    spec = importlib.util.spec_from_file_location("config", file_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    
    try:
      connection = mysql.connector.connect(
          host=config.hostname,
          user=config.username,
          password=config.password,
          database=config.database
      )
      cursor = connection.cursor()
      query = f"SELECT COUNT(id) FROM {r['table']} where {r['fld']}='{r['val']}'"
      cursor.execute(query)

      results = cursor.fetchall()

      cursor.close()
      connection.close()

      if results==[]:
        return False
      return results[0]
    except mysql.connector.Error as err:
      return {"status":err}


#
# return company general data
# 1. year 
# 2. maam
#
def gen_data():
  z = find_in_sql({'table':'gen','fld':'is_active','val':1,'what':'*','all':1})
  gen={}
  for x in z:
    id   = x[0]
    name = x[1]
    gd   = x[6]
    gen[name]={"id":id, "val":x[2]}
    if gd!=None and gd:
      gen[name]["data"] = json.loads(gd)

  return gen
  

#
# get data field as object
#
def get_data(table,id,fld="id"):
  z = find_in_sql({'table':table,'fld':fld,'val':id,'what':'data'})
  obj={}
  if type(z) is tuple and z[0]!=None:
    obj=json.loads(z[0])
  return obj


#
# take the data field (json) add info init
#
def add_to_data(table,id,fld1,val1=""):
  obj=get_data(table,id)

  if type(fld1) is str:
    obj[fld1]=val1
    if val1=="!del":
      del obj[fld1]
  if type(fld1) is dict:
    for k in fld1:
      obj[k]=fld1[k]

  sobj = json.dumps(obj,ensure_ascii=False)

  setdata = sql_var("data",sobj)
  
  res = insert_to_sql({'table':table,'set':setdata,'id':id})
  return res




def get_next_counter(field, type1 , data={}):
  gen=gen_data()
  x=gen[f"{type1}_{field}"]
  c=int(x["val"])
  c=c+1
  t=insert_to_sql({'table':'gen','set':f"val1={c}",'id':x["id"]})

  if not t["status"]:
    print("problem with sql write")
    return -1
  for k in data:
    r=add_to_data("gen",x["id"],k,data[k])
  return c
  


# any other sql query
#
#####################
def kic_sql(q,elr=0):
    file_path = "../config.py"
    spec = importlib.util.spec_from_file_location("config", file_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    
    try:
      connection = mysql.connector.connect(
          host=config.hostname,
          user=config.username,
          password=config.password,
          database=config.database
      )
      cursor = connection.cursor()
    
      cursor.execute(q)
      rc = cursor.rowcount
      results = cursor.fetchall()
      connection.commit()
      cursor.close()
      connection.close()

      if elr:
        return { "status":1 , "row_count":rc, "results":results }
      return results
    except mysql.connector.Error as err:
      if cursor:
        cursor.close()
      if connection:
        connection.close()
      return {"status":err}
    

#
# delete record
#
def kic_sql_delete(r):
  q=f'delete from {r["table"]} where id={kic_geresh(r["id"])} limit 1'
  w=kic_sql(q,1)
  if w["row_count"]>0:
    return {"status":1}
  return {"status":0,"err":"not deleted"}

  
  

# return the last bank of importer lines from xl
# type1="cust"
#
def import_state(type1):
    q=f'select count(id),type,count from import where type="{type1}" AND is_active=1 group by count order by count desc limit 1'
    ans = kic_sql(q)
    # print(f"ans = {ans}") #  [(900, 'cust', 8)] 
    if len(ans)==0:
      return { "count":0 ,"lines":0,"updated_at":"" }
    count=ans[0][2]
    lines=ans[0][0]
    
    z = find_in_sql({'table':'gen','fld':'key1','val':type1 + '_import','what':'updated_at'})

    if z==False:
      return { "count":0 ,"lines":0,"updated_at":"" }
    updated_at = z[0]
    return { "count":count,"lines":lines,"updated_at":updated_at }


#
# give me the next id in table
# consider use this method on large tables , but sql will be called for each records , see also sql_order
#
def sql_next(r):
  table=r["table"]
  id=0
  if r["id"]:
    id=r["id"]
  
  if not "is_active" in r: # default only actives
    r["is_active"]=1

  q=f"select * from `{table}` where id>{id}"
  if r["is_active"]:
    q += f""" AND is_active={r["is_active"]} """

  q+=f" order by id limit 1"
  #                 ^^^^^^^

  dict = kic_sql(f"desc `{table}`")

  ans = kic_sql(q)
  if len(ans)==0:
    return { "id":"" }
  obj=array2obj(ans[0],dict)
  return obj

#
# same as sql_next but use yield to return just a single records
# consider use this method on small tables
#
def sql_order(r):
  table=r["table"]
  id=0
  if r["id"]:
    id=r["id"]
  
  if not "is_active" in r: # default only actives
    r["is_active"]=1

  q=f"select * from `{table}` where id>{id}"
  q += f""" AND is_active={r["is_active"]} """
  if "where" in r:
    q += f""" AND {r["where"]}"""

  q += f' order by id'

  dict = kic_sql(f"desc `{table}`")

  ans = kic_sql(q)
  
  for x in ans:
    obj=array2obj(x,dict)
    yield obj


#
#
def array2obj(ary,dict):
  ans={}
  for i in range(len(dict)):
    fld=dict[i][0]
    val=ary[i]
    ans[fld]=val
  return ans
  

cache1 = {} 
def dic_of_table(tab):
  global cache1
  if "dict" in cache1:
    if tab in cache1["dict"]:
      return cache1["dict"][tab]
  dict = kic_sql(f"desc `{tab}`")
  if not "dict" in cache1:
    cache1["dict"] = {}
  cache1["dict"][tab] = dict 
  return dict

  

  
#  
# is table is small general table
# 0 - false 
# 1 - true
#
def is_gen_table(tab):
    g = gen_data()
    gtab=f"{tab}_tab"
    if gtab in g:
        gen_id=g[gtab]["id"]
        d = get_data("gen",gen_id) # {'tab_type': 'gen'} 
        if 'tab_type' in d:
            if d['tab_type']=="gen":
                return 1
    return 0



def kic_refine(x,v,cond):
    if "cln" in cond:
        for cln in cond["cln"]:
            v=v.replace(cln,"")
    if "toLower" in cond:
        v = v.lower()
    if "strip" in cond:
      v=v.strip() # removes the leading and trailing spaces and special whitespace characters like tabs ( \t ) and newlines ( \n ) 
    if "fill_zeros" in cond:
      v=str(v).zfill(cond["fill_zeros"])
    if v!="":
        if "min" in cond:
            if len(v)<cond["min"]:
                return {'status':0,'err':f'length of {x} too small /{v}/'}
        if "max" in cond:
            if len(v)>cond["max"]:
                return {'status':0,'err':f'length of {x} too long'}
        if "exactly" in cond:
            if len(v)!=cond["exactly"]:
                return {'status':0,'err':f'length of {x} must be {cond["exactly"]} == {cond} '}
        if "list" in cond:
            if v not in cond["list"]:
                return {'status':0,'err':f'{x} = ({v}) not in a list {cond["list"]}'}
        if "regex" in cond:
            if not re.search(cond["regex"], v):
                return {'status':0,'err':f'content of {x} must comply to regex'}
        if "is" in cond:
            for ii in cond["is"]:
                if ii=="email":
                    if not validate_email(v):
                        return {'status':0,'err':f'content not a valid email address'}
                if ii=="sum":
                    if v==0:
                        continue
                    if not v:
                        return {'status':0,'err':f'content not a valid sum'}
                if ii=="yesno":
                    if v.strip()=="כן":
                        v=1
                    else:
                        return {'status':0,'err':f'must be yes or no /{v}/'}
                if ii=="date/mdy": # (11/30/2024)
                  v=validate_datemdy(v)
                if ii=="bool01":
                  if v=="0" or v=="1" or v==1 or v==0:
                    v=int(v)
                  else:
                    return {'status':0,'err':f'must be 0 or 1 /{v}/'}
                if ii=="phone":
                  v1=v.replace("-","")
                  if not re.fullmatch(r"\d{10}",v1):
                    return {'status':0,'err':f'phone fromat wrong /{v}/','errcode':101}
    return v    
            
def validate_email(email):
  pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
  return re.match(pattern, email) is not None
    
def validate_datemdy(v):
  d=v.split("/")
  day = int(d[1])
  mon = int(d[0])
  yir = int(d[2])
  y0 = int(datetime.today().strftime('%Y'))
  e=0
  if day>31 or day<1:
    e=1
  if mon>12 or mon<1:
    e=2
  if yir>(y0+10) or yir<(y0-180):
    e=3
  if e:
    return {'status':0,'err':f'date wrong format ({e} / {y0})'}
  if day<10:
    day=f"0{day}"
  if mon<10:
    mon=f"0{mon}"
  v=f"{yir}-{mon}-{day}"
  return v

def kic_config():
  file_path = "../config.py"
  # Load the module
  spec = importlib.util.spec_from_file_location("config", file_path)
  config = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(config)
  return config
    

#
#    smart return value with geresh : value ->  "value"  or 'value'
# 
def kic_geresh(v):
  g = "'"
  if type(v) is str and g in v:
    g='"'
  if type(v) is int or type(v) is float:
    g=""
  return f"""{g}{v}{g}"""
  
#
# get single data field as object
#
def get_record(table,id,fld="id"):
  dict = kic_sql(f"desc `{table}`")
  z = find_in_sql({'table':table,'fld':fld,'val':id,'what':'*'})
  if type(z) is bool:
    return {}
  obj=array2obj(z,dict)
  jdata = get_data(table,id)
  obj = {**obj,**jdata}
  del obj["data"]
  return obj

#
# fix string of mysql set command
# 
# key_name,value -> to string -> key_name="value"
# or
# name=my"name -> `name`="my\"name"
#
# value is dict ->  name='{"key":"val"}'  = if json 
#
def sql_var(k,v,c="="):
  g=""
  r=""
  t=type(v)
  if t is not int and c != " in ":
    g='"'
    if t is dict:
      v=json.dumps(v,ensure_ascii=False)
      g="'"
    if t is str and g in v:
      v=v.replace(g,f'\{g}')
  if k in ["order","key","group","order","limit","from","to"]:
    r="`"
  return f"""{r}{k}{r}{c}{g}{v}{g}"""
  #          name      =  " val "
  # 
# file tmp/res1.txt all reserved words


#
# mysql insert set command from object to string
# 
# {"name":"eli" , "phone":"054-444" } -> object to string -> name="eli",phone="052-444"
#
def sql_set(obj):
  if type(obj) is str:
    return obj
  set1=""
  for k in obj:
    v=obj[k]
    set1 += f",{sql_var(k,v)}"
  return set1[1:]
  
#
# fix the WHERE command as object -> to string , with AND delimiter
#
#  {"where": [ "id":44 , "date":(">","20241228")]
#           vvvvv^^^^^ vvv^^^^^^^^^^^^^^^^^^^^
#    where  id=44 AND date>20241228
# note the tuple if you need extendeed condition( >=,<,in,like default is "="
#

def sql_where(obj):
  if type(obj) is str or type(obj) is int:
    return str(obj),1
  set1=""
  c=0
  for k in obj:
    vv=obj[k]
    v=vv
    con="="
    key = k.split("/")[0]
    if type(vv) is tuple:  # ("like","search")
      con0 = vv[0]   # condition
      v    = vv[1]   # value 
      con=f" {con0} " # " > " or " IN "
      if con0=="in":
        v="(" + ",".join(map(str, v)) + ")" # v= must be (1,3,..) or [1,3,...]
      if con0=="like":
        v=f"%{v}%"
      if len(vv)>2:
        key = f"{vv[2]}->>'$.{key}'"  # for search in data AS json
        #        "data->>'$.price'"
    set1 += f" AND {sql_var(key,v,con)}"
    c=c+1
  return set1[5:],c
  #
  #
  # where = { "is_active" : 1 , ...       } 
  # where = { "date" : (">","2025-07-07") } 
  # where = { "name" : ("like","משה")     }  
  # 
  # where a data json field: 
  #    "data->>'$.price'" > 0  do this :
  # where = { "price" : ( ">" , 0 , "data" )
  #                                 ^^^^^^
  
#
# support join in select
# #find_in_sql({
#         'table': 'pri_prod_brand b',
#         'join' :  [ {"jtab":"pri_prod pp", "on" :"prod_id" } ,
#                     {"jtab":"pri_brand pb", "on" :"brand_id" }
#         ], 
#         'fld':"b.prod_id",
#         'val':prod_id,
#         'all': 1,
#         'what': 'pb.id id,pb.name name,pb.image image'
#     })
def sql_join(tableas, r):

  j=""
  for typ in ("join/INNER","ljoin/LEFT","rjoin/RIGHT"):
    ty=typ.split("/")
    key=ty[0]
    side=ty[1]
    if key in r:
      for join in r[key]:
        jtab = join["jtab"]
        onj  = join.get("jon","id")
        on1  = join["on"]
        jtabas = jtab if " " not in jtab else jtab.split(" ")[1]
        j += f"{side} JOIN {jtab} ON {tableas}.{on1}={jtabas}.{onj} "
        if "And" in join:
          j += f' AND {join["And"]}'
  return j
      

#def sql_data_what(key):
def sqd(key):
  return f"json_extract(data,'$.{key}')"

#
#  "id,name" -> "id,name"          vvvv______vvvv
#  "id,name,data:sort" ->  id,name,data->>"$.sort"
#           ^^^^:^^^^   = for clean 
#
def sql_what(s):
  if ":" not in s:
    return s
  news = ""
  p=""
  for one in str(s).split(","):
    if ":" in one:
      two = one.split(":")
      one=f'{two[0]}->>"$.{two[1]}"'
    news += (p + one)
    p=","
  return news


# sortj options: 
#  sort        or    data:sort  or  data:sort:int  or    data:sort:int/desc 
#  sort::int   or    sort::desc
# 
#  sort desc  - (not recomended)
# 
def sql_sortj(s):
  if ":" not in s:
    return s

  sall = s.split(":")


  l = len(sall) 

  s1 = sall[0]                # data   or  field
  s2 = sall[1] if l>1 else "" # field
  s3 = sall[2] if l>2 else "" # options int/desc

  s = s1

  if s2:
    s=f'{s1}->>"$.{s2}"'

  if "int" in s3:
    s=f'CAST({s} as SIGNED INTEGER)'
    
  if "desc" in s3:
    s=f'{s} DESC'

  return s
  