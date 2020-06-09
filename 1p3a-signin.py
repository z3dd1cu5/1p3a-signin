import sys
import time
import random
import requests
import telegram
import xml.dom.minidom
from bs4 import BeautifulSoup
from vcode import captcha

username= "_"
pswd = "_"
TG_BOT_TOKEN = "_"
TG_USERID = _

def failed(reason):
    bot = telegram.Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=TG_USERID, text="#1point3acres 签到失败，" + str(reason))
    sys.exit(0)

try:
    print("Login...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36"
    }
    r = requests.get("https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&mobile=2", headers=headers)
    if r.status_code != 200:
        failed("/bbs %d" % r.status_code)
    cookies = requests.utils.dict_from_cookiejar(r.cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    post_url = "https://www.1point3acres.com/bbs/" + soup.form.get("action")
    formhash = soup.find(id="formhash").get("value")

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Origin": "https://www.1point3acres.com",
        "Referer": "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&mobile=2"
    }
    data = {
        "formhash": formhash,
        "referer": "https://www.1point3acres.com/bbs/./",
        "fastloginfield": "username",
        "cookietime": 2592000,
        "username": username,
        "password": pswd,
        "questionid": 0,
        "answer": ""
    }
    r = requests.post(post_url, data=data, headers=headers, cookies=cookies)
    if r.status_code != 200:
        failed("/bbs %d" % r.status_code)
    new_cookies = requests.utils.dict_from_cookiejar(r.cookies)
    for key, value in new_cookies.items():
        cookies[key] = value

    print("Sign in...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/"
    }
    r = requests.get("https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no", cookies=cookies, headers=headers)
    if r.status_code != 200:
        failed("/forum %d" % r.status_code)
    new_cookies = requests.utils.dict_from_cookiejar(r.cookies)
    for key, value in new_cookies.items():
        cookies[key] = value
    soup = BeautifulSoup(r.text, "html.parser")
    formhash = soup.find(id="scbar_form").find_all("input")[1].get("value")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no"
    }
    r = requests.get("https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&%s&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign" % formhash, headers=headers, cookies=cookies)
    if r.status_code != 200:
        failed("/plugin %d" % r.status_code)
    if "您今天已经签到过了或者签到时间还未开始" in r.text:
        failed("您今天已经签到过了或者签到时间还未开始")
    idx = r.text.index("updateseccode")
    str_slice = r.text[idx:]
    idhash = str_slice.split("'")[1]

    print("Obtaining captcha link...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no"
    }
    r = requests.get("https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=update&idhash=%s&inajax=1&ajaxtarget=seccode_%s" % (idhash, idhash), headers=headers, cookies=cookies)
    if r.status_code != 200:
        failed("/misc %d" % r.status_code)
    idx = r.text.index("misc.php?mod=seccode&update=")
    url = r.text[idx:].split('"')[0]

    print("Loading captcha...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no"
    }
    r = requests.get("https://www.1point3acres.com/bbs/" + url, headers=headers, cookies=cookies)
    if r.status_code != 200:
        failed("/misc %d" % r.status_code)
    cookies.update(requests.utils.dict_from_cookiejar(r.cookies))
    vcode = captcha(r.content)

    print("Checking captcha...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no"
    }
    r = requests.get("https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=check&inajax=1&&idhash=%s&secverify=%s" % (idhash, vcode), headers=headers, cookies=cookies)
    if r.status_code != 200:
        failed("/misc %d" % r.status_code)
    if "invalid" in r.text:
        print("Captcha Failed.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Origin": "https://www.1point3acres.com",
        "Referer": "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no"
    }
    data = {
        "formhash": formhash,
        "qdxq": "kx",
        "qdmode": 1,
        "todaysay": "今天我啥也没干，麻麻别骂我啊~~",
        "fastreply": 0,
        "sechash": idhash,
        "seccodeverify": vcode
    }
    r = requests.post("https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1", data=data, cookies=cookies, headers=headers)
    if r.status_code != 200:
        failed("/plugin %d" % r.status_code)

    print("Get stat...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36",
        "Referer": "https://www.1point3acres.com/bbs/"
    }
    r = requests.get("https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no", cookies=cookies, headers=headers)
    if r.status_code != 200:
        failed("/forum %d" % r.status_code)
    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join([x.text for x in soup.find_all("a", class_="showmenu")])
    text = "#1point3acres 签到信息\n" + text
    bot = telegram.Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=TG_USERID, text=text)
except Exception as e:
    failed(str(e))
