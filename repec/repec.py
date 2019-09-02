#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import json
import requests
import sys
import traceback
import urllib.parse


REPEC_TOKEN = "V0yH5Swz"


def get_text (url):
    buf = []
    
    try:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        
        for p in soup.find_all("p"):
            buf.append(p.get_text())

        return "\n".join(buf)
    except:
        print(traceback.format_exc())
        sys.exit(-1)


if __name__ == "__main__":
    title = "Withdrawal from Foreign Lending in the Financial Crisis by Parent Banks and Their Branches and Subsidiaries: Supply Versus Demand Effects"

    enc_title = urllib.parse.quote_plus(title)
    cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}".format(enc_title)
    response = requests.get(cgi_url).text
    #print(BeautifulSoup(response, "html.parser").prettify())

    soup = BeautifulSoup(response, "html.parser")
    ol = soup.find("ol", {"class": "list-group"})
    li = ol.findChild()

    handle = li.find("i").get_text()
    print(handle)

    #sys.exit(0)

    api_url = "https://api.repec.org/call.cgi?code={}&getref={}".format(REPEC_TOKEN, handle)
    response = requests.get(api_url).text
    data = json.loads(response)

    print(data[0]["author"].split(" & "))

    print(json.dumps(data, indent=2))
