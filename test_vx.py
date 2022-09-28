import os
from wsgiref import headers
os.environ["RUNNING_TESTS"]="1"

import twitfix,twExtract
import pytest
import json
import cache
from flask.testing import FlaskClient
client = FlaskClient(twitfix.app)

testTextTweet="https://twitter.com/jack/status/20"
testVideoTweet="https://twitter.com/Twitter/status/1263145271946551300"
testMediaTweet="https://twitter.com/Twitter/status/1118295916874739714"
testMultiMediaTweet="https://twitter.com/Twitter/status/1293239745695211520"

textVNF_compare = {'tweet': 'https://twitter.com/jack/status/20', 'url': '', 'description': 'just setting up my twttr', 'screen_name': 'jack', 'type': 'Text', 'images': ['', '', '', '', ''], 'time': 'Tue Mar 21 20:50:14 +0000 2006', 'qrt': {}, 'nsfw': False}
videoVNF_compare={'tweet': 'https://twitter.com/Twitter/status/1263145271946551300', 'url': 'https://video.twimg.com/amplify_video/1263145212760805376/vid/1280x720/9jous8HM0_duxL0w.mp4?tag=13', 'description': 'Testing, testing...\n\nA new way to have a convo with exactly who you want. We’re starting with a small % globally, so keep your 👀 out to see it in action. https://t.co/pV53mvjAVT', 'thumbnail': 'http://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg', 'screen_name': 'Twitter', 'type': 'Video', 'images': ['', '', '', '', ''], 'time': 'Wed May 20 16:31:15 +0000 2020', 'qrt': {}, 'nsfw': False,'verified': True, 'size': {'width': 1920, 'height': 1080}}
testMedia_compare={'tweet': 'https://twitter.com/Twitter/status/1118295916874739714', 'url': '', 'description': 'On profile pages, we used to only show someone’s replies, not the original Tweet 🙄 Now we’re showing both so you can follow the conversation more easily! https://t.co/LSBEZYFqmY', 'thumbnail': 'https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg', 'screen_name': 'Twitter', 'type': 'Image', 'images': ['https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg', '', '', '', '1'], 'time': 'Tue Apr 16 23:31:38 +0000 2019', 'qrt': {}, 'nsfw': False, 'size': {}}
testMultiMedia_compare={'tweet': 'https://twitter.com/Twitter/status/1293239745695211520', 'url': '', 'description': 'We tested, you Tweeted, and now we’re rolling it out to everyone! https://t.co/w6Q3Q6DiKz', 'thumbnail': 'https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg', 'screen_name': 'Twitter', 'type': 'Image', 'images': ['https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg', 'https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg', '', '', '2'], 'time': 'Tue Aug 11 17:35:57 +0000 2020', 'qrt': {}, 'nsfw': False, 'verified': True, 'size': {}}

def compareDict(original,compare):
    for key in original:
        assert key in compare
        assert compare[key]==original[key]

## Tweet retrieve tests ##
def test_textTweetExtract():
    tweet = twExtract.extractStatus(testTextTweet)
    assert tweet["full_text"]==textVNF_compare['description']
    assert tweet["user"]["screen_name"]=="jack"
    assert 'extended_entities' not in tweet
    assert tweet["is_quote_status"]==False

def test_videoTweetExtract():
    tweet = twExtract.extractStatus(testVideoTweet)
    assert tweet["full_text"]==videoVNF_compare['description']
    assert tweet["user"]["screen_name"]=="Twitter"
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==1
    video = tweet['extended_entities']["media"][0]
    assert video["media_url_https"]=="https://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg"
    assert video["type"]=="video"
    assert tweet["is_quote_status"]==False

def test_mediaTweetExtract():
    tweet = twExtract.extractStatus(testMediaTweet)
    assert tweet["full_text"]==testMedia_compare['description']
    assert tweet["user"]["screen_name"]=="Twitter"
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==1
    video = tweet['extended_entities']["media"][0]
    assert video["media_url_https"]=="https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg"
    assert video["type"]=="photo"
    assert tweet["is_quote_status"]==False

def test_multimediaTweetExtract():
    tweet = twExtract.extractStatus(testMultiMediaTweet)
    assert tweet["full_text"]==testMultiMedia_compare['description']
    assert tweet["user"]["screen_name"]=="Twitter"
    assert 'extended_entities' in tweet
    assert len(tweet['extended_entities']["media"])==2
    video = tweet['extended_entities']["media"][0]
    assert video["media_url_https"]=="https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg"
    assert video["type"]=="photo"
    video = tweet['extended_entities']["media"][1]
    assert video["media_url_https"]=="https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg"
    assert video["type"]=="photo"

## VNF conversion test ##

def test_textTweetVNF():
    vnf = twitfix.link_to_vnf_from_unofficial_api(testTextTweet)
    compareDict(textVNF_compare,vnf)

def test_videoTweetVNF():
    vnf = twitfix.link_to_vnf_from_unofficial_api(testVideoTweet)
    
    compareDict(videoVNF_compare,vnf)

def test_mediaTweetVNF():
    vnf = twitfix.link_to_vnf_from_unofficial_api(testMediaTweet)
    compareDict(testMedia_compare,vnf)

def test_multimediaTweetVNF():
    vnf = twitfix.link_to_vnf_from_unofficial_api(testMultiMediaTweet)
    compareDict(testMultiMedia_compare,vnf)

## Test adding to cache ; cache should be empty ##
def test_addToCache():
    cache.clearCache()
    twitfix.vnfFromCacheOrDL(testTextTweet)
    twitfix.vnfFromCacheOrDL(testVideoTweet)
    twitfix.vnfFromCacheOrDL(testMediaTweet)
    twitfix.vnfFromCacheOrDL(testMultiMediaTweet)
    #retrieve
    compareDict(textVNF_compare,cache.getVnfFromLinkCache(testTextTweet))
    compareDict(videoVNF_compare,cache.getVnfFromLinkCache(testVideoTweet))
    compareDict(testMedia_compare,cache.getVnfFromLinkCache(testMediaTweet))
    compareDict(testMultiMedia_compare,cache.getVnfFromLinkCache(testMultiMediaTweet))
    cache.clearCache()

def test_embedFromScratch():
    cache.clearCache()
    client.get(testTextTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testMultiMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})

def test_embedFromCache():
    cache.clearCache()
    twitfix.vnfFromCacheOrDL(testTextTweet)
    twitfix.vnfFromCacheOrDL(testVideoTweet)
    twitfix.vnfFromCacheOrDL(testMediaTweet)
    twitfix.vnfFromCacheOrDL(testMultiMediaTweet)
    #embed time
    resp = client.get(testTextTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMultiMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200

def test_embedFromOutdatedCache(): # presets a cache that has VNF's with missing fields; there's probably a better way to do this
    cache.setCache({"https://twitter.com/Twitter/status/1118295916874739714":{"description":"On profile pages, we used to only show someone’s replies, not the original Tweet 🙄 Now we’re showing both so you can follow the conversation more easily! https://t.co/LSBEZYFqmY","hits":0,"images":["https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg","","","","1"],"likes":5033,"nsfw":False,"pfp":"http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg","qrt":{},"rts":754,"screen_name":"Twitter","thumbnail":"https://pbs.twimg.com/media/D4TS4xeX4AA02DI.jpg","time":"Tue Apr 16 23:31:38 +0000 2019","tweet":"https://twitter.com/Twitter/status/1118295916874739714","type":"Image","uploader":"Twitter","url":""},"https://twitter.com/Twitter/status/1263145271946551300":{"description":"Testing, testing...\n\nA new way to have a convo with exactly who you want. We’re starting with a small % globally, so keep your 👀 out to see it in action. https://t.co/pV53mvjAVT","hits":0,"images":["","","","",""],"likes":61584,"nsfw":False,"pfp":"http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg","qrt":{},"rts":17138,"screen_name":"Twitter","thumbnail":"http://pbs.twimg.com/media/EYeX7akWsAIP1_1.jpg","time":"Wed May 20 16:31:15 +0000 2020","tweet":"https://twitter.com/Twitter/status/1263145271946551300","type":"Video","uploader":"Twitter","url":"https://video.twimg.com/amplify_video/1263145212760805376/vid/1280x720/9jous8HM0_duxL0w.mp4?tag=13"},"https://twitter.com/Twitter/status/1293239745695211520":{"description":"We tested, you Tweeted, and now we’re rolling it out to everyone! https://t.co/w6Q3Q6DiKz","hits":0,"images":["https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg","https://pbs.twimg.com/media/EfJ-aHlU0AAU1kq.jpg","","","2"],"likes":5707,"nsfw":False,"pfp":"http://pbs.twimg.com/profile_images/1488548719062654976/u6qfBBkF_normal.jpg","qrt":{},"rts":1416,"screen_name":"Twitter","thumbnail":"https://pbs.twimg.com/media/EfJ-C-JU0AAQL_C.jpg","time":"Tue Aug 11 17:35:57 +0000 2020","tweet":"https://twitter.com/Twitter/status/1293239745695211520","type":"Image","uploader":"Twitter","url":""},"https://twitter.com/jack/status/20":{"description":"just setting up my twttr","hits":0,"images":["","","","",""],"likes":179863,"nsfw":False,"pfp":"http://pbs.twimg.com/profile_images/1115644092329758721/AFjOr-K8_normal.jpg","qrt":{},"rts":122021,"screen_name":"jack","thumbnail":"","time":"Tue Mar 21 20:50:14 +0000 2006","tweet":"https://twitter.com/jack/status/20","type":"Text","uploader":"jack","url":""}})
    #embed time
    resp = client.get(testTextTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMultiMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200