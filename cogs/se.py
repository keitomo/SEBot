from random import choices
from discord.errors import InvalidArgument
from discord.ext import commands, pages
from pydub import AudioSegment
import discord
from discord.commands import Option,SlashCommandGroup
import asyncio
from voice_generator import creat_WAV
import queue
import os
import json
import pydub
import re

guild_list=None

class SECog(commands.Cog,name="SE-Bot"):
    server_chat = {"null": -1}
    voice_queue = {"null":queue.Queue()}
    user_voice  = {"null":-1}
    lock = False

    def __init__(self,bot):
        self.bot = bot
        with open("guild_list.json", 'r') as f:
            guild_list=json.load(f)

    async def SEplay(self,path,guild):
        vc = guild.voice_client
        SECog.voice_queue[guild].put(path)
        if vc.is_playing():
            return
        while not SECog.voice_queue[guild].empty():
            while SECog.lock:
                pass
            play_path = SECog.voice_queue[guild].get()
            ffmpeg_audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(play_path),volume=0.5)
            sound = AudioSegment.from_file(play_path, "mp3")
            try:
                vc.play(ffmpeg_audio_source)
            except discord.errors.ClientException:
                return
            await asyncio.sleep(sound.duration_seconds+1)
            SECog.lock = True
            if ("voice/" in play_path):
                os.remove(play_path)
            SECog.lock = False

    async def disconnect_server(self,guild):
        vc = guild.voice_client
        while not SECog.voice_queue[guild].empty():
            play_path = SECog.voice_queue[guild].get()
            if ("voice/" in play_path):
                os.remove(play_path)
        del SECog.server_chat[guild]
        await vc.disconnect()

    def get_SEList(self,guildID):
        result=[]
        with open('./SE/'+str(guildID)+"/list.json",'r') as f:
            server_se_list = json.load(f)
        se_list=list(server_se_list.items())
        embed=discord.Embed()
        for i in range(len(se_list)):
            embed.add_field(name=se_list[i][0],value=se_list[i][1],inline=True)
            if (i+1)%24==0 or i+1 == len(se_list) :
                result.append(embed)
                embed=discord.Embed()
        return result

    def get_WORDList(self,guildID):
        result=[]
        with open('./dict/'+str(guildID)+".json",'r') as f:
            server_word_list = json.load(f)
        word_list=list(server_word_list.items())
        embed=discord.Embed(title="単語辞書")
        for i in range(len(word_list)):
            embed.add_field(name=word_list[i][0],value=word_list[i][1],inline=True)
            if (i+1)%24==0 or i+1 == len(word_list) :
                result.append(embed)
                embed=discord.Embed(title="単語辞書")
        return result


    se = SlashCommandGroup("se", "seや読み上げに関連するコマンド",guild_ids=guild_list)

    @se.command(description="SE-Botが通話に参加します",guild_ids=guild_list)
    async def cn(self,ctx):
        guild=ctx.guild
        vc = ctx.guild.voice_client
        if not (vc is None):
            await ctx.respond("SE-Botはすでに通話に参加しています")
            return
        SECog.voice_queue[guild] = queue.Queue()
        try:
            voice_id = ctx.author.voice.channel.id
        except AttributeError:
            await ctx.respond("通話に参加してからコマンドを実行してください")
            return
        """サーバー初期設定関係"""
        server_conf = './guildconf/'+str(guild.id)+'.json'
        if not os.path.exists(server_conf):
            with open(server_conf, 'w') as f:
                    f.write("{}")
            with open(server_conf, 'r') as f:
                server_conf_dict=json.load(f)
            server_conf_dict["name"]=guild.name
            server_conf_dict["join_notifiction"]=True
            with open(server_conf, 'w') as f:
                json.dump(server_conf_dict,f,indent=4,ensure_ascii=False)
        try:
            channel = self.bot.get_channel(voice_id)
        except UnboundLocalError:
            return
        vc = await channel.connect()
        SECog.server_chat[guild] = ctx.channel.id
        await ctx.respond("通話に参加しました")


    @se.command(description="SE-Botが通話から切断します",guild_ids=guild_list)
    async def dc(self,ctx):
        if ctx.guild.voice_client == None :
            await ctx.respond("SE-Botは通話に参加していません")
            return
        await self.disconnect_server(ctx.guild)
        await ctx.respond("通話から切断しました")

    @se.command(description="登録されているSEを表示します",guild_ids=guild_list)
    async def list(self,ctx):
        try:
            await ctx.defer()
            paginator = pages.Paginator(pages=self.get_SEList(ctx.guild.id), show_disabled=False, show_indicator=True,author_check=False)
            paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
            paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
            paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
            paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)
            await paginator.send(ctx, ephemeral=False)
        except Exception:
            await ctx.respond("辞書に登録されていません")

    @se.command(description="サーバーにSEを追加します",guild_ids=guild_list)
    async def add(self,ctx,word:Option(str,description="SEを流す正規表現")):
        attachment = ctx.message.attachments[0]
        if attachment.content_type != "audio/mpeg":
            await ctx.respond("このファイルは登録できません")
            return
        guild=ctx.guild
        server_se_path = './SE/'+str(guild.id)+"/"
        server_se_list = './SE/'+str(guild.id)+"/list.json"
        if not os.path.exists(server_se_list):
            os.makedirs(server_se_path)
            with open(server_se_list, 'w') as f:
                f.write("{}")
        await attachment.save(server_se_path+attachment.filename)
        with open(server_se_list, 'r') as f:
            server_dict=json.load(f)
        server_dict[str(word)]=attachment.filename
        embed = discord.Embed(title="以下のSEを追加しました")
        embed.add_field(name="正規表現", value=word,inline=True)
        embed.add_field(name="再生ファイル", value=server_dict[str(word)],inline=True)
        await ctx.respond(embed=embed)
        with open(server_se_list, 'w') as f:
            json.dump(server_dict,f,indent=4,ensure_ascii=False)

    @se.command(description="サーバーからSEを削除します",guild_ids=guild_list)
    async def delete(self,ctx,word:Option(str,description="削除する正規表現")):
        guild=ctx.guild
        server_se_path = './SE/'+str(guild.id)+"/"
        server_se_list = './SE/'+str(guild.id)+"/list.json"
        if not os.path.exists(server_se_list):
            with open(server_se_list, 'w') as f:
                f.write("{}")
        with open(server_se_list, 'r') as f:
            server_dict=json.load(f)
        if (word in server_dict):
            keyword=word
            valueword=server_dict[str(word)]
            del server_dict[str(word)]
            embed = discord.Embed(title="以下のSEをサーバーから削除しました")
            embed.add_field(name="正規表現", value=keyword,inline=True)
            embed.add_field(name="再生ファイル", value=valueword,inline=True)
            if not (valueword in server_dict.values()):
                os.remove(server_se_path+valueword)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("そのSEは登録されていません")
        with open(server_se_list, 'w') as f:
            json.dump(server_dict,f,indent=4,ensure_ascii=False)


    @se.command(description="声質を設定します",guild_ids=guild_list)
    async def voice_set(self,ctx,
                m:Option(str,choices=["angry","bashful","normal","happy","sad"],description="声質"),
                r:Option(float,description="速さ",min_value=0.0),
                fm:Option(float,description="ピッチ"),
                a:Option(float,description="オールパス値",min_value=0.0,max_value=1.0)):
        SECog.user_voice[str(ctx.author.id)]={"m":m,"r":str(r),"fm":str(fm),"a":str(a)}
        with open('./voiceconf/'+str(ctx.author.id)+'.json', 'w') as f:
            json.dump(SECog.user_voice[str(ctx.author.id)],f,indent=4)
        embedTitle = ctx.author.name+"の声質設定"
        embed = discord.Embed(title=embedTitle)
        embed.add_field(name="声質", value=m)
        embed.add_field(name="速さ", value=r)
        embed.add_field(name="ピッチ", value=fm)
        embed.add_field(name="オールパス値", value=a)
        await ctx.respond("声質を変更しました",embed=embed)

    @se.command(description="サーバー辞書に単語を追加します",guild_ids=guild_list)
    async def aw(self,ctx,word:Option(str,"単語"),reading:Option(str,"読み")):
        server_dict_path = './dict/'+str(ctx.guild.id)+'.json'
        if not os.path.exists(server_dict_path):
            with open(server_dict_path, 'w') as f:
                f.write("{}")
        with open(server_dict_path, 'r') as f:
            server_dict=json.load(f)
        server_dict[str(word)]=reading
        embed = discord.Embed(title="以下の単語をサーバー辞書に追加しました")
        embed.add_field(name="単語", value=word,inline=True)
        embed.add_field(name="読み", value=server_dict[str(word)],inline=True)
        await ctx.respond(embed=embed)
        with open(server_dict_path, 'w') as f:
            json.dump(server_dict,f,indent=4,ensure_ascii=False)

    @se.command(description="サーバー辞書から単語を削除します",guild_ids=guild_list)
    async def dw(self,ctx,word:Option(str,"削除する単語")):
        server_dict_path = './dict/'+str(ctx.guild.id)+'.json'
        if not os.path.exists(server_dict_path):
            with open(server_dict_path, 'w') as f:
                f.write("{}")
        with open(server_dict_path, 'r') as f:
            server_dict=json.load(f)
        if (word in server_dict):
            keyword=word
            valueword=server_dict[str(word)]
            del server_dict[str(word)]
            embed = discord.Embed(title="以下の単語をサーバー辞書から削除しました",guild_ids=guild_list)
            embed.add_field(name="単語", value=keyword,inline=True)
            embed.add_field(name="読み", value=valueword,inline=True)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("その単語は登録されていません")
        with open(server_dict_path, 'w') as f:
            json.dump(server_dict,f,indent=4,ensure_ascii=False)

    @se.command(description="サーバー辞書に登録されている単語を表示します",guild_ids=guild_list)
    async def lw(self,ctx):
        try:
            await ctx.defer()
            paginator = pages.Paginator(pages=self.get_WORDList(ctx.guild.id), show_disabled=False, show_indicator=True,author_check=False)
            paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
            paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
            paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
            paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)
            await paginator.send(ctx, ephemeral=False)
        except Exception:
            await ctx.respond("辞書に登録されていません")

    """
    @se.command(description="声質設定の詳しい説明が見れます")
    async def sethelp(self,ctx):
        await ctx.send("/se set (声質)　(速さ)　(ピッチ)　(オールパス値)　で設定できます")
        await ctx.send("声質：angry bashful normal happy sad の５つから選べます")
        await ctx.send("速さ：0.0~　速さを選べます　ピッチ：声の高さを指定できます")
        await ctx.send("オールパス値：0.0~1.0 の間で指定するとなんか変わります")
    """

    @se.command(description="今の声質の設定が見れます",guild_ids=guild_list)
    async def voice_show(self,ctx):
        with open('./voice/'+str(ctx.author.id)+'.json','r') as f:
            df = json.load(f)
        embedTitle = ctx.author.name+"の声質設定"
        embed = discord.Embed(title=embedTitle)
        embed.add_field(name="声質", value=df['m'])
        embed.add_field(name="速さ", value=df['r'])
        embed.add_field(name="ピッチ", value=df['fm'])
        embed.add_field(name="オールパス値", value=df['a'])
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        chat_id = message.channel.id
        if message.author.bot:
            return

        if not os.path.exists('./voiceconf/'+str(message.author.id)+'.json'):
            SECog.user_voice[str(message.author.id)]={"m":"normal","r":"1.0","fm":"0.0","a":"0.5"}
            with open('./voiceconf/'+str(message.author.id)+'.json', 'w') as f:
                json.dump(SECog.user_voice[str(message.author.id)],f,indent=4)

        if message.content.startswith('；') or message.content.startswith('/'):
            return

        if guild.voice_client != None and chat_id == SECog.server_chat[guild]:
            server_se_path = './SE/'+str(guild.id)+"/"
            server_se_list = './SE/'+str(guild.id)+"/list.json"
            se_list={}
            if os.path.exists(server_se_list):
                with open(server_se_list, 'r') as f:
                    se_list=json.load(f)
            for word,se in se_list.items():
                if re.fullmatch(word,message.content)!=None:
                    await self.SEplay(server_se_path+se,guild)
                    return
            try:
                p = re.compile('[\u0020-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E\u2000-\u2E60\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65\u3000-\u303F]+')
                if message.content != '' and p.fullmatch(message.content)==None:
                    ow = creat_WAV(message)
                    await self.SEplay(ow,guild)
            except pydub.exceptions.CouldntDecodeError:
                return

    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after):
        guild = member.guild
        server_conf = './guildconf/'+str(guild.id)+'.json'
        join_notifiction=True
        if os.path.exists(server_conf):
            with open(server_conf, 'r') as f:
                server_conf_dict=json.load(f)
            join_notifiction = server_conf_dict["join_notifiction"]
        if member.bot:
            return
        if guild.voice_client != None :
            if before.channel == after.channel:
                return
            if after.channel == guild.voice_client.channel and join_notifiction:
                ow = creat_WAV(None,member.display_name+"が通話に参加しました",member.guild.id)
                await self.SEplay(ow,guild)
            elif before.channel == guild.voice_client.channel:
                members=guild.voice_client.channel.members
                for mem in members:
                    if mem.bot == False:
                        return
                await self.disconnect_server(guild)


def setup(bot):
    bot.add_cog(SECog(bot))
