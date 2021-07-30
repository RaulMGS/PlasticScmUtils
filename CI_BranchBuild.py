import os
import re
import sys
import subprocess
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed

# Script setup
WEBHOOK_URL = 'WEBHOOK_URL'

# Embed content formats
EMBED_TITLE_FORMAT = 'Northern Lights automatic build started'
EMBED_ICON_URL = 'https://i.imgur.com/koyPU5S.png'
EMBED_DESCRIPTION_FORMAT = '{user} started a new Unity Build'

# Build Utils
BUILD_TARGET_BRANCH = 'main/staging'
BUILD_UNITY_PATH = 'D:/Work/Unity Installs/2019.4.26f1/Editor'
BUILD_WORKSPACE_PATH = 'D:/Work/Unity Projects/Northern Lights/'
BUILD_RESULT_PATH = 'D:/Work/Unity Builds/NorthernLights-Release/Northern Lights'

#-Implementation----------------------------------
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

def parse_plastic_user(): 
    return os.environ['PLASTIC_USER']

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
    embed_instance.set_color('30f803')
    embed_instance.set_thumbnail(url=EMBED_ICON_URL)
    return embed_instance

# Runtime Utils
def run_webhook(url, embed): 
    webhook_instance = DiscordWebhook(url=url)
    webhook_instance.add_embed(embed) 
    webhook_instance.execute()

def run_build_pipeline():
    os.chdir(BUILD_WORKSPACE_PATH)
    os.system("cm update")
    os.chdir(BUILD_UNITY_PATH)
    os.popen("Unity.exe -quit -batchmode -projectpath \"{inpath}\" -buildWindows64Player \"{outpath}\"".format(
        inpath = BUILD_WORKSPACE_PATH,
        outpath = BUILD_RESULT_PATH
    ))

#-Runtime-----------------------------------------
#-------------------------------------------------

branch, changes = parse_plastic_stdin()
user = parse_plastic_user()

# We only want to continue if we are on the build branch. We don't want to start builds from checkins 
# that are on branches irrelevant to the building procedure
if branch == BUILD_TARGET_BRANCH:
    # Compose embed for webhook message
    embed = get_embed_for(
        EMBED_TITLE_FORMAT, 
        EMBED_DESCRIPTION_FORMAT.format(user=user), 
        changes, 
        branch)

    # Send webhook post to discord announcing that a build has started
    run_webhook(WEBHOOK_URL, embed)

    # Run unity build pipeline
    run_build_pipeline()
