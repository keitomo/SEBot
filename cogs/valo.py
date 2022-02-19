from typing_extensions import Required
import discord
from discord.ext import commands
from discord.commands import Option,SlashCommandGroup
from discord.ui import Button,View
import random
import json

guild_list=None


class ValoCog(commands.Cog,name="Valorant"):
    valo_list = {"null": -1}
    def __init__(self,bot):
        self.bot = bot
        with open("guild_list.json", 'r') as f:
            guild_list=json.load(f)

    valo = SlashCommandGroup("valo", "valorantに関連するコマンド",guild_ids=guild_list)

    def GetValoList(self,ctx):
        server_id = ctx.guild.id
        try:
            valoplayer = ValoCog.valo_list[str(server_id)]
        except KeyError:
            ValoCog.valo_list[str(server_id)] = []
            valoplayer = ValoCog.valo_list[str(server_id)]
        return valoplayer

    def valorand(self,ctx):
        valoplayer = ValoCog.GetValoList(self,ctx)
        map_list=["アセント","バインド","スプリット","ヘイブン","アイスボックス","ブリーズ","フラクチャー"]
        maps=random.sample(map_list, len(map_list))
        valolist = random.sample(valoplayer, len(valoplayer))
        attackers = "None"
        defenders = "None"
        for i in range(len(valolist)):
            if i % 2 == 0:
                if attackers == "None":
                    attackers = valolist[i].display_name+"\n"
                else:
                    attackers += valolist[i].display_name+"\n"
            elif i % 2 == 1:
                if defenders == "None":
                    defenders = valolist[i].display_name+"\n"
                else:
                    defenders += valolist[i].display_name+"\n"
        embed = discord.Embed(title="VALORANTチーム分け", description="Victory 目指して頑張ってください！")
        embed.add_field(name="Maps", value=maps[0], inline=False)
        embed.add_field(name="Attackers", value=attackers, inline=True)
        embed.add_field(name="Defenders", value=defenders, inline=True)
        return embed


    @valo.command(name="valo_set",description="現在ボイスチャンネルに接続しているメンバーをリストに追加します",guild_ids=guild_list)
    async def set(self,ctx):
        valoplayer = ValoCog.GetValoList(self,ctx)
        vl = ctx.author.voice.channel.members
        valoplayer.clear()
        for i in range(len(vl)):
            if vl[i].bot == False:
                valoplayer.append(vl[i])
        member = "None"
        for i in range(len(valoplayer)):
            if member == "None":
                member = valoplayer[i].mention+"\n"
            else:
                member += valoplayer[i].mention+"\n"
        embed = discord.Embed(
            title="valorantメンバー一覧", description="以下のメンバーがセットされました！")
        embed.add_field(name="参加人数",value=str(len(valoplayer))+"人",inline=False)
        embed.add_field(name="Members", value=member, inline=True)
        await ctx.respond(embed=embed)

    @valo.command(name="valo_list",description="現在リストに追加されているメンバーを表示します",guild_ids=guild_list)
    async def list(self,ctx):
        valoplayer = ValoCog.GetValoList(self,ctx)
        member = "None"
        for i in range(len(valoplayer)):
            if member == "None":
                member = valoplayer[i].mention+"\n"
            else:
                member += valoplayer[i].mention+"\n"
        embed = discord.Embed(title="valorantメンバー一覧", description="現在設定されているメンバーです！")
        embed.add_field(name="参加人数",value=str(len(valoplayer))+"人",inline=False)
        embed.add_field(name="Members", value=member, inline=False)
        await ctx.respond(embed=embed)

    @valo.command(name="valo_add",description="プレイヤーをリストに追加します",guild_ids=guild_list)
    async def add(self,ctx,player:Option(discord.Member,"追加するプレイヤーを選択してください")):
        valoplayer = ValoCog.GetValoList(self,ctx)
        if not(player in valoplayer):
            valoplayer.append(player)
            await ctx.respond(player.mention+"がリストに追加されました！")
        else:
            await ctx.respond(player.mention+"は既にリストに追加されています！")

    @valo.command(name="valo_rm",description="プレイヤーをリストから削除します",guild_ids=guild_list)
    async def rm(self,ctx,player:Option(discord.Member,"削除するプレイヤーを選択してください")):
        valoplayer = ValoCog.GetValoList(self,ctx)
        try:
            valoplayer.remove(player)
        except ValueError:
            await ctx.respond("そのプレイヤーはリストに存在しません")
            return
        await ctx.respond(player.mention+"がリストから削除されました！")

    @valo.command(name="valo_reset",description="プレイヤーリストをリセットします",guild_ids=guild_list)
    async def reset(self,ctx):
        valoplayer = ValoCog.GetValoList(self,ctx)
        valoplayer.clear()
        await ctx.respond("プレイヤーリストを削除しました！")

    @valo.command(name="valo_rand",description="プレイヤーをランダムにチーム分けします",guild_ids=guild_list)
    async def rand(self,ctx):
        button = Button(label="再振り分け",style=discord.ButtonStyle.secondary,emoji="🔄")

        async def button_callback(interaction):
            message = interaction.message
            embed = self.valorand(ctx)
            await  message.edit(embed=embed)

        button.callback=button_callback

        view = View()
        view.add_item(button)

        embed = self.valorand(ctx)
        await ctx.respond(embed=embed,view=view)


def setup(bot):
    bot.add_cog(ValoCog(bot))

