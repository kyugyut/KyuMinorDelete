import session
from bs4 import BeautifulSoup
from monkey import magic_code
import re
import time

def minor_delete(gall_id,article):
    time.sleep(0.1)
    header = {
        'X-Requested-With' : "XMLHttpRequest",
        'Referer' : "https://gall.dcinside.com/mgallery/board/delete/?id=" + gall_id + "&no=" + article,
        'Origin' : "https://gall.dcinside.com"
    }
    session.get("https://gall.dcinside.com/mgallery/board/view/?id=" + gall_id + "&no=" + article)
    res = session.get("https://gall.dcinside.com/mgallery/board/delete/?id=" + gall_id + "&no=" + article)
    payload = {}
    try:
        bfdoc = BeautifulSoup(res.text,'html.parser')
        form = bfdoc.body.find('form',{'id':"delete"})
        hidden_payload = form.find_all('input')
    except Exception:
        return "false"
    for value in hidden_payload:
        payload[value.get('name')] = value.get('value')

    r = None
    x = None
    sc_list = bfdoc.body.find_all('script')
    for script in sc_list:
        r = re.search("_d\('(.*?)'",script.text)
        if r is not None:
            r = r.groups()[0]
            x = re.search("formData.?\+=.?\"&(.*?)\"",script.text).groups()[0]
            break
    x = x.split('=')
    payload[x[0]] = x[1]
    payload['service_code'] = magic_code(payload['service_code'],r)
    res = session.post("https://gall.dcinside.com/board/forms/delete_submit",header,payload)
    return res.text