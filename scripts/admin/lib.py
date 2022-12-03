
import os
import urllib.parse
from lxml import html

URL_BASE = 'https://hyc.ie'
USERNAME = os.environ.get('ADMIN_USERNAME')
PASSWORD = os.environ.get('ADMIN_PASSWORD')

def login(session):
    result = session.get(URL_BASE + "/login")
    tree = html.fromstring(result.text)
    authenticity_token = tree.xpath("//input[@name='authenticity_token']/@value")[0]

    payload = {
        'authenticity_token': authenticity_token,
        'user_session[login]': USERNAME,
        'user_session[password]': PASSWORD,
    }

    return session.post(URL_BASE + "/login", data=payload)

def get_events(session, event_type, year):
    result = session.get(URL_BASE + "/admin/results/{}?event_type={}&year={}&&commit=Filter".format(event_type, event_type, year))
    tree = html.fromstring(result.text)
    return tree.xpath("//select[@id='event_title']/option/@value")

def get_edit_refs(session, event_type, year, event_title):
    result = session.get(URL_BASE + "/admin/results?event_title={}&event_type={}&year={}".format(urllib.parse.quote(event_title), event_type, year))
    tree = html.fromstring(result.text)
    return tree.xpath("//tr/td[3]/a[2]/@href")

def get_result(session, edit_ref):
    result = session.get(URL_BASE + edit_ref)
    tree = html.fromstring(result.text)
    try:
        ftp_path = tree.xpath("//input[@name='result[ftp_path]']/@value")[0]
    except IndexError:
        ftp_path = ''
    return {
        "id": edit_ref.split("/")[3],
        "event": tree.xpath("//input[@name='result[event_title]']/@value")[0],
        "class_name": tree.xpath("//input[@name='result[class_name]']/@value")[0],
        "ftp_path": ftp_path
    }

def update_ftp_path(session, edit_ref, ftp_path):
    result = session.get(URL_BASE + edit_ref)
    tree = html.fromstring(result.text)
    data = {}
    inputs = [ "utf8", "authenticity_token", "result[event_type]", "result[year]", "result[event_title]", "result[class_name]"]
    for i in inputs:
        data[i] = tree.xpath("//input[@name='{}']/@value".format(i))[0]
    data["result[ftp_path]"] = ftp_path
    edit_ref = edit_ref.replace("/edit", "")
    return session.put(URL_BASE + edit_ref, data=data)
