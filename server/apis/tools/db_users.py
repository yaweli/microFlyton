# tools/db_user.py
# Helper functions for users table - Flyton style

import os, sys, json
sys.path.append(os.path.dirname(__file__))
from sql import *

def get_user(user_id):
    return get_record("users", user_id)

def is_role(user_id,role):
    # Roles is JSON array string like ["admin","owner"]
    row = find_in_sql({
        'table': 'users',
        'fld'  : 'id',
        'val'  : user_id,
        'what' : 'Roles'
    })
    
    if not row:
        return False
    
    roles_json = row[0] or "[]"
    # simple fast check - Flyton prefers this over json.loads when possible
    if f'"{role}"' in roles_json:
        return 1
    return 0


def is_owner(user_id):
    return is_role(user_id,"owner")

def is_admin(user_id):
    return is_role(user_id,"admin")


def is_page_allowed(page, user_id):
    PAGE_ROLES = {
        "dashboard":   [],
        "users":       ["admin","owner"],
        "sys_admin":   ["admin","owner"],
        "sys_plugins": ["admin","owner"],
        "sys_profile": [],
    }
    roles = PAGE_ROLES.get(page, ["admin","owner"])
    if not roles:
        return 1
    return any(is_role(user_id, r) for r in roles)
    

def get_user_custs(user_id):
    if is_owner(user_id):
        # owner sees all active customers
        return find_in_sql({
            'table': 'cust',
            'what' : 'id,name',
            'all'  : 1,
            'where': {'is_active': 1},
            'sort' : 'name'
        }) or []
    
    # normal user — only from data JSON
    user_data = get_data("users", user_id)
    cust_id = user_data.get("cust", None)
    
    if not cust_id:
        return []
    
    cust = find_in_sql({
        'table': 'cust',
        'what' : 'id,name',
        'fld'  : 'id',
        'val'  : cust_id
    })
    
    return [cust] if cust else []
    

        
def list_users(r={}):
    where = {"id":(">",2000)}
    if "all" in r and r["all"]:
        where  = {"id":(">",0)}
    w = find_in_sql({"table":"users","what":"id","where":where,"all":1})
    return w



def chk_user(r):
    pass
    return r


def add_user(r):
    pass
    
    