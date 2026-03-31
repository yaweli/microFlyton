import os, sys
import importlib


def body_admin(data):
    page = data["s"]["page"]
    #
    # code subdirectiries
    # 
    add="admin."
    if page.startswith("tab"):
        add="admin.tabs."
    if page.startswith("test"):
        add="admin.test."
    if page.startswith("card_"):
        add="admin.test."
    print(f"<!-- page = {page} add = {add} file= {__file__}  -->")
    #
    #
    mod = f"{add}{page}"
    module = importlib.import_module(mod)
    # locals()["page"]()
    # locals()[function_name]()
    #foo=globals()[page]
    foo = getattr(module, page)
    print(f"""
       <div class="container-fluid">
            <div class="row kicbody" id=zzz>
            {foo(data)}
            </div>
       </div>    """)


