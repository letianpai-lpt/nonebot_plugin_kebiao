import json
import datetime
import re
import requests
import ast
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText
from typing import Union
from nonebot.adapters import Event

global furl
global key
#配置文件的地址
furl="/root/bot/lolbot/lolbot/src/plugins/nonebot_plugin_kebiao/qqinfo.json"
#和风天气的个人开发者key
key="4e7fe30df877402bb5f20bbfed95350e"



#设置开始周数
def startweeknum(y,m,d):
    return datetime.date(y,m,d).isocalendar()[1]

#初步处理课表
def get_kb(fileurl):
    original_content=open(fileurl,"r",encoding='UTF-8')
    original_content=json.load(original_content)
    sjklist=original_content["sjkList"]
    sjk=[]
    for i in sjklist:
        sjk.append([i["qsjsz"],i["kcmc"]])
    kblist=original_content["kbList"]
    kb=[]
    for i in kblist:
        kb.append([i["zcd"],i["xqj"],i["xqjmc"],i["jc"],i["kcmc"],i["cdmc"],i["xm"]])
    kkb=[]
    for i in kb:
        kkb.append(i)
    for i in sjk:
        kkb.append(i)
    return kkb
#再次处理课表
def handleweeknum(kb):
    afterhand=[]
    for i in kb:
        weeklist=[]
        a=i[0].split(",")
        k=0
        #单双周处理
        for j in a:
            if "(单)" in j:
                j=j.replace("(单)","")
                k=1
            if "(双)" in j:
                j=j.replace("(双)","")
                k=2
            j=j[:-1]
            if "-" in j:
                b=j.split("-")
                for m in range(int(b[0]),int(b[1])+1):
                    if k==0:
                        weeklist.append(m)
                    if k==1:
                        if m%2==1:
                            weeklist.append(m)
                    if k==2:
                        if m%2==0:
                            weeklist.append(m)
            else:
                weeklist.append(int(j))
        after=[]
        after.append(weeklist)
        for n in i[1:]:
            after.append(n)
        afterhand.append(after)
    return afterhand
#获取今天周数和是周几
def gettime_today(startweeknum):
    tdweeknum=datetime.datetime.now().isocalendar()[1]
    nowweeknum=tdweeknum-startweeknum+1
    weekdaynum=datetime.datetime.today().weekday()+1
    return nowweeknum,weekdaynum
#获取明天周数和是周几
def gettime_tom(startweeknum):
    tomweeknum=(datetime.datetime.now()+datetime.timedelta(days=1)).isocalendar()[1]
    tomweeknum=tomweeknum-startweeknum+1
    tomweekdaynum=(datetime.datetime.today()+datetime.timedelta(days=1)).weekday()+1
    return tomweeknum,tomweekdaynum

#根据城市信息返回对应的emoji
def getwea_toady_and_tom(city):
    weapi="https://devapi.qweather.com/v7/weather/3d?"
    idapi="https://geoapi.qweather.com/v2/city/lookup?"
    city=ast.literal_eval(requests.get(idapi+"key="+key+"&"+"location="+city).text)["location"][0]["id"]
    wea=ast.literal_eval(requests.get(weapi+"key="+key+"&"+"location="+city).text)
    todaywea=wea["daily"][0]["textDay"]
    tomwea=wea["daily"][1]["textDay"]
    weathertab={
        "雨":"🌧",
        "雪":"❄",
        "晴":"☀",
        "云":"☁",
        "阴":"⛅"
    }
    todw="🌟"
    tomw="🌟"
    for i in weathertab:
        if i in todaywea:
            todw=weathertab[i]
        if i in tomwea:
            tomw=weathertab[i]
    return todw,tomw

#处理发出去的课表信息
def judge(weeknum,weekday,handkb,citywea="🌟"):
    daymap={1:"⏳星期一⏳",2:"⏳星期二⏳",3:"⏳星期三⏳",4:"⏳星期四⏳",5:"⏳星期五⏳",6:"⏳星期六⏳",7:"⏳星期日⏳"}
    if weekday in daymap:
        msg=daymap[weekday]+"\n-------------------------------------\n"
    for i in handkb:
        timetab={
            "1":"🕗",
            "2":"🕘",
            "3":"🕙",
            "4":"🕚",
            "5":"🕝",
            "6":"🕞",
            "7":"🕟",
            "8":"🕠",
            "9":"🕢",
            "10":"🕣",
            "11":"🕘",
            "12":"🕤",
        }
        #根据第几节返回对应的emoji
        try:
            if i[3][0] in timetab:
                kbtime=timetab[i[3][0]]
            else:
                kbtime="🕘"
            if weeknum in i[0] and weekday==int(i[1]):
                msg=msg+kbtime+i[3]+citywea+i[4]+"\n\n"+"🏠"+i[5]+"🏠\n🚶"+i[6]+"🚶\n-------------------------------------\n"
        except:
            if weeknum in i[0]:
                if msg[-1] !=":":
                    msg=msg+"🕹实践课:"
                if msg[-1] ==":":
                    msg=msg+i[1]+" "    
    return msg

#各个监听器
kebiao = on_command("kebiao", aliases={"今日课表","课表","课程表"}, priority=5)
tomkebiao = on_command("tomkebiao", aliases={"明日课表"}, priority=5)
weekkebiao = on_command("weekkebiao", aliases={"本周课表"}, priority=5)
nextweekkebiao = on_command("nextweekkebiao", aliases={"下周课表"}, priority=5)
kebiaohelp = on_command("kebiaohelp", aliases={"课表帮助"}, priority=5)

#课表帮助
@kebiaohelp.handle()
async def send_kebiaohelp(matcher: Matcher, args: Message = CommandArg()):
    msg="课表,今日课表\n明日课表\n本周课表\n下周课表"
    await kebiaohelp.finish(msg)

#今日课表
@kebiao.handle()
async def send_today_kb(event: Event,matcher: Matcher, args: Message = CommandArg()):
    try:
        qqinfo=str(event)
        qq=re.split(' from |@| ',qqinfo)[3]
        qqtoinfo=json.load(open(furl,"r",encoding="utf-8"))
        y=qqtoinfo[qq]["starttime"][0]
        m=qqtoinfo[qq]["starttime"][1]
        d=qqtoinfo[qq]["starttime"][2]
        try:
            city=qqtoinfo[qq]["city"]
        except:
            city="☀"
        todaywea=getwea_toady_and_tom(city=city)[0]
        a=judge(gettime_today(startweeknum(y,m,d))[0],gettime_today(startweeknum(y,m,d))[1],handleweeknum(get_kb(qqtoinfo[qq]["kbinfo"])),todaywea)
        msg="今日课表📝📝📝:\n\n"+a
        await kebiao.finish(msg)
    except:
        print("未绑定课表信息")

#明日课表
@tomkebiao.handle()
async def send_tom_kb(event: Event,matcher: Matcher, args: Message = CommandArg()):
    try:
        qqinfo=str(event)
        qq=re.split(' from |@| ',qqinfo)[3]
        qqtoinfo=json.load(open(furl,"r",encoding="utf-8"))
        y=qqtoinfo[qq]["starttime"][0]
        m=qqtoinfo[qq]["starttime"][1]
        d=qqtoinfo[qq]["starttime"][2]
        try:
            city=qqtoinfo[qq]["city"]
        except:
            city="☀"
        tomwea=getwea_toady_and_tom(city=city)[1]
        a=judge(gettime_tom(startweeknum(y,m,d))[0],gettime_tom(startweeknum(y,m,d))[1],handleweeknum(get_kb(qqtoinfo[qq]["kbinfo"])),tomwea)
        msg="明日课表📝📝📝:\n\n"+a
        await tomkebiao.finish(msg)
    except:
        print("未绑定课表信息")
#本周课表
@weekkebiao.handle()
async def send_nowweek_kb(event: Event,matcher: Matcher, args: Message = CommandArg()):
    try:
        qqinfo=str(event)
        qq=re.split(' from |@| ',qqinfo)[3]
        qqtoinfo=json.load(open(furl,"r",encoding="utf-8"))
        y=qqtoinfo[qq]["starttime"][0]
        m=qqtoinfo[qq]["starttime"][1]
        d=qqtoinfo[qq]["starttime"][2]
        a=""
        for i in range(1,8):
            a=a+judge(gettime_today(startweeknum(y,m,d))[0],i,handleweeknum(get_kb(qqtoinfo[qq]["kbinfo"])))+"\n✨✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
        msg="本周课表📝📝📝:\n\n"+a
        await weekkebiao.finish(msg)
    except:
        print("未绑定课表信息")
#下周课表
@nextweekkebiao.handle()
async def send_nowweek_kb(event: Event,matcher: Matcher, args: Message = CommandArg()):
    try:
        qqinfo=str(event)
        qq=re.split(' from |@| ',qqinfo)[3]
        qqtoinfo=json.load(open(furl,"r",encoding="utf-8"))
        y=qqtoinfo[qq]["starttime"][0]
        m=qqtoinfo[qq]["starttime"][1]
        d=qqtoinfo[qq]["starttime"][2]
        a=""
        for i in range(1,8):
            a=a+judge(gettime_today(startweeknum(y,m,d))[0]+1,i,handleweeknum(get_kb(qqtoinfo[qq]["kbinfo"])))+"\n✨✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
        msg="下周课表📝📝📝:\n\n"+a
        await nextweekkebiao.finish(msg)
    except:
        print("未绑定课表信息")
