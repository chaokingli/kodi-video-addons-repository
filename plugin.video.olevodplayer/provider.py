# -*- coding: utf-8 -*-
import base64
import sys
from http import cookiejar
from urllib.parse import urlencode, parse_qsl
from urllib.request import build_opener, HTTPCookieProcessor
from pathlib import PurePath

import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

addon = xbmcaddon.Addon(id='plugin.video.olevodplayer')
rootDir = addon.getAddonInfo('path')
rootDir = xbmcvfs.translatePath(rootDir)
search_file = PurePath(rootDir, "search.txt")


def encode_param(ps, kw):
    if kw in ps:
        ps[kw] = base64.urlsafe_b64encode(ps[kw])


def decode_param(ps, kw):
    if kw in ps:
        ps[kw] = base64.urlsafe_b64decode(ps[kw])


def decode_params(ps, ks):
    for key in ks:
        decode_param(ps, key)


class Provider():
    def __init__(self):
        self._plugin_url = sys.argv[0]
        self._handle = int(sys.argv[1])
        self._params = dict(parse_qsl(sys.argv[2][1:]))
        self._need_encode_keys = ["url" "title" "keyword"]
        decode_params(self._params, self._need_encode_keys)
        cookie_jar = cookiejar.MozillaCookieJar()
        self._opener = build_opener(HTTPCookieProcessor(cookie_jar))
        self._name = "default provider"
        self._cookie_string = self._params["Cookie"] if "Cookie" in self._params else ""
        self._user_agent = self._params["User-Agent"] if "User-Agent" in self._params else ""
        self._router = {"clear_search_history": self.clear_search_history,
                        "search": self.search,
                        "load_search": self.load_search,
                        "detail": self.episodes,
                        "play": self.play,
                        "list": self.list,
                        'movie': self.movie,
                        "variety": self.variety,
                        "animation": self.animation,
                        'tv': self.tv,
                        "index": self.index}

    def encode_params(self, ps):
        if "User-Agent" not in ps and 'User-Agent' in self._params:
            ps["User-Agent"] = self._params["User-Agent"]
        if "Cookie" not in ps and "Cookie" in self._params:
            ps["Cookie"] = self._params["Cookie"]
        for item in self._need_encode_keys:
            encode_param(ps, item)
        ps["provider"] = self._name
        return urlencode(ps)

    def add_search_history(self, keyword):
        fo = open(search_file, "a+", encoding="utf-8")
        print('search keyword: ' + keyword)
        fo.write(keyword + '\n')
        fo.close

    def load_search_history(self):
        print(search_file)
        try:
            fo = open(search_file, "r", encoding="utf-8")
            kws = fo.readlines()
            fo.close
            return kws
        except:
            return []

    def clear_search_history(self):
        print(search_file)
        fo = open(search_file, "w")
        fo.write("")
        fo.close

    def gen_plugin_url(self, params):
        return self._plugin_url + "?" + self.encode_params(params)

    def list(self, url):
        pass

    def search(self, kw):
        pass

    def movie(self):
        pass

    def tv(self):
        pass

    def variety(self):
        pass

    def animation(self):
        pass

    def new_search(self):
        pass

    def index(self):
        pass

    def play(self):
        pass

    def route(self, act):
        self._router[act]()

    def get_full_url(self, url):
        imageUrl = url
        if not imageUrl.startswith("http"):
            imageUrl = self._baseUrl + imageUrl
        return imageUrl

    def play_url(self, url, title):
        listitem = xbmcgui.ListItem(title, path=url)
        listitem.setProperty('inputstream', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        xbmcplugin.setResolvedUrl(self._handle, succeeded=True, listitem=listitem)

    def page_url(self, id, pageno):
        pass

    def category(self, cates):
        for item in cates:
            listitem = xbmcgui.ListItem(item[0])
            url = self.gen_plugin_url({"act": "list",
                                       "url": self.page_url(item[1], 1)})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def load_search(self):
        listitem = xbmcgui.ListItem("new search")
        url = self.gen_plugin_url({"act": "search"})
        xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)

        kws = self.load_search_history()
        for kw in kws:
            kw = kw.rstrip()
            listitem = xbmcgui.ListItem("search: " + kw)
            url = self.gen_plugin_url({"act": "search",
                                       "keyword": kw})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        if len(kws) > 0:
            listitem = xbmcgui.ListItem("clear search history")
            url = self.gen_plugin_url({"act": "clear_search_history"})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)

    def choose_and_play(self, list, title):
        new_list = [x for x in list if "m3u8" in x or "mp4" in x]
        if len(new_list) == 0:
            new_list = list
        if len(new_list) == 1:
            movie_url = new_list[0]
        else:
            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose a source', new_list)
            movie_url = new_list[ret]
        print(title, movie_url)
        self.play_url(movie_url, title)
