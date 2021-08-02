import os
import sys
import datetime
import re
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed  

# Script setup
WEBHOOK_URL = 'WEBHOOK_URL'
WEBHOOK_KEEP_FILES = False 

# Embed content formats
EMBED_TITLE_FORMAT = 'New check-in in {branch}'
EMBED_ICON_URL = 'https://i.imgur.com/koyPU5S.png'
EMBED_DESCRIPTION_FORMAT = '{user} checked in a new changeset \n\n**Comments:**\n{comment}'
EMBED_DESCRIPTIONLONG_FORMAT = '{user} checked in a new changeset \n\n**For comments check file (more than 200 characters)**'

#-Implementation---------------------------------
#-------------------------------------------------

# Data parsing
def parse_plastic_stdin():
    change_branch = '' 
    change_count = 0
    for line in sys.stdin:
        change_count = change_count + 1
        if not change_branch:
            change_branch = re.search(r"\#br:(.+?)\;", line).group()
            change_branch = change_branch.replace("#br:/", "").replace(";", "")
            
    return change_branch, change_count    

def parse_plastic_envvars():
    embed_contents = EMBED_DESCRIPTION_FORMAT.format(user=os.environ['PLASTIC_USER'], comment=os.environ['PLASTIC_COMMENT'])
    if len(os.environ['PLASTIC_COMMENT']) > 1500:
        embed_contents = EMBED_DESCRIPTIONLONG_FORMAT.format(user=os.environ['PLASTIC_USER'])
    return embed_contents

def parse_datetime():
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def parse_plastic_tags():
    comment = os.environ['PLASTIC_COMMENT']
    tag_matches = re.findall(r"\[\#([0-9]+?)\]", comment)
    return tag_matches

# File logging
def mk_logfile(path): 
    file = open(path, "w")
    file.write(EMBED_DESCRIPTION_FORMAT.format(
        os.environ['PLASTIC_USER'],  
        os.environ['PLASTIC_COMMENT']))
    file.close()

def rm_logfile(path):
    # remove file when done
    if os.path.exists(path) and (not WEBHOOK_KEEP_FILES):
        os.remove(path)

# Discord API wrappers
def get_embed_for(title, contents, change_count, change_branch):
    if not title:
        title = 'MISSING_TITLE'
    if not contents:
        contents = 'MISSING_CONTENTS'
    if not change_branch:
        change_branch = 'MISSING_BRANCH'

    embed_instance = DiscordEmbed(
        title=title,
        description=contents)
    embed_instance.add_embed_field(name='Files Changed', value=change_count)
    embed_instance.add_embed_field(name='Branch', value=change_branch)
    embed_instance.set_timestamp()
    embed_instance.set_color('03b2f8')
    embed_instance.set_thumbnail(url = EMBED_ICON_URL)
    return embed_instance


def post_webhook(url, embed):
    # construct webhook message
    webhook_instance = DiscordWebhook(url=url)
    webhook_instance.add_embed(embed)

    # add file to webhook if char limit reached
    if len(os.environ['PLASTIC_COMMENT']) > 1500:
        # Get path for file
        path = "{}_{}.txt".format(parse_datetime(), os.environ['PLASTIC_USER'])

        # Create log file from checkins
        mk_logfile(path)

        # Load file to webhook
        with open(path, "rb") as f:
            webhook_instance.add_file(file=f.read(), filename=path)

        # Remove log file
        rm_logfile(path)

    # post webhook
    webhook_instance.execute()

#-Runtime-----------------------------------------
#-------------------------------------------------

# get vars for embed
branch, changes = parse_plastic_stdin()
title = EMBED_TITLE_FORMAT.format(branch=branch)
comments = parse_plastic_envvars()
timestamp = parse_datetime()

issues = parse_plastic_tags()
# TODO: Parse tags and pass to github api

# get embed and execute webhook
embed = get_embed_for(title, comments, changes, branch)
post_webhook(WEBHOOK_URL, embed)
