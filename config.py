"""Config file for shard data and discord config"""
import json
import os


# Initialize `SHARD_DATA`
SHARD_DATA = [
    """Sample format of payout data:
    {
        "name": "Player's name",
        "emoji": "emoji code", (emoji to appear beside the player's name)
        "swgoh.gg": "<https://swgoh.gg/p/xxxxxx>", (swgoh.gg profile link)
        "payout": "08:00" (payout time in UTC)
    }
    """
]

# Read in the file
with open(os.getenv('SHARD_DATA', 'shard-data.json')) as fp:
    SHARD_DATA = json.load(fp)


# Discord stuff
DISCORD_BASE_URL = 'https://discord.com/api/'
DISCORD_BOT_TOKEN = os.getenv('BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('CHANNEL_ID')

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')
CORS_ALLOWED_METHODS = ['HEAD', 'GET', 'OPTIONS']
CORS_ALLOWED_HEADERS = ['Authorization']

# Basic Auth
AUTH_USERNAME = os.getenv('AUTH_USERNAME')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD')

# Logging
LOG_LEVEL = int(ll) if (ll := os.getenv('LOG_LEVEL')) else 20
