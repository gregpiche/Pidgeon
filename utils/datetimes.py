import time
import locale

# Added proper suffix to date
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

# Format date in English
def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Format date in French
def get_date_french():
    loc = 'fr' 
    locale.setlocale(locale.LC_ALL, loc)
    return time.strftime("%d %b %Y")