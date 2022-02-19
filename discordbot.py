import os
import traceback
import discord
from discord.ext import commands

#環境変数読み込み
token = os.environ['SE_BOT_TOKEN']
ownerid = os.environ['OWNER_ID']

INITIAL_EXTENSIONS = [
    'cogs.general',
    'cogs.valo',
    'cogs.se',
    #'cogs.test',
]

class SEBot(commands.Bot):

    def __init__(self, command_prefix,owner_id,intents=discord.Intents.all()):
        super().__init__(command_prefix=command_prefix,owner_id=owner_id,intents=intents)
        self.owner_id=owner_id
        requiredDirectories=["./dict","./guildconf","./input","./SE","./voice","./voiceconf"]
        for rd in requiredDirectories:
            if not os.path.exists(rd):
                os.makedirs(rd)
        if not os.path.exists("guild_list.json"):
            with open("guild_list.json", 'w') as f:
                f.write("[]")

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print("Logged in as " + client.user.name)
        print("-----")
        #await client.change_presence(activity=discord.Activity(name='リニューアル！'))

    def is_owner(self, user):
        return int(user.id)==int(self.owner_id)

if __name__ == '__main__':
    client = SEBot(command_prefix="/",owner_id=ownerid)
    client.run(token)