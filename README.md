Gets a random Wiki article, formats it, and sends it off as a tweet two times an hour

Usage: python3 wikitedium.py [--notweet|--manual]

Flags:

       --notweet:  Get and format a Wiki article without sending it to twitter
       --manual :  Bypass the schedule restrictions, just sending one tweet immediately

Note that the "XXXXX"s in "accToken", "apiKey", etc. need to be replaced with tokens obtained by creating an app on app.twitter.com, linking to an account, and setting perms to read/write (which also involves linking a phone number).  The program must also be able to download image files to the local directory.
