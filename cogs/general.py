import discord
from discord.ui import Button,View
from discord.ext import commands
from discord.commands import Option
import re
import json

guild_list=None

class GeneralCommands(commands.Cog,name="一般的なコマンド"):

    def __init__(self,bot):
        self.bot = bot
        with open("guild_list.json", 'r') as f:
            guild_list=json.load(f)

    def strEmoji(self,emoji, i):
        return "<:"+emoji[i].name+":"+str(emoji[i].id)+">"

    @commands.slash_command(guild_ids=guild_list,description="Botがチャット欄で鳴きます")
    async def neko(self,ctx):
        await ctx.respond("にゃーん")

    @commands.slash_command(guild_ids=guild_list,description="簡単な四則演算をしてくれます。")
    async def calc(self,ctx,formula: Option(str, '数式を入力してください')):
        try:
            f=re.sub('[a-zA-Z]','',formula)
            result=str(eval(f,{'__builtins__': {}}))
            replacelist={'*':'\*','_':'\_','~':'\~','|':'\|','`':'\`'}
            for k,v in replacelist.items():
                formula=formula.replace(k,v)
            await ctx.respond(formula+"=**"+result+"**")
        except Exception:
            await ctx.respond("計算できませんでした・・・")

    @commands.slash_command(guild_ids=guild_list,description="へぇボタンです")
    async def reac(self,ctx):

        button = Button(label="へぇ",style=discord.ButtonStyle.secondary,emoji="✋")

        async def button_callback(interaction):
            message = interaction.message
            count = int(message.embeds[0].fields[0].value)+1
            embed = discord.Embed(title="うなずきボタン")
            embed.add_field(name="へぇ",value=str(count))
            await  message.edit(embed=embed)

        button.callback=button_callback

        view = View()
        view.add_item(button)

        embed = discord.Embed(title="うなずきボタン")
        embed.add_field(name="へぇ",value=str(0))
        await ctx.respond(embed=embed,view=view)

    @commands.command(hidden=True)
    async def leave(self,ctx,arg):
        if (self.bot.is_owner(ctx.author)):
            try:
                await ctx.send(self.bot.get_guild(int(arg)).name+"から抜けました")
                await self.bot.get_guild(int(arg)).leave()
            except AttributeError as e:
                await ctx.send("そのサーバーには参加していません")
        else:
            await ctx.send("権限がありません")

    @commands.command(hidden=True)
    async def glist(self,ctx):
        if (self.bot.is_owner(ctx.author)):
            guild_list="現在所属しているサーバ一覧\n"
            for g in self.bot.guilds:
                guild_list+=g.name+":"+str(g.id)+"\n"
            await ctx.send(guild_list)
        else:
            await ctx.send("権限がありません")

def setup(bot):
    bot.add_cog(GeneralCommands(bot))