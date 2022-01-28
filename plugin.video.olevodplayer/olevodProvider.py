# -*- coding: utf-8 -*-
import re
from urllib.parse import quote_plus

import xbmc
from xbmc import Keyboard

import utils
from provider import *

CATEGORIES = {"movie": "movie",
              "tv": "tv",
              "variety": "variety",
              "animation": "animation",
              "search": "load_search"}

headers = {"Host": "www.olevod.com",
           "Cache-Control": "nax-age=0",
           "Accept": "application/json, text/plain, */*",
           "Origin": "https://www.olevod.com",
           "X-Requested-With": "XMLHttpRequest",
           "User-Agent": 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
           "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
           "DNT": "1",
           "Referer": "https://www.olevod.com",
           "Accept-Encoding": "",
           "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
           "Connection": "keep-alive"}


class OlevodProvider(Provider):
    def __init__(self):
        Provider.__init__(self)
        self._header = utils.custom_header(headers['Host'], "https", headers, headers['Origin'])
        self._baseUrl = headers['Origin']
        self._name = "olevod"
        if len(self._cookie_string) > 0:
            self._header['Cookie'] = self._cookie_string
        if len(self._user_agent) > 0:
            self._header['User-Agent'] = self._user_agent

    def index(self):
        user_agent = headers["User-Agent"]

        for item, value in CATEGORIES.items():
            listitem = xbmcgui.ListItem(item)
            isFolder = True
            url = self.gen_plugin_url({"act": value,
                                       "name": value,
                                       # 'Cookie': cookie_string,
                                       "User-Agent": user_agent})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, isFolder)
        xbmcplugin.endOfDirectory(self._handle)

    def getMovieList(self, url):
        url = self._baseUrl + url
        print("getMoveList url", url)
        print("header", self._header)
        result = utils.get_html(url)

        # print result
        # reg = r'<a href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)" class=".*?">\n<img.*?data-original="(.*?)".*?alt="(.*?)".*?/>'
        reg = r'<a class=".*?".*?data-original="(.*?)".*?href="([-a-zA-Z0-9@:%_\+.~#?&//=]*?)".*?title="(.*?)">'
        playList = utils.parse(result, reg)
        print("playlist:", playList)
        for i in playList:
            # imageUrl = self._baseUrl + i[0] + "|Cookie=" + self._cookie_string + "&User-Agent=" + self._user_agent
            imageUrl = self._baseUrl + i[0]
            # listitem = xbmcgui.ListItem(i[2], thumbnailImage=imageUrl)
            listitem = xbmcgui.ListItem(i[2])
            listitem.setArt({'thumb': imageUrl,
                             'icon': imageUrl,
                             'fanart': imageUrl})
            url = self.gen_plugin_url({"act": "detail",
                                       "url": i[1],
                                       "title": i[2]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def movie(self):
        self.getMovieList('/index.php/vod/show/id/1.html')

    def tv(self):
        self.getMovieList('/index.php/vod/show/id/2.html')

    def search(self):
        if "keyword" not in self._params:
            kb = Keyboard('', 'Please input Movie or TV Shows name 请输入想要观看的电影或电视剧名称')
            kb.doModal()
            if not kb.isConfirmed():
                return
            sstr = kb.getText()
            if not sstr:
                return
            self.add_search_history(sstr)
        else:
            sstr = self._params["keyword"]
        inputMovieName = quote_plus(sstr)

        xbmc.log('inputMovieName:' + inputMovieName)

        # urlSearch = self._baseUrl + '/index.php?m=vod-search'
        urlSearch = self._baseUrl + '/index.php/vod/search.html?wd=' + inputMovieName
        # data = 'wd=' + inputMovieName
        # req = request.Request(urlSearch, inputMovieName, self._header)
        # searchResponse = self._opener.open(req).read()
        searchResponse = utils.get_html(urlSearch)
        searchReg = r'<h4 class="vodlist_title">.*?<a href="(.*?)".*?><span class="info_right">.*?</span>(.*?)</a>'
        searchResult = utils.parse(searchResponse, searchReg)

        listitem = xbmcgui.ListItem(
            '[COLOR FFFF00FF]Search result 当前搜索: [/COLOR][COLOR FFFFFF00](' + sstr + ') [/COLOR][COLOR FF00FFFF] Total 共计：' + str(
                len(searchResult)) + '[/COLOR]【[COLOR FF00FF00]' + 'Click here for new search 点此输入新搜索内容' + '[/COLOR]】')
        xbmcplugin.addDirectoryItem(self._handle, self.gen_plugin_url({"act": "search"}), listitem, True)
        for i in searchResult:
            listitem = xbmcgui.ListItem(i[1])
            url = self.gen_plugin_url({"act": "detail",
                                       "url": i[0],
                                       "title": i[1]})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, True)
        xbmcplugin.endOfDirectory(self._handle)

    def episodes(self):
        print(self._params)
        url = self._params['url']
        title = self._params['title']
        print(url)
        urlDetail = self._baseUrl + url
        print(urlDetail)
        # req = request.Request(urlDetail, None, self._header)
        # response = self._opener.open(req).read()
        response = utils.get_html(urlDetail)
        # reg = r'<li><a href="(.*?)".*?>(.*?)</a>'
        reg = r'<li><a class="\d*" href="(.*?)" onclick="clixx\(this\);" target="_blank">(.*?)<\/a><\/li>'
        pattern = re.compile(reg)
        result = pattern.findall(response)
        for i in range(len(result)):
            item = result[i]
            print("caption:", item[1])
            print("url:", item[0])
            episodeTitle = title + " " + item[1]
            listitem = xbmcgui.ListItem(episodeTitle)
            listitem.setInfo("video", {"Title": episodeTitle})
            listitem.setProperty("IsPlayable", "true")
            url = self.gen_plugin_url({"act": "play",
                                       "url": item[0],
                                       "title": episodeTitle})
            xbmcplugin.addDirectoryItem(self._handle, url, listitem, False)
        xbmcplugin.endOfDirectory(self._handle)

    def play(self):
        url = self._params['url']
        title = self._params['title']

        urlPlay = self._baseUrl + url
        # req = request.Request(urlPlay, None, self._header)
        # response = str(self._opener.open(req).read())
        print("urlPlay:", urlPlay)
        response = utils.get_html(urlPlay)
        # reg = r'var url=\'(.*?)\'.*?replace\(\'(.*?)\'.*?\'(.*?)\''
        reg = r'player_aaaa=.*?\"url\":\"(.*?)\"'
        pattern = re.compile(reg)
        result = pattern.findall(response)
        print("Play Url not formatted:", result)
        # url = result[0].replace("\/", "/") + "|Origin=https://www.olevod.com&referer=https://www.olevod.com/&accept=*/*"
        url = result[0].replace("\/", "/")

        print("play Url: ", url)
        self.play_url(url, title)
