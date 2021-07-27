import os
import datetime
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed

# Script Setup
WEBHOOK_URL = 'WEBHOOK_URL'
WEBHOOK_KEEP_FILES = False

# Checkin formats
EMBED_TITLE_FORMAT = 'New commit in {branch}'
EMBED_ICON_URL = ''
EMBED_DESCRIPTION_FORMAT = '**{user} checked in a new changeset** \n\n**Comments:**\n{comment}'
EMBED_DESCRIPTIONLONG_FORMAT = '**{user} checked in a new changeset** \n\n**For comments check file (more than 200 characters):**'

# get change count
change_count = 0
for line in sys.stdin:
	change_count = change_count + 1

# TODO: Fetch branch somehow
change_branch = 'main'

# get formatted time
now = datetime.datetime.now()
timestr = now.strftime("%Y_%m_%d_%H_%M_%S")

# get webhook string message
embed_contents = EMBED_DESCRIPTION_FORMAT.format(user = os.environ['PLASTIC_USER'], comment = os.environ['PLASTIC_COMMENT'])
if len(os.environ['PLASTIC_COMMENT']) > 1500:
	embed_contents = EMBED_DESCRIPTIONLONG_FORMAT.format(user = os.environ['PLASTIC_USER'])
 
# construct embed
embed_instance = DiscordEmbed(
	title=EMBED_TITLE_FORMAT.format(branch = change_branch),
	description = embed_contents)
embed_instance.add_embed_field(name = 'Files Changed', value = change_count)
embed_instance.add_embed_field(name = 'Branch', value = change_branch)
embed_instance.set_timestamp()
embed_instance.set_color('03b2f8')

webhook_instance = DiscordWebhook(url=WEBHOOK_URL)
webhook_instance.add_embed(embed_instance)

# add file to webhook if char limit reached
if len(os.environ['PLASTIC_COMMENT']) > 1500:
	
	# write to file. 
	path = "{}_{}.txt".format(timestr, os.environ['PLASTIC_USER'])
	file = open(path, "w") 
	file.write(EMBED_DESCRIPTION_FORMAT.format(os.environ['PLASTIC_USER'] ,change_count, os.environ['PLASTIC_COMMENT'])) 
	file.close()

	# Load file to webhook
	with open(path, "rb") as f:
		webhook_instance.add_file(file=f.read(), filename=path)

	# remove file when done
	if os.path.exists(path) and (not WEBHOOK_KEEP_FILES):
		os.remove(path)

# post webhook
webhook_instance.execute()
