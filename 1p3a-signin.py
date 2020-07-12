import sys
import copy
import time
import random
import requests
import telegram
import xml.dom.minidom
from bs4 import BeautifulSoup
from vcode import captcha
from qa import QA

username= "_"
pswd = "_"
TG_BOT_TOKEN = "_"
TG_USERID = _

base_headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Mobile Safari/537.36"
}
cookies = {}

def failed_no_exit(reason):
    bot = telegram.Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=TG_USERID, text="#1point3acres 签到失败，" + str(reason))

def failed(reason):
    failed_no_exit(reason)
    sys.exit(0)

def add_header(headers, key, val):
    new_headers = copy.deepcopy(headers)
    new_headers[key] = val
    return new_headers

def req(url, headers, method, status_code, data=None):
    global cookies
    if method == "GET":
        r = requests.get(url, headers=headers, cookies=cookies)
    elif method == "POST":
        r = requests.post(url, headers=headers, cookies=cookies, data=data)
    if r.status_code != status_code:
        failed("%s %d" % (url, r.status_code))
    cookies.update(requests.utils.dict_from_cookiejar(r.cookies))
    return r

def login():
    try:
        print("Login...")
        r = req(
            "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&mobile=2",
            base_headers, "GET", 200
        )
        soup = BeautifulSoup(r.text, "html.parser")
        post_url = "https://www.1point3acres.com/bbs/" + soup.form.get("action")
        formhash = soup.find(id="formhash").get("value")

        headers = add_header(base_headers, "Origin", "https://www.1point3acres.com")
        headers = add_header(headers, "Referer", "https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&mobile=2")
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
        r = req(post_url, headers, "POST", 200, data=data)

        headers = add_header(base_headers, "Referer", "https://www.1point3acres.com/bbs/")
        r = req(
            "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no",
            headers, "GET", 200
        )
        soup = BeautifulSoup(r.text, "html.parser")
        formhash = soup.find(id="scbar_form").find_all("input")[1].get("value")
    except Exception as e:
        failed(str(e))
    return formhash

def solve_captcha(idhash):
    headers = add_header(base_headers, "Referer", "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no")
    
    print("Obtaining captcha link...")
    r = req(
        "https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=update&idhash=%s&inajax=1&ajaxtarget=seccode_%s" % (idhash, idhash),
        headers, "GET", 200
    )
    idx = r.text.index("misc.php?mod=seccode&update=")
    url = r.text[idx:].split('"')[0]

    print("Loading captcha...")
    r = req(
        "https://www.1point3acres.com/bbs/" + url,
        headers, "GET", 200
    )
    vcode = captcha(r.content)

    print("Checking captcha...")
    r = req(
        "https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=check&inajax=1&&idhash=%s&secverify=%s" % (idhash, vcode),
        headers, "GET", 200
    )
    if "invalid" in r.text:
        return None
    return vcode

def signin(formhash):
    print("Sign in...")
    headers = add_header(base_headers, "Referer", "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no")
    r = req(
        "https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&%s&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign" % formhash,
        headers, "GET", 200
    )
    if "您今天已经签到过了或者签到时间还未开始" in r.text:
        failed_no_exit("您今天已经签到过了或者签到时间还未开始")
        return False
    idx = r.text.index("updateseccode")
    str_slice = r.text[idx:]
    idhash = str_slice.split("'")[1]

    for _ in range(30):
        vcode = solve_captcha(idhash) 
        if vcode:
            break

    headers = add_header(base_headers, "Referer", "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no")
    headers = add_header(headers, "Origin", "https://www.1point3acres.com")
    data = {
        "formhash": formhash,
        "qdxq": "kx",
        "qdmode": 1,
        "todaysay": "good good study, day day up",
        "fastreply": 0,
        "sechash": idhash,
        "seccodeverify": vcode
    }
    r = req(
        "https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1",
        headers, "POST", 200, data=data
    )
    return True

def day_question():
    print("Get day question...")
    headers = add_header(base_headers, "Referer", "https://www.1point3acres.com")
    r = req(
        "https://www.1point3acres.com/bbs/plugin.php?id=ahome_dayquestion:pop&infloat=yes&handlekey=pop&inajax=1&ajaxtarget=fwin_content_pop",
        headers, "GET", 200
    )
    if "您今天已经参加过答题，明天再来吧！" in r.text:
        failed_no_exit("您今天已经参加过答题，明天再来吧！")
        return False
    soup = BeautifulSoup(r.text[53:], "html.parser")
    divs = soup.form.find_all("div")
    question = divs[0].text.replace("【题目】", "").replace("\xa0", " ").strip()
    choices = [[divs[i].text.replace("\xa0", " ").strip(), divs[i].get("onclick").split("'")[1]] for i in range(1, 5)]
    if question not in QA:
        failed_no_exit("题库中找不到该题：\n%s\n%s\n%s\n%s\n%s" % (question, choices[0][0], choices[1][0], choices[2][0], choices[3][0]))
        return False
    answers = QA[question]
    if type(answers) == str:
        answers = [answers]
    found_ans = None
    for choice, ans in choices:
        if choice in answers:
            found_ans = ans
            break
    if not found_ans:
        failed_no_exit("题库中找不到该题的答案：\n%s\n%s\n%s\n%s\n%s" % (question, choices[0][0], choices[1][0], choices[2][0], choices[3][0]))
        return False

    idx = r.text.index("updateseccode")
    str_slice = r.text[idx:]
    idhash = str_slice.split("'")[1]
    formhash = soup.input.get("value")

    for _ in range(30):
        vcode = solve_captcha(idhash) 
        if vcode:
            break

    headers = add_header(base_headers, "Origin", "https://www.1point3acres.com")
    headers = add_header(headers, "Referer", "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no")
    data = {
        "formhash": formhash,
        "answer": found_ans[1],
        "sechash": idhash,
        "seccodeverify": vcode,
        "submit": "true"
    }
    r = req(
        "https://www.1point3acres.com/bbs/plugin.php?id=ahome_dayquestion:pop",
        headers, "POST", 200, data=data
    )

def get_stat():
    print("Get stat...")
    headers = add_header(base_headers, "Referer", "https://www.1point3acres.com")
    r = req(
        "https://www.1point3acres.com/bbs/forum.php?mod=guide&view=hot&mobile=no",
        headers, "GET", 200
    )
    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join([x.text for x in soup.find_all("a", class_="showmenu")])
    text = "#1point3acres 签到信息\n" + text
    bot = telegram.Bot(token=TG_BOT_TOKEN)
    bot.send_message(chat_id=TG_USERID, text=text)

if __name__ == "__main__":
    formhash = login()
    signin(formhash)
    day_question()
    get_stat()
