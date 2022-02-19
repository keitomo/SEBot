import subprocess
import json
import random,string
import re,os

def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))



def creat_WAV(message,s=None,server=None):
    #message.contentをテキストファイルに書き込み
    if message != None:
        input_file = './input/'+str(message.guild.id)+".txt"
    else:
        input_file = './input/'+str(server)+".txt"

    if s!=None:
        server_dict_path = './dict/'+str(server)+'.json'
        text = s
        df = {
            "m": "normal",
            "r": "1.0",
            "fm": "0.0",
            "a": "0.55"
            }
        if os.path.exists(server_dict_path):
            with open(server_dict_path, 'r') as f:
                server_dict=json.load(f)
            for key,value in server_dict.items():
                text = text.replace(key,value)
    else:
        server_dict_path = './dict/'+str(message.guild.id)+'.json'
        with open('./voiceconf/'+str(message.author.id)+'.json','r') as f:
            df = json.load(f)

        text = message.content

        stamp_pattern = r'(<:)([a-zA-Z0-9_]+)(:[0-9]+>)'
        text = re.sub(stamp_pattern,r'\2',text)

        user_pattern = r'<@[^0-9]*([0-9]+)>'

        while True:
            m=re.search(user_pattern,text)
            if m==None:
                break
            elif message.guild.get_member(int(m.groups()[0]))!=None:
                text = re.sub(user_pattern,message.guild.get_member(int(m.groups()[0])).display_name,text,1)
            elif message.guild.get_role(int(m.groups()[0]))!=None:
                text = re.sub(user_pattern,message.guild.get_role(int(m.groups()[0])).name,text,1)
            else:
                text = re.sub(user_pattern,"".name,text,1)

        channel_pattern = r'<#[^0-9]*([0-9]+)>'
        while True:
            m=re.search(channel_pattern,text)
            if m==None:
                break
            elif message.guild.get_channel(int(m.groups()[0]))!=None:
                text = re.sub(channel_pattern,message.guild.get_channel(int(m.groups()[0])).name,text,1)
            else:
                text = re.sub(channel_pattern,"",text,1)

        url_pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        text = re.sub(url_pattern,'ユーアールエルショウリャク',text)

        if os.path.exists(server_dict_path):
            with open(server_dict_path, 'r') as f:
                server_dict=json.load(f)
            for key,value in server_dict.items():
                text = re.sub(key,value,text)

    with open(input_file,'w',encoding='utf-8') as file:
        file.write(text)

    command = 'open_jtalk -x {x} -m {m} -r {r} -fm {fm} -a {a} -ow {ow} {input_file}'

    #辞書のPath
    x = '/var/lib/mecab/dic/open-jtalk/naist-jdic'

    #ボイスファイルのPath
    m = '/usr/share/hts-voice/mei/mei_'+df['m']+'.htsvoice'

    #発声のスピード
    r = df['r']

    fm = df['fm']

    a = df['a']

    #出力ファイル名　and　Path

    ow = './voice/'+randomname(8)+'.wav'

    args= {'x':x, 'm':m, 'r':r, 'fm':fm, 'a':a, 'ow':ow, 'input_file':input_file}

    cmd= command.format(**args)

    subprocess.run(cmd,stdin=subprocess.PIPE,shell=True,stdout = subprocess.DEVNULL)
    return ow

if __name__ == '__main__':
    creat_WAV('テスト',"")