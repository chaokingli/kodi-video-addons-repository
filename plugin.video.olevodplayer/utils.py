# -*- coding: utf-8 -*-
import re
import xbmc
import xbmcgui
import ssl
from urllib import request

import xbmcvfs
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context


def custom_header(host, protocol, headers, refers=""):
    new_header = headers.copy()
    new_header["Host"] = host
    # new_header["Origin"] = protocol + "://" + host
    url = protocol + "://" + host
    if len(refers) == 0:
        new_header["Referer"] = url
    else:
        new_header["Referer"] = refers
    return new_header


def parseHtml(html_doc):
    return BeautifulSoup(html_doc, 'html.parser')


def parse(content, reg):
    pattern = re.compile(reg, re.DOTALL)
    return pattern.findall(content)


def xbmc_play(url, title):
    listitem = xbmcgui.ListItem(title, path=url)
    xbmc.Player().play(url, listitem)


def get_html(url, header=None, *args):
    print("request url:", url)
    req = request.Request(url)
    if header:
        req.headers = header

    r = request.urlopen(req)
    soup = parseHtml(r.read())
    if len(args) > 0:
        soup = soup.find(*args)

    return str(soup)


def filtCategories(htmlText):
    print("html:", htmlText)
    return htmlText


def getCategories(url):
    htmlText = get_html(url)
    categories = filtCategories(htmlText)

    return categories


def getVideosUrl(category):
    return None


def getUserDataPath():
    # "special://masterprofile/playercorefactory.xml"
    return xbmcvfs.translatePath("special://masterprofile")


def createDefaultPlayer():
    path = getUserDataPath()
    print(path)
    # xbmcvfs.copy("playercorefactory.xml",)
    # xbmcvfs.validatePath("special://masterprofile/playercorefactory.xml")


# response = get_html("https://www.olevod.com/index.php/vod/detail/id/33351.html", None, "div", "playlist_full")
# print(response)
# reg = r'<li><a class="\d*" href=".*?" onclick="clixx\(this\);" target="_blank">.*?<\/a><\/li>'
# pattern = re.compile(reg)
# result = pattern.findall(response)
# print(result)
# url = result[0].replace("\/", "/")
createDefaultPlayer()
