import core.module
import core.widget
import aiohttp
import asyncio
import json
import time
import random


async def getMessages(id, token):
    headers = {
        'Authorization': token
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/api/v8/channels/{id}/messages', headers=headers) as r:
            responseJson = await r.json()
            return responseJson # -- to losers who use snake case ( ͡° ͜ʖ ͡°)


class Module(core.module.Module):

    def handleInput(self, _):
        self.disable = not self.disable

    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.fullText))

        self.disable = False

        core.input.register(None, button=core.input.LEFT_MOUSE, cmd=self.handleInput)

        self.firstTime = False

        self.token = ""
        self.channelIds = []
        
        self.countDown = 1
        self.channelLastNotifIds = {}
        self.errorInCfg = False
        self.rangeTime = 0

        self.filePath = 'disbee.cfg'

        try:
            with open(self.filePath, 'r') as file:
                for line in file:
                    if line.startswith('#'):
                        continue
                    
                    line_content = line.strip()
                    
                    if line.startswith('TOKEN '):
                        self.token = line.strip()[6:]
                        if self.token in 'YOUR_TOKEN_HERE':
                            self.firstTime = True
                    elif line.startswith('COUNTDOWN '):
                        self.countdown = int(line.strip()[10:])
                    else:
                        self.channelIds.append(line_content)
        except FileNotFoundError:
            with open(self.filePath, 'w') as file:
                file.write("# Replace YOUR_TOKEN_HERE with your discord token\n")
                file.write("TOKEN YOUR_TOKEN_HERE\n")
                file.write("COUNTDOWN 5\n")
                file.write("# Add a new line to incicate a new channel id. Example: 15261214836325270 https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-\n")


    async def fullText(self, widgets):

        if self.disable == True:
            return ""

        if self.firstTime:
            return 'Please go to your home directory and edit disbee.cfg'

        if not self.channelIds:
            return "Please add channel ids"

        if self.rangeTime > 0:
            time.sleep(0.35)
            self.rangeTime -= 1
            return f"New message! ({self.rangeTime + 1})"

        result = ""

        for id in self.channelIds:
            messages = await getMessages(id, self.token)
            jsonstring = str(messages)

            if "content" in jsonstring:
                indexId = jsonstring.find("id")
                notifId = jsonstring[indexId + 4: indexId + 4 + 19]

                if id not in self.channeLastNotifIds:
                    self.channeLastNotifIds[id] = notifId
                else:
                    if notifId != self.channeLastNotifIds[id]:
                        result += f"New message!"
                        self.channel_last_notif_ids[id] = notifId
                        self.rangeTime = self.countdown
            else:
                result += f'Error in channel {id}! {jsonstring}\n'

        if result:
            return result
        else:
            return 'No new messages'