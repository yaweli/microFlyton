import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from kiclang        import *

# 
# Ver: 2025.11.11.zne
#

#
# add more param to url 
#
def kic_more(more):
    a=""
    for x in more:
        if not x in ["use"]:
            val = str(more[x]).replace(" ","+")
            a+=f"&{x}={val}"
    return a

#
# url of link to next page
#
# start for admin  webapp
def kicnav(page,ses,more={},app="start"):
    return f"/cgi-bin/p?app={app}&r=309012&ses={ses}&rpage={page}{kic_more(more)}"

#
# link to next page
#
def kicmenu(page,ses,title,cls="kicmenu"):
    url=kicnav(page,ses)
    return f'<a class="{cls}" href="{url}">{title}</a>'
    
#
#   more = { "use" : "formvar1,formvar2,..." } = value of form item wil  be added to the url 
#            "tab" : "ins" = will be added to the url , data["tab"]
#             "*"  : 
#
def kicbutton(page,ses,title,cls="kicmenu",more={},app="start"):
    url=kicnav(page,ses,more,app)
    use=more.get("use","")
    # print(use)
    return f'<button class="{cls}" onclick=kic_run_but("{url}","{use}")>{title}</button>'


#
# you must load it before isung buttons
# print(kicbutton0())
#
def kicbutton0():
    return """
    <script>
    function kic_run_but(url,use){
        
        if (event.target.innerHTML) 
        {
            event.target.disabled=true;
            event.target.innerHTML = " ..המתן.. "; 
        }
        

        if (typeof(use)!="undefined" && use.length)
        {
        
            use.split("/").forEach(function (item) {
                var el = document.getElementById(item) ; 
                vvv = el.value;
                if ( el.type=="radio" || el.type=="checkbox") {
                    if ( el.checked ) 
                    {
                        url += "&" + el.name + "=" + vvv;
                    }
                } else 
                {
                    url += "&" + item + "=" + vvv;
                }
                });
        }
        if (url.includes("app=admin"))
        {
            el = document.getElementById("menu00");
            el.innerHTML='<div class="spinner-grow text-danger"></div> &nbsp;Loading ... ';
        }
        document.location=url;
    }
    </script>
    """
    
    
#
# card:
# well design menu item , with place for explanation
#
def kic_collapse(title,explain,button_text,ses,page):
    return f"""
<div class="card">
    <div class="card-header" data-bs-toggle="collapse" data-bs-target="#{page}">
        {title} 
    </div>
    <div id="{page}" class="collapse">
        <div class="card-body">
            <div class="explanation">
                {explain}
            </div>
        </div>
        <div class="card-footer">
        {kicbutton(page,ses,button_text,"btn btn-primary")}
            </div>
    </div>
</div>"""

# 
# print(kicselect("org","select Organization","org",{"tab":"org","value":data.get("she","")}))
#
def kicselect(id,label,more={}):
    def1 = more["value"]
    dis=""
    if "disable" in more:
        if more["disable"]:
            dis=" disabled"
    return f"""
    <div style="width:300px" class="mb-3">
        <label for="{id}" class="form-label"> {label}</label>

        <select id={id} name={id} class="form-select" aria-label="{id}" {dis}>
        {kicselect_def(more)}
        {kicselect_o(def1,more["data"])}
        </select>
    </div>
        """


def kicselect_def(more):
    if "empty" in more:
        return "<option value=0>None</option>"


def kicselect_o(def1,data):
    a=""
    for x in data:
        id=x[0]
        name=x[1]
        sel=""
        if id==def1:
            sel=" selected"
        a += f"<option{sel} value={id}>{name} - {id}</option>"
    return a


def kiccard(title,title1,explain,button_text="",ses="",page="",more={}):
    title1 = str(title1)
    explain = str(explain)
    old = """
            <h5 class="card-header">
            <span>{title}</span>
            </h5>
    """
    strlen = "450px"
    if "width" in more:
        strlen = more["width"]
    cls1=""
    if "cls" in more:
        cls1=more["cls"]
    if "color" in more:
        color=more["color"]
        if color=="red":
            cls1="bg-danger"
        if color=="green":
            cls1="bg-success"
        if color=="grey":
            cls1="bg-secondary"
    return f"""
        <div class="card {cls1}" style=width:{strlen}>
            <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{txt(title)}</h5>
            <span class="ms-auto">{kic_icon(title,more)}</span>
            </div>            
            <div class="card-body">
                <h5 class="card-title">{txt(title1)}</h5>
                <p class="card-text">{txt(explain)}</p>
                {cond_but(page,ses,button_text,more)}
            </div>
        </div>
    """

def kic_icon(title,m):
    if "icon" in m:
        return m["icon"]
    if "Insurance" in title:
        return "&#x1F6E1;"
    if "Organizations" in title:
        return "&#x1F465;"
    if "Occupation" in title:
        return "&#x1F4BC;"
    return ""
    

def cond_but(page,ses,button_text,more):
    if button_text=="":
        return ""
    cls="primary"
    if "but_cls" in more:
        cls=more["but_cls"]
    return kicbutton(page,ses,button_text,f"btn btn-{cls}",more)




def kicinput(id,label,placeh,more={}):
    a= f"""
<div class="mb-3">
  <label for="usernameInput" class="form-label">{label}</label>
  <input type="text" class="form-control " id="{id}" placeholder='{placeh}'
    """
    if "onchange" in more:
        a+=f""" onchange="{more["onchange"]}" """
    if "value" in more:
        a+=f""" value="{more["value"]}" """
    a+= """
  >
  <div class="valid-feedback">Looks good!</div>
  <div class="invalid-feedback">wrong data </div>
</div>"""
    return a






# convert dates
# h = is a datetime object
def kic_date(h,format="%Y-%m-%d"):
    if h=="" or h=="now":
        h=datetime.today()
    if format=="-":
        format="%Y-%m-%d"
    if format=="y0":
        format="%Y"
    if format==8 or format=="disp":
        format="%d-%m-%Y"
    if format==6:
        format="%m/%d/%Y"
    if format==3 or format=="int":
        format="%Y%m%d"
        return int(h.strftime(format))
    if format=="dif": # never used - TODOmake iit simple
        date1 = datetime.datetime(h[0], h[1], h[2])
        date2 = datetime.datetime(h[4], h[5], h[6])
        #date2 = datetime.datetime(2023, 12, 25)
        
        # Calculate the difference in days
        difference = date2 - date1        
        return difference
    return h.strftime(format)
