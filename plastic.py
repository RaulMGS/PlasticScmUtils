import sys
import os
import datetime
from discord_webhook import DiscordWebhook

# Script Setup
WEBHOOK_URL = 'YOUR_WEBHOOK_URL'
WEBHOOK_KEEP_FILES = False

# Checkin formats
checkinStr = '**{} checked in a new changeset** \n{} files have changed \n\n**Comments:**\n{}'
checkinLongStr = '@everyone **{} checked in a new changeset** \n{} files have changed \n\n**For comments check file (more than 200 characters):**'

# get change count
change_count = 0
for line in sys.stdin:
	change_count = change_count + 1
	
# get formatted time
now = datetime.datetime.now()
timestr = now.strftime("%Y_%m_%d_%H_%M_%S")

# get webhook string message
webhook_content = checkinStr.format(os.environ['PLASTIC_USER'], change_count, os.environ['PLASTIC_COMMENT'])
if len(os.environ['PLASTIC_COMMENT']) > 1500:
	webhook_content = checkinLongStr.format(os.environ['PLASTIC_USER'] ,change_count)
 
# create webhook
webhook = DiscordWebhook(url=WEBHOOK_URL, content = webhook_content )

# add file to webhook if char limit reached
if len(os.environ['PLASTIC_COMMENT']) > 1500:
	
	# write to file. 
	path = "{}_{}.txt".format(timestr, os.environ['PLASTIC_USER'])
	file = open(path, "w") 
	file.write(checkinStr.format(os.environ['PLASTIC_USER'] ,change_count, os.environ['PLASTIC_COMMENT'])) 
	file.close()

	# Load file to webhook
	with open(path, "rb") as f:
		webhook.add_file(file=f.read(), filename=path)

	# remove file when done
	if os.path.exists(path) and (not WEBHOOK_KEEP_FILES):
		os.remove(path)

# post webhook
webhook.execute()