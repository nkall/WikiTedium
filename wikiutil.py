AGENT = "WikiTedium 2.0.  Contact me at og_ivan_drago@hotmail.com"

RAND_WIKI_URL = ("http://en.wikipedia.org/w/api.php?action=query&generator=random" +
                 "&grnnamespace=0&prop=extracts|categories|images&exchars=700" +
                 "&format=json")
IMG_CHQ_URL = ("https://en.wikipedia.org/w/api.php?action=query&list=imageusage" +
               "&iulimit=15&iufilterredir=nonredirects&format=json&iutitle=")
IMG_GET_URL = ("http://en.wikipedia.org/w/api.php?action=query&prop=imageinfo" +
               "|categories&iiprop=url|size&format=json&titles=")


# Various terms banned from title, category, and image name because they were deemed
# boring/irrelevant.  These would probably be more sensible in a seperate file read
# in by the program.
INVALID_TITLES = ["List ", " season", "History of ", "Geography of ", "Politics of ",
		 "Cinema of ", "Athletics at ", " – Singles", " – Doubles",
		 " – Men's ", " – Women's ", "Economy of "]
INVALID_CATS = ["isambiguation", " stubs", "List of", " lists", "ootball", "ugby",
	       "Surname", "Villages", "Sport", "thletes", "Outlines", "ockey",
	       "unclear notability", "promotional tone", "onstituencies", "abinets",
	       "discographies", "filmographies", " skaters", "Challenger Tour",
	       "Set indices on", "Populated places in", "runners", "bibliographies",
	       "electorates", " bishop", "occer", "Towns in ", " episodes",
	       "Townships in ", " sport", " elections", " cricketers", "boxers",
	       "Nations at the ",  " timelines", "Districts of ", " counties",
	       "Golf in ", " players", "basketball", " sprinters", " swimmers",
	       "Boroughs in ", "State Senators", "Formula One races", "WTA Tour",
	       "County officials in ", " electoral districts", " in athletics",
	       "Cup of Nations", "aseball", " tennis", "Davis Cup",  "Days of the",
	       "Bus routes in ", "Revenue blocks of ", "eightlifting at ", " albums",
	       "chool districts", "Bilateral relations of ", "Medical databases",
	       "State highways in ", " seasons", "Championship", "ompanies of India",
	       "tate legislators", " hurlers", "Swimming at the ", "NPOV disputes",
	       "Wrestling at ", "Diving at ", "Qualification for ", " statistics",
	       "Search engine optimization", " executives", "peacock terms",
	       "possible conflicts of interest", " wrestling", " Women's Circuit",
	       " House of Representatives", " legislative sessions", " resolutions",
	       "ubdivisions of ", "Tehsils of ", "Taluk", "ensus-designated places ",
	       " bandy", "econdary schools", "middle schools", " municipalities",
	       " eclipses", "Unincorporated communities ", "igh schools",
	       "Congressional districts of ", " Games", "City Council members",
	       "Area Codes in "]
INVALID_IMGS = ["Icon", "icon", "Logo", "logo", "Ambox", "Login_Manager"]

# Strings invalid for sentence ends
INVALID_ENDS = ["Dr", "Mr", "etc", "Co", "St", "Inc", "Mt", "com", "ca", "Gen", "Sgt",
		"Col"]

# Various words which begin the page definition
BEGIN_WORDS = [" is ", "was ", " are ", " were ", " describes ", " relates to ",
              " pertains to ", " means ", " refers to ", " occured ", " forms ",
	      " served as ", " is concerned with ", " has been ", " comprises ",
	      " states that ", " displays ", " can refer to ", " consists of "]

#
# Removes everything in a string between the start and end strings
#
def removeBetween(string, start, end):
	if end not in string[string.find(start):]:
		bracketed = string[string.find(start):]
	else:
		bracketed = string[string.find(start):string.find(end)+len(end)]
	return string.replace(bracketed, "")
	
#
#  Applies many formatting operations to string: remove parentheticals, headers,
#  extra spaces/punctuation marks, newlines, etc.
#
def unbracket (string):
	idleCount = 0
	while (True):
		idleCount += 1
		if (idleCount > 500):
			return "fail"

		if "(" in string:
			string = removeBetween(string, "(", ")")
		elif "[" in string:
			string = removeBetween(string, "[", "]")
		elif "<h2>" in string:
			string = removeBetween(string, "<h2>", "</h2>")
		elif "<h3>" in string:
			string = removeBetween(string, "<h3>", "</h3>")
		elif "<li>" in string:
			string = removeBetween(string, "<li>", "</li>")
		elif "<ul>" in string:
			string = removeBetween(string, "<ul>", "</ul>")
		elif "<dd>" in string:
			string = removeBetween(string, "<dd>", "</dd>")
		elif "<" in string:
			string = removeBetween(string, "<", ">")
		elif "\n" in string:
			string = string.replace("\n", " ")
		elif "  " in string:
			string = string.replace("  ", " ")
		elif " ." in string:
			string = string.replace(" .", ".")
		elif ".." in string:
			string = string.replace("..", ".")
		elif " ," in string:
			string = string.replace(" ,", ",")
		elif "&amp;" in string:
			string = string.replace("&amp;", "&")
		elif "&#160;" in string:
			string = string.replace("&#160;", " ")
		elif "&lt;" in string:
			string = string.replace("&lt;", "<")
		elif "&gt;" in string:
			string = string.replace("&gt;", ">")
		else:
			return string

#
#  Find index of last period in string that indicates a sentence end rather
#  that an initial or abbreviation
#
def findSentenceEnd (string):
	string = string[:string.rfind(". ") + 1]
	if (len(string) == 0):
		return -1

	if string[len(string)-3] is " " or string[len(string)-3] is ".":
		return findSentenceEnd(string[:len(string)-1])
	for end in INVALID_ENDS:
		if (string.endswith(end + ".")):
			return findSentenceEnd(string[:len(string)-1])
	return len(string)

#
# Shorten string until appropriate length for a tweet 
#
def blurbify (string):
	while (True):
		if (len(string) < 85):		# Too short == not interesting
			return "fail"
		elif (len(string) > 141):	# Delete sentences if over limit
			string = string[:len(string) - 1]
			newEnd = findSentenceEnd(string)
			if (newEnd == -1):
				return "fail"
			string = string[:newEnd]
		elif (len(string) == 141):	# Truncate period if one over
			string = string[:len(string) - 1]
		else:
			# Too many commas indicate list of occupations, e.g.
			# "businessman, singer, actor," etc.  Boring.
			if (string.count(",") > 3):
				print("Rejected blurb: '" + string +
				      "' (too many commas).")
				return "fail"

			return string
