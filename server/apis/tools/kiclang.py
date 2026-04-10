############################################################################
#
# Single : english to hebrew  - !! linguale
# ver kicdev 1.01 - for zohar neeman
# usage: print("""  fix title: {txt("Person name",":")} {PersonName}""") 
#                   ^^^        ^^^ = translated   ^^^   ^^^=not translated
#                   not translated   part1        part2
# 
# to be continue
######################
_lang = "en"

def set_lang(lang):
    global _lang
    _lang = lang

def txt(*args, **kwargs):
    #example : txt("Alice", "Bob", "Charlie", age=30, city="New York")
    #              args[]                     kwargs[][]
    #global base
    #print(base)
    a=""
    for z in args:
        a += txt1(z)
    return a
    
    
#
# return one sentence translated and edited
#
def txt1(z):
    before,after,s = txtGetProp(z)
    snew = txtDic(s)
    snew = f"""{before}{snew}{after}"""
    return snew

#
# return one sentence translated
#
def txtDic(z):
    if _lang == "en":
        return z

    global dictionary
    if dictionary is None:
        dictionary = load_dictionary()

    return dictionary.get(z, z)


#
# break dirty sentence into spaces + clean sentence
# " word1 word2   " -> before=" " ,after="   ", s="word1 word2"
#
def txtGetProp(z):    
    before=""
    after=""
    mode=0
    s=""
    for char in z:
        if mode==0 and char==" ":
            before+=" "
            continue
        if char!=" ":
            mode=1
        if mode==1:
            s += char
    if mode==1:
        for char in reversed(z):
            if mode==1 and char==" ":
                after += " "
                s = s[:-1]
                continue
            if char!=" ":
                break
    return before,after,s
        


#
#
#
import json

def load_dictionary():
    return {
        "Total": "סך הכל",
        "users": "משתמשים",
        "customers": "לקוחות",
        "Id": "מזהה",
        "Username": "שם משתמש",
        "Full Name": "שם מלא",
        "Roles": "תפקידים",
        "Subscriber": "מנוי",
        "Status": "סטטוס",
        "Actions": "פעולות",
        "Activate": "הפעל",
        "Deactivate": "השבת",
        "Active": "פעיל",
        "Inactive": "לא פעיל",
        "System Users": "משתמשי מערכת",
        "Import User": "ייבוא משתמש",
        "+ Add User": "הוסף משתמש",
        "Export QR": "ייצוא QR",
        "Edit": "ערוך",
        "Back to Dashboard": "חזרה ללוח הבקרה",
        "Owner – protected": "בעלים – מוגן",
    }


    # with open('/data/media/dictionary.json', 'r') as f:
    #     return json.load(f)

dictionary = None

# def translate(word):
#     global dictionary
#     if dictionary is None:
#         dictionary = load_dictionary()

#     return dictionary.get(word, word)  # Default to the original word if not found

# # Example usage:
# translated_word = translate("hello")
# print(translated_word)