import discord, asyncio, os, sys
from discord.ext import commands
import json
import pandas as pd
import re


home_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), '../..')
with open(os.path.join(home_dir, 'config.json'), 'r') as f:
    conf = json.load(f)

namedf = pd.read_csv(os.path.join(home_dir, 'namelist.csv'))
dciddf = pd.read_csv(os.path.join(home_dir, 'dcidlist.csv'))
game = discord.Game("스크린샷 수집")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix='$')

@client.event
async def on_ready(): 
    print("영령전 스크린샷 수집 중(collecting Hall of heroes)")
    print('---------------')
    await client.change_presence(status=discord.Status.online, 
    activity=game)

@client.command()
async def test_channel(ctx):
    channel = ctx.message.channel
    print(channel)

@client.command()
async def uid(ctx, uid):
    global namedf, dciddf
    uid = int(re.findall('\d+',uid)[0])
#    kdid = ctx.guild.id   #어느 디스코드 서버인지 체크
    dcid = ctx.author   #디스코드 아이디 체크
    temp = namedf['nickname'][namedf['uid']==uid].values
    if not temp:
        await ctx.send("""uid를 다시 확인 해 주세요 (서버원 명단에 존재하지 않음)
            check the uid again (not a member of KD1525)""")
    else:
        nickname = temp[0]
        with open(os.path.join(home_dir, 'dcidlist.csv'),'a',encoding='UTF-8') as f:
            f.write(f'{dcid},{uid},{nickname}\n')
        dciddf = pd.concat([dciddf, pd.DataFrame([{'dcid':dcid,'uid':uid,'nickname':nickname}])])
        await ctx.send(f"""{nickname} {uid} : uid 등록완료
        {nickname} {uid} : uid registered""")

@client.command(aliases=['제출','본캐','본계정'])
async def submit(ctx, *args):
    global namedf, dciddf
    channel = ctx.message.channel
    #if channel != "spirits-제출-submit":
    #    await ctx.send("여기 아니야!!")
    #    return
    dcid = ctx.author
    if len(args)==0:
        temp = dciddf['uid'][dciddf['dcid']==dcid].values
        if len(temp)==0:
            await ctx.send("""uid를 먼저 등록하시거나(!uid 11111111), 혹은 !제출 11111111 형식으로 적어주세요
            need to register uid first""")
            return
            #uid = 99999999
        else:
            uid = temp[-1]
    else:
        uid = int(re.findall('\d+',args[0])[0])
    attachment = ctx.message.attachments
#    kdid = ctx.guild.id   #어느 디스코드 서버인지 체크 / 나중에 다른서버에도 서비스한다면 필요한부분. 
    dcid = ctx.author   #디스코드 아이디 체크    
    temp = namedf['nickname'][namedf['uid']==uid].values
    if not temp:
        await ctx.send("""uid를 다시 확인 해 주세요 (서버원 명단에 존재하지 않음)
        check the uid again (not a member of KD1525)""")
    else:
        nickname = temp[0]
        if len(attachment)==0:
            await ctx.send("""스크린샷을 첨부해 주세요 (첨부파일과 uid를 동시에 전송해야합니다)
            plz attatch screenshot (send the screenshot and uid at the same time in one message)""")
        else:
            for attach in attachment:
                fname = str(attach).split('/')[-1]
                exten = fname.split('.')[-1]
                await attach.save(fp=os.path.join(os.path.join(home_dir, 'screenshots'), str(uid)+'.'+exten))
            await ctx.send(f"""{nickname} {uid} : 영령전 제출완료
            {nickname} {uid} : finished""")

##1525에서는 사용 안함
"""
@client.command(aliases=['부캐','부계정'])
async def sub(ctx, uid):
    global namedf, dciddf
    uid = int(re.findall('\d+',uid)[0])
    attachment = ctx.message.attachments
    dcid = ctx.author   #디스코드 아이디 체크
    temp = dciddf['nickname'][dciddf['dcid']==dcid].values
    if len(temp)==0:
        await ctx.send("부계정 영령전을 제출하시려면 본계정의 uid를 먼저 등록해주세요 (!uid xxxxxxxx)")
    else:
        mainnick = temp[-1]
        if len(attachment)==0:
            await ctx.send("스크린샷을 첨부해 주세요 (첨부파일과 uid를 동시에 전송해야합니다)")
        else:
            for attach in attachment:
                fname = str(attach).split('/')[-1]
                exten = fname.split('.')[-1]
                mainid = dciddf['uid'][dciddf['dcid']==dcid].values[-1]
                await attach.save(fp=dir+f'sub{mainid}_{uid}.{exten}')
            nickname = namedf['nickname'][namedf['uid']==uid].values
            if nickname:
                await ctx.send(f"{mainnick}님 부계정 {nickname} {uid} : 영령전 제출완료")
            else:
                await ctx.send(f"{mainnick}님 부계정 {uid} : 영령전 제출완료 (500위 외 닉네임 확인 불가)")
"""
bot_info = conf['bot_info']
token = bot_info["TOKEN"]
print(token)
client.run(token)

