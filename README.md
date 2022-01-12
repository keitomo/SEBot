# SEBot
pycordで書かれたチャット読み上げ、SE再生機能などを備えたDiscordBotです。  

チャット読み上げにOpen JTalkを使用しています。  

# 実行環境  
Python 3.9.9 以上  
ライブラリはrequirements.txtにまとめてあります。  

Open JTalkについては各自調べてください。  
[Open JTalk](http://open-jtalk.sourceforge.net/)  

参考になるかもしれないサイト  
[OpenJTalk + python で日本語テキストを発話](https://qiita.com/kkoba84/items/b828229c374a249965a9)  

# 実行方法  
必要なライブラリを一括で追加  
```
pip install -r requirements.txt
```  

discord.uiを使用するためにpy-cordのみ別で追加  
```
pip install git+https://github.com/Pycord-Development/pycord
```  

discordbot.py内の以下を書き換え
```
token = os.environ['SE_BOT_TOKEN']　#自分のBotトークンに書き換え
ownerid = os.environ['OWNER_ID']　　#自分のDiscordIDに書き換え
```

実行コマンド  
```
python3 discordbot.py
```　　

# 何かあったら　　
まずは自分で調べてください。　　
聞きたいことがあったらTwitterで聞いてください。
