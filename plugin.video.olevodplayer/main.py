# -*- coding: utf-8 -*-

# using zip -r -0 oversea.zip plugin.video.overseaplayer/ to zip

import sys
from urllib.parse import parse_qsl

import olevodProvider

_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    x = olevodProvider.OlevodProvider()
    if params:
        x.route(params.get("act", "index"))
    else:
        x.index()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
