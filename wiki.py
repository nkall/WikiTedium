import json
import os
import urllib.request
from urllib.parse import quote
from wikiutil import *

#
#  Takes in a Wiki image filename and checks if that image is valid.  If so, it
#  downloads the image into the same directory and returns the name of the saved
#  file.
#
def getWikiImage(name):
	print("Retrieving " + name + "...")
	name = urllib.parse.quote(name)
	request = urllib.request.Request(IMG_GET_URL + name, headers={"User-Agent": AGENT})
	response = urllib.request.urlopen(request).read().decode()
	jsonResponse = json.loads(response)
	
	for entry in jsonResponse['query']['pages']:
		dlUrl = jsonResponse['query']['pages'][entry]['imageinfo'][0]['url']
		# Reject non-free images
		if ((jsonResponse['query']['pages'][entry]).get('categories')):
			cats = jsonResponse['query']['pages'][entry]['categories']
			for cat in cats:
				if "on-free" in cat or "logo" in cat:
					sys.stdout.buffer.write("Rejected image: " + name +
                                                                " (non-free/logo).")
					return "fail"

	imageArea = (jsonResponse['query']['pages'][entry]['imageinfo'][0]['width'] *
	                jsonResponse['query']['pages'][entry]['imageinfo'][0]['height'])
	# Reject images too small to be useful
	if (imageArea < 65000):
		print("Rejected image: " + name + " (image too small).")
		return "fail"
	# Reject image over twitter max file size of 3 MB
	if (jsonResponse['query']['pages'][entry]['imageinfo'][0]['size'] > 3000000):
		print("Rejected image: " + name + " (file too large).")
		return "fail"

	_, ext = os.path.splitext(dlUrl)
	urllib.request.urlretrieve(dlUrl, "in" + ext)
	return ("in" + ext)

#
#  Takes raw title and body string and formats it into one twitter-suitable string.
# 
def makeBlurb (title, body):
	body = body.replace("...", "")
	# Period required to split sentences
	if "." not in body:
		return "fail"

	title = unbracket(title)
	body = unbracket(body)

	if (body == "fail" or title == "fail"):
		return "fail"

	while title.endswith(" "):
		title = title[:len(title)-1]

	title += ": "

        # Skips disambiguation hatnote
	if (body.startswith("This article is about ")):
		body = body[body.find("."):]

	# Delete filler words for colon format
	beginIndex = 500
	for word in BEGIN_WORDS:
		if (word in body) and (body.find(word) < beginIndex):
			beginIndex = body.find(word)
			beginLen = len(word)
	if (beginIndex == 500):
		return "fail"
	blurb = body[beginIndex+beginLen:]
	if (blurb.startswith("a ")):
		blurb = blurb[2:]
	if (blurb.startswith("an ")):
		blurb = blurb[3:]
	if (blurb.startswith("the ")):
		blurb = blurb[4:]

	blurb = title + blurb

	return blurbify(blurb)

#
#  Valid pages must not contain invalid category or title strings
#
def isValidPage (entry):
	for cat in entry['categories']:
		for icat in INVALID_CATS:
			if icat in cat['title']:
				print("Rejected page: " + entry['title'] + " (category '"
				      + cat['title'] + "' matches banned string '" + icat + "')")
				return False
	for invalidTitle in INVALID_TITLES:
		if invalidTitle in entry['title']:
			print("Rejected page: " + entry['title'] + " (title " +
			      " matches banned string '" + invalidTitle + "')")
			return False
	return True

#
#  Keep getting articles until a valid page found 
#
def getArticleRecurr (url):
	request = urllib.request.Request(url, headers={"User-Agent": AGENT})
	response = urllib.request.urlopen(request).read()
	jsonResponse = json.loads(response.decode('utf-8'))
	for pageNum in jsonResponse['query']['pages']:
		mainEntry = jsonResponse['query']['pages'][pageNum]

	if (isValidPage(mainEntry)):
		return mainEntry
	else:
		return getArticleRecurr(url)

#
#  If too many pages link to an image, it is likely generic. Returns True if image has under
#  15 pages linking to it, and False otherwise
#
def isValidImage(img):
	img = urllib.parse.quote(img)
	imgUrl = IMG_CHQ_URL + img
	request = urllib.request.Request(imgUrl, headers={"User-Agent": AGENT})
	response = urllib.request.urlopen(request).read()
	jsonResponse = json.loads(response.decode('utf-8'))
	if (len(jsonResponse['query']['imageusage']) < 15):
		return True
	else:
		return False 

#
#  Generates blurb and list of usable images
#
def getFromWiki():
	resultBlurb = "fail"

	while (resultBlurb == "fail"):
		mainEntry = getArticleRecurr(RAND_WIKI_URL)
		resultBlurb = makeBlurb (mainEntry['title'], mainEntry['extract'])

	print("\n" + mainEntry['extract'])
	print("\n" + resultBlurb + "\n")

	imageList = []
	# Image usually takes about 23 characters -- if no room, don't bother
	if (len(resultBlurb) < 120 and mainEntry.get('images')):
		for img in mainEntry['images']:
			isRightFormat = (img['title'].endswith(".jpg") or img['title'].endswith(".png")
			           or img['title'].endswith(".gif") or img['title'].endswith(".JPG"))
			for iImg in INVALID_IMGS:
				if iImg in img['title']:
					print("Rejected image: " + img['title'].replace(" ", "_") +
						" (matches banned term '" + iImg + "').")
					isRightFormat = False
			if isRightFormat:
				imageList.append(img['title'].replace(" ", "_"))
		for image in imageList:
			if (not isValidImage(image)):
				print("Rejected image: " + image + " (too common).")
				imageList.remove(image)
		print(imageList)
	return (resultBlurb, imageList)
