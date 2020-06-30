"""Module containing all the API's resources"""
import json
import logging

import dateparser
import falcon

from config import (
    DISCORD_BASE_URL,
    DISCORD_BOT_TOKEN,
    DISCORD_CHANNEL_ID as channel_id,
    SHARD_DATA,
    LOG_LEVEL
)
from discord import DiscordAPISession


class PayoutTimerResource(object):
    """Resource that updates the payout countdown on the configured discord
    channel"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _logger = logging.getLogger('PayoutTimerResource')
        _logger.setLevel(LOG_LEVEL)
        _logger.addHandler(logging.StreamHandler())
        self.logger = _logger

    def on_get(self, req, resp):
        # current time
        now = dateparser.parse("now UTC")
        # compute time to each payout
        data = []
        for po in SHARD_DATA:
            payout_time = dateparser.parse(f'today {po["payout"]} UTC')
            delta = payout_time - now
            # Copy the payout data
            row = po.copy()
            row['time_to_payout'] = delta.seconds  # time to payout, in seconds
            data.append(row)
        # sort and format for output
        fields = []
        for po in sorted(data, key=lambda x: x['time_to_payout']):
            hours = po['time_to_payout']//3600  # hours to payout
            minutes = (po['time_to_payout'] % 3600)//60  # minutes to payout
            fields.append({
                'name': f'{hours:02}:{minutes:02} (UTC {po["payout"]})',
                'value': f'{po["emoji"]} [{po["name"]}]({po["swgoh.gg"]})',
                'inline': True
            })
        embed = {
            'description': '**Time until next payout**:',
            'footer': {
                'text': 'Last refresh:',
                'icon_url': 'https://i.imgur.com/OEwutbb.png',
            },
            'thumbnail': {
                'url': 'https://i.imgur.com/OEwutbb.png',
            },
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
        }

        with DiscordAPISession(DISCORD_BASE_URL) as api:
            # First, check for existing messages and delete them
            headers = {'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
                       'Content-Type': 'application/json'}
            messages_resp = api.get(
                f'channels/{channel_id}/messages',
                headers=headers)
            if messages_resp.status_code != 200:
                self.logger.debug(messages_resp.raw)
                resp.status = falcon.HTTP_500
                resp.body = json.dumps(
                    {"error": "Could not get channel messages"})
                return
            messages = messages_resp.json()
            if (msg_count := len(messages)) > 0:
                # First, clear the channel
                if msg_count == 1:
                    # The bulk delete API has a minimum # of message ID's,
                    # so we use a different API to delete just a single message
                    msgid = messages[0]['id']
                    del_resp = api.delete(
                        f'channels/{channel_id}/messages/{msgid}',
                        headers=headers)
                    if del_resp.status_code != 204:
                        self.logger.debug("Error deleting message")
                        self.logger.debug(del_resp.json())
                else:
                    # Use the bulk delete API (max 100 messages per call)
                    while (batch := [msg['id'] for msg in messages[:100]]):
                        self.logger.debug(batch)
                        del_resp = api.post(
                            f'channels/{channel_id}/messages/bulk-delete',
                            headers=headers,
                            json={'messages': batch})
                        if del_resp.status_code != 204:
                            self.logger.debug("Error deleting message")
                            self.logger.debug(del_resp.json())
                        messages = messages[100:]
            # Send new messages
            # The embed object can have at most 25 fields (payouts/players)
            while (batch := fields[:25]):
                embed['fields'] = batch
                send_resp = api.post(
                    f'channels/{channel_id}/messages',
                    headers=headers,
                    json={'embed': embed})
                fields = fields[25:]
                if send_resp.status_code != 200:
                    self.logger.debug(data)
                    self.logger.debug(send_resp.json())
                    resp.status = falcon.HTTP_500
                    resp.body = json.dumps(
                        {"error": "Error creating message"})
                    return

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"status": "OK"})
