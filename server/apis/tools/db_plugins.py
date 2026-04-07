from tools.sql import *

#
# db_plugins.py
# table: plugins  (id, plugin_code, is_active, created_at, update_at, data)
#


def plugin_list():
    w = find_in_sql({'table':'plugins','fld':'is_active','val':1,
                     'what':'id,plugin_code,created_at','all':1})
    if type(w) is bool:
        return []
    return w


def plugin_get(plugin_code):
    w = find_in_sql({'table':'plugins','fld':'plugin_code','val':plugin_code,
                     'what':'id,plugin_code,is_active,created_at'})
    if type(w) is bool:
        return None
    return w


def plugin_chk(plugin_code):
    w = find_in_sql({'table':'plugins','fld':'plugin_code','val':plugin_code,
                     'what':'id,is_active'})
    if type(w) is bool:
        return 0
    return int(w[1])


def plugin_add(plugin_code):
    w = find_in_sql({'table':'plugins','fld':'plugin_code','val':plugin_code,
                     'what':'id,is_active'})
    if type(w) is not bool:
        pid = w[0]
        if int(w[1]) == 1:
            return {"status":0,"err":"already installed"}
        return insert_to_sql({'table':'plugins','id':pid,'set':'is_active=1'})
    return insert_to_sql({'table':'plugins','set':f"plugin_code='{plugin_code}',is_active=1"})


def plugin_disable(pid):
    return insert_to_sql({'table':'plugins','id':pid,'set':'is_active=0'})
