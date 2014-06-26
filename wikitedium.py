import time
import sys
import schedule
from wiki import *
from TwitterAPI import TwitterAPI

#
#  Gets a random Wiki article, formats it, and sends it off as a tweet three times an hour
#
#  Usage: python3 wikitedium.py [--notweet/--manual]
#  Flags:
#	--notweet:  Get and format a Wiki article without sending it to twitter
#	--manual :  Bypass the schedule restrictions, just sending one tweet immediately
#



def sendToTwitter(blurb, imgName):
	# These tokens are necessary for twitter contact and must be obtained by creating 
	# an app on app.twitter.com, linking to an account, and setting perms to read/write
	accToken = "XXXXX"
	accTokenSecret = "XXXXX"

	apiKey = "XXXXX"
	apiSecret = "XXXXX"
	
	api = TwitterAPI(apiKey, apiSecret, accToken, accTokenSecret)
	
	if (imgName != "" and imgName != "fail"):
		open_file = open(imgName, "rb")
		r = api.request("statuses/update_with_media",
		               {"status": blurb},
		               {"media[]": open_file.read()})
		if r.status_code is not 200:
			# Try once more, truncating period
			r = api.request("statuses/update_with_media",
			               {"status": blurb[:len(blurb)-1]},
                                       {"media[]": open_file.read()})
			if r.status_code is not 200:
				print("Image tweet failed (status code " + str(r.status_code) +
				      "). Trying tweet without image...")
				r = api.request("statuses/update",
			       	                {"status": blurb})
	else:
		r = api.request("statuses/update",
		                {"status": blurb})
	return r.status_code


def makeTweet():
	fail_count = 0
	while (True):
		print("\nGenerating blurb...")
		blurb, images = getFromWiki()
		imgName = ""
		for image in images:
			imgName = getWikiImage(image)
			if (imgName != "fail"):
				print("Image retrieved.")
				break

		if not SHOULD_TWEET:
			return 0

		sendcode = sendToTwitter(blurb, imgName)
		if sendcode is not 200:
			print('Tweet sending failed (status code ' + str(sendcode) +
			      '). Retrying...')
		else:
			print('Tweeted successfully.')

		if (sendcode is 200) or (fail_count > 2):
			fail_count = 0
			return (sendcode is 200)
		else:
			fail_count += 1


schedule.every().hour.at(':00').do(makeTweet)
schedule.every().hour.at(':20').do(makeTweet)
schedule.every().hour.at(':40').do(makeTweet)

SHOULD_TWEET = True
if (len(sys.argv) == 2):
	if (sys.argv[1] == "--manual"):
        	makeTweet()
	if (sys.argv[1] == "--notweet"):
		SHOULD_TWEET = False
		makeTweet()
else:		
	while True:
		schedule.run_pending()
		time.sleep(1)
