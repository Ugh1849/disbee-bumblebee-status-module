import core.module
import core.widget
import requests
import json
import time
import random


def getmessages(id, token):

    headers = {
        'Authorization': token
    }

    r = requests.get(f'https://discord.com/api/v8/channels/{id}/messages', headers=headers)
    jsonn = json.loads(r.text)
    return jsonn


class Module(core.module.Module):

    def handleInput(self, _):
        self.disable = not self.disable

    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.full_text))

        self.disable = False

        core.input.register(None, button=core.input.LEFT_MOUSE, cmd=self.handleInput)

        self.firstTime = False

        self.token = ""
        self.channelIds = []
        
        self.countdown = 1
        self.channel_last_notif_ids = {}
        self.errorincfg = False
        self.rangeTime = 0

        self.file_path = 'disbee.cfg'

        try:
            with open(self.file_path, 'r') as file:
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
            with open(self.file_path, 'w') as file:
                file.write("# Replace YOUR_TOKEN_HERE with your discord token\n")
                file.write("TOKEN YOUR_TOKEN_HERE\n")
                file.write("COUNTDOWN 5\n")
                file.write("# Add a new line to incicate a new channel id. Example: 15261214836325270 https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-\n")


    def full_text(self, widgets):

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
            jsonstring = str(getmessages(id, self.token))

            if "content" in jsonstring:
                index_id = jsonstring.find("id")
                notif_id = jsonstring[index_id + 4: index_id + 4 + 19]

                if id not in self.channel_last_notif_ids:
                    self.channel_last_notif_ids[id] = notif_id
                else:
                    if notif_id != self.channel_last_notif_ids[id]:
                        result += f"New message!"
                        self.channel_last_notif_ids[id] = notif_id
                        self.rangeTime = self.countdown
            else:
                result += f'Error in channel {id}! {jsonstring}\n'

        if result:
            return result
        else:
            return 'No new messages'