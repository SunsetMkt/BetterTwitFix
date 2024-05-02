import os

import twitfix,twExtract
import cache
from flask.testing import FlaskClient
from vx_testdata import *
client = FlaskClient(twitfix.app)

def test_embed_qrtTweet():
    cache.clearCache()
    # this is an incredibly lazy test, todo: improve it in the future
    resp = client.get(testQRTTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    assert testQRTTweet_compare['text'][:10] in str(resp.data)
    # test qrt-ception
    resp = client.get(testQrtCeptionTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"}) # get top level tweet
    assert resp.status_code==200
    assert "Please retweet this to spread awareness for retweets" in str(resp.data)
    qtd_tweet=cache.getVnfFromLinkCache("https://twitter.com/EliLanger/status/585253161260216320") # check that the quoted tweet for the top level tweet is cached
    assert qtd_tweet is not None
    assert qtd_tweet["qrtURL"] is not None # check that the quoted tweet for the top level tweet has a qrtURL
    assert cache.getVnfFromLinkCache("https://twitter.com/EliLanger/status/313143446842007553") is None # check that the bottom level tweet has NOT been cached
    resp = client.get("/EliLanger/status/585253161260216320",headers={"User-Agent":"test"}) # get mid level tweet
    assert resp.status_code==200
    assert cache.getVnfFromLinkCache("https://twitter.com/EliLanger/status/313143446842007553") is not None # check that the bottom level tweet has been cached now

def test_embed_qrtVideoTweet():
    cache.clearCache()
    # this is an incredibly lazy test, todo: improve it in the future
    resp = client.get(testQrtVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    qtd_tweet=cache.getVnfFromLinkCache("https://twitter.com/i/status/1674197531301904388")
    vurl = qtd_tweet["mediaURLs"][0]
    assert f"twitter:player:stream\" content=\"{vurl}" in str(resp.data)

def test_embed_FromScratch():
    cache.clearCache()
    client.get(testTextTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    client.get(testMultiMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})

def test_embed_FromCache():
    cache.clearCache()
    twitfix.getTweetData(testTextTweet)
    twitfix.getTweetData(testVideoTweet)
    twitfix.getTweetData(testMediaTweet)
    twitfix.getTweetData(testMultiMediaTweet)
    #embed time
    resp = client.get(testTextTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testVideoTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    resp = client.get(testMultiMediaTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200

def test_embed_Suggestive():
    resp = client.get(testNSFWTweet.replace("https://twitter.com",""),headers={"User-Agent":"test"})
    assert resp.status_code==200
    assert "so i had a bot generate it for me" in str(resp.data)
    assert "FfF_gKwXgAIpnpD" in str(resp.data)

def test_embed_direct():
    resp = client.get(testVideoTweet.replace("https://twitter.com","")+".mp4",headers={"User-Agent":"test"})
    assert resp.status_code==200
    assert testVideoTweet_compare["mediaURLs"][0] in str(resp.data)

def test_embed_message404():
    resp = client.get("https://twitter.com/jack/status/12345",headers={"User-Agent":"test"})
    assert resp.status_code==200
    assert "Failed to scan your link!" in str(resp.data)

def test_combine():
    twt = twitfix.getTweetData(testMultiMediaTweet)
    img1 = twt["mediaURLs"][0]
    img2 = twt["mediaURLs"][1]
    resp = client.get(f"/rendercombined.jpg?imgs={img1},{img2}",headers={"User-Agent":"test"})
    assert resp.status_code==200
    assert resp.headers["Content-Type"]=="image/jpeg"
    assert len(resp.data)>1000