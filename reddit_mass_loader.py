import json
import urllib2
from datetime import datetime
import time
import sys
import socket

def main():
	pull_feed("python")
	print "***reddit pull complete***"

def pull_feed(item, after_id=-1):
	hdr = {'User-Agent': 'bot by /u/awsomntbiker'}

	if after_id == -1:
		url = "http://www.reddit.com/r/" + item + "/new/.json"
	else:
		url = "http://www.reddit.com/r/" + item + "/new/.json" + "?count=25&after=" + after_id

	try:
		req = urllib2.Request(url, headers=hdr)
		reddit_page = urllib2.urlopen(req)
		if reddit_page.getcode() == 200:
			status = False

		if reddit_page.getcode() == 504:
			status = True

	except Exception as inst:
		print inst

	# parse the json into python objects
	parsed = json.loads(reddit_page.read())
	after_id = parsed['data']['after']
		
	save_item(parsed['data']['children'])

	#time.sleep(2)

	#pull_feed(item, after_id=after_id)	

def save_item(json_item):
	for item in json_item:
		print item['data']['title'].encode('utf-8')
		print item['data']['permalink'].encode('utf-8')
		print datetime.fromtimestamp(item['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S')

main()