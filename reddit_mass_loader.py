import json
import urllib2
from datetime import datetime
import time
import sys
import socket

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tidder.settings')

from django.utils.timezone import utc
from django.contrib.auth.models import User

from stories.models import Story

STORY_COUNT_MAX = 1000
STORY_COUNT = 0

def main():
	pull_feed("python")
	print "***reddit pull complete***"

def pull_feed(item, after_id=-1):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'}

	if after_id == -1:
		url = "http://www.reddit.com/r/" + item + "/new/.json"
	else:
		url = "http://www.reddit.com/r/" + item + "/new/.json" + "?count=25&after=" + after_id

	try:
		req = urllib2.Request(url, headers=headers)
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

	if STORY_COUNT >= STORY_COUNT_MAX:
		sys.exit()

	time.sleep(2)

	pull_feed(item, after_id=after_id)	

def save_item(json_item):
	global STORY_COUNT
	# Add the stories to the database
	moderator = User.objects.get(username='john')

	for item in json_item:
		STORY_COUNT += 1
		print item['data']['title'].encode('utf-8')
		print "http://www.reddit.com" + item['data']['permalink'].encode('utf-8')
		print datetime.fromtimestamp(item['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S.000000+00:00'), '\n'

		story = Story(title=item['data']['title'],
			url="http://www.reddit.com" + item['data']['permalink'],
			points=1,
			moderator=moderator)
		story.save()
		story.created_at = datetime.fromtimestamp(item['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S.000000+00:00')
		story.save()

main()