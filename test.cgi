#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import cgi
import cgitb
import oauth2 as oauth
import sqlite3
import twitter
cgitb.enable()

request_token_url = 'http://twitter.com/oauth/request_token'
access_token_url = 'http://twitter.com/oauth/access_token'

consumer_key = '**********'
consumer_secret = '**********'

def callback():
    # oauth_token と oauth_verifier を取得
    if 'QUERY_STRING' in os.environ:
        query = cgi.parse_qs(os.environ['QUERY_STRING'])
    else:
        query = {}

    # oauth_token_secret を取得
    con = sqlite3.connect('oauth.db')
    oauth_token_secret = con.execute(
        u'select oauth_token_secret from oauth where oauth_token = ?'
        , [query['oauth_token'][0]]).fetchone()[0]
    con.close()

    # access_token と access_token_secret を取得
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(query['oauth_token'][0], query['oauth_verifier'][0])
    client = oauth.Client(consumer, token)
    resp, content = client.request(access_token_url, "POST", body="oauth_verifier=%s" % query['oauth_verifier'][0])
    access_token = dict(parse_qsl(content))

    return access_token['oauth_token'], access_token['oauth_token_secret']

def client(access_token, access_token_secret):
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret,
                      cache=None)
    TL = api.GetFriendsTimeline()
    for tweet in TL:
        print tweet.text.encode('utf-8')
        print '<br>'

def parse_qsl(url):
    param = {}
    for i in url.split('&'):
        _p = i.split('=')
        param.update({_p[0]: _p[1]})
    return param

if __name__ == '__main__':
    print 'Content-type: text/html; charset: utf-8'
    print
    access_token, access_token_secret = callback()
    client(access_token, access_token_secret)
