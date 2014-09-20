#!/usr/bin/env python

from cgi import escape
from flup.server.fcgi import WSGIServer
from mpd import MPDClient
from os import chmod
from os.path import basename, splitext
import simplejson as json
from stat import S_IRUSR, S_IWUSR, S_IRGRP, S_IROTH
import tempfile
from youtube_dl import YoutubeDL
from youtube_dl.extractor.youtube import (
    YoutubeIE,
    YoutubeChannelIE,
    YoutubeFavouritesIE,
    YoutubeHistoryIE,
    YoutubePlaylistIE,
    YoutubeRecommendedIE,
    YoutubeSearchDateIE,
    YoutubeSearchIE,
    YoutubeSearchURLIE,
    YoutubeShowIE,
    YoutubeSubscriptionsIE,
    YoutubeTopListIE,
    YoutubeTruncatedURLIE,
    YoutubeUserIE,
    YoutubeWatchLaterIE,
)

# FIXME - mpd config
MPD_HOST = "localhost"
MPD_PLAYLISTS = "/var/lib/mpd/playlists"

ALLOWED_FORMATS = ['171', '140']


def extract_video_info(url):
    '''Extract video info'''

    # FIXME - configurable somehow
    ydl_opts = {
        'quiet': True,
        'formats': '171/140/webm',
        'cachedir': None
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.add_default_info_extractors()
        res = ydl.extract_info(url, download=False)
    return res


def add_stream(stream_info):
    '''Add stream'''

    if stream_info.get('formats'):
        formats = [(f.get('format_id'), f.get('url')) for f in stream_info['formats'] if f.get('format_id') in ALLOWED_FORMATS]
        formats_dict = dict(formats)
        available_formats = formats_dict.keys()
        for allowed_format in ALLOWED_FORMATS:
            if allowed_format in available_formats:
                stream_url = formats_dict[allowed_format]
                break
    else:
        stream_url = stream_info.get('url')

    if stream_url is None:
        #start_response('500 Internal Server Error', [('Content-type', 'application/json')])
        #return [json.dumps({'status': 'error', 'text': "No URL can be found"})]
        return

    title = stream_info.get('title', 'Youtube stream')
    pls_dict = {
        'title': title,
        'url': stream_url
    }

    pls_text = u'''[playlist]
NumberOfEntries=1
File1=%(url)s
Title1=%(title)s
Length1=-1
version=2''' % pls_dict

    with tempfile.NamedTemporaryFile(suffix='.pls', dir=MPD_PLAYLISTS, delete=False) as pls:
        chmod(pls.name, S_IRGRP | S_IROTH | S_IRUSR | S_IWUSR)
        pls.write(encode(pls_text))
        pls.flush()
        pls_name = basename(pls.name)
        mpdc = MPDClient()
        mpdc.connect(MPD_HOST, 6600)
        mpdc.load(pls_name)
        mpdc.close()


    return [json.dumps({'status': 'success', 'text': pls_text})]


def encode(s):
    if isinstance(s, bytes):
        return s  # Already encoded
    return s.encode('utf-8')


def app(environ, start_response):
    '''Application'''

    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [('Content-type', 'application/json')])
        return ''

    try:
        req = json.load(environ['wsgi.input'])
    except Exception as e:
        start_response('400 Bad Request', [('Content-type', 'application/json')])
        return [json.dumps({'status': 'error', 'text': e.message})]
    url = req.get('url', None)
    if url is None:
        start_response('400 Bad Request', [('Content-type', 'application/json')])
        return [json.dumps({'status': 'error', 'text': "Missing 'url' parameter"})]

    res = extract_video_info(url)

    entries = res.get('entries')
    if entries is not None:
        for entry in entries:
            ret = add_stream(entry)
    else:
        ret = add_stream(res)
    start_response('200 OK', [('Content-type', 'application/json')])
    return [json.dumps({'status': 'success', 'text': 'Successfully added'})]


if __name__ == '__main__':
    # FIXME - configurable socket
    WSGIServer(app, bindAddress=("localhost", 8888)).run()
