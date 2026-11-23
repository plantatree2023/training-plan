import json, datetime as dt
WD=["周一","周二","周三","周四","周五","周六","周日"]
def fp(s): s=int(round(s)); return f"{s//60}'{s%60:02d}\""
def fc(s): s=int(round(s)); return f"{s//60}:{s%60:02d}"
# date -> (t, tag, title, items, why); km computed from runs
R={}  # date -> list of runs (km, sec)
X={}  # date -> list of other activity strings
acts=[("9-29",.2503,169),("9-29",7.27031,3305),("10-1",1.51675,756),("10-1",2.02317,725),("10-1",.2407,61),
("10-4",7.40125,3235),("10-7",.56811,234),("10-7",3.0441,1029),("10-10",7.64759,3207),("10-12",.70317,312),("10-12",3.41072,1512),
("10-13",5.02454,2046),("10-16",5.05587,2083),("10-17",5.03961,2297),("10-19",10.153,4376),("10-22",5.01778,1677),("10-24",9.98989,4961),
("10-26",5.01784,2345),("10-27",6.42648,2613),("10-29",2.51507,1229),("10-29",5.01287,2153),("10-31",8.41293,3824),
("11-2",7.2235,2945),("11-4",11.8141,5508),("11-5",.7261,303),("11-5",.25527,74),("11-5",1.02545,269),("11-5",1.06399,622),
("11-6",.301,176),("11-7",.79569,358),("11-7",3.55506,1375)]
for k,km,s in acts: R.setdefault(k,[]).append((km,s))
X["9-29"]=["另走路 <b>3.1公里</b>"]
X["10-25"]=["单车 <b>8分钟</b>"]
X["10-28"]=["单车 <b>16分钟</b> + <b>3分钟</b>"]
X["10-29"]=["中午单车 <b>4分钟</b>"]
X["11-1"]=["单车 <b>14分钟</b>"]
X["11-6"]=["中午椭圆机 <b>7分钟</b>"]
SPECIAL={
 "10-1":("interval","快跑","2公里快跑",None,"2公里平均 <b>5'58\"</b>,前后各有慢跑"),
 "10-7":("interval","快跑","3公里快跑",None,"3公里平均 <b>5'38\"</b>"),
 "10-22":("interval","5K测试","5K测试",None,"5公里用时约 <b>27:57</b>(移动时间),平均 <b>5'34\"</b>"),
 "11-2":("interval","间歇跑","4×1000米间歇",None,"按 <b>5'30\"</b> 跑的 4×1000米"),
 "11-5":("interval","快跑","1公里快跑",None,"1公里 <b>4'22\"</b>(4:29),前后有热身和放松"),
 "11-7":("tempo","节奏跑","3.5公里稍快跑",None,"主段 <b>3.6公里</b>,平均 <b>6'27\"</b>"),
}
def make():
    weeks=[]; start=dt.date(2026,9,28)
    for wi in range(6):
        days=[]
        for i in range(7):
            d=start+dt.timedelta(7*wi+i); k=f"{d.month}-{d.day}"
            runs=R.get(k,[]); km=round(sum(r[0] for r in runs),1)
            items=[]
            if runs:
                main=max(runs,key=lambda r:r[0])
                tot=sum(r[1] for r in runs)
                if k in SPECIAL:
                    t,tag,title,_,line=SPECIAL[k]; items.append("已完成:"+line)
                    items.append(f"当天共跑 <b>{km:g}公里</b>")
                else:
                    long=km>=9.5
                    t,tag="long" if long else "easy","长距离" if long else "轻松跑"
                    title="长距离跑" if long else "轻松跑"
                    items.append(f"已完成:<b>{km:g}公里</b>,平均 <b>{fp(tot/km)}</b>")
                items+=X.get(k,[])
                why="实际记录,来自Strava。10/26到11/7的记录是批量导入的,没有步频。"
                days.append(dict(key=f"2026-{d.month}-{d.day}",d=f"{d.month}/{d.day}",w=WD[i],t=t,tag=tag,title=title,km=km,items=items,why=why,pre=True))
            elif k in X:
                days.append(dict(key=f"2026-{d.month}-{d.day}",d=f"{d.month}/{d.day}",w=WD[i],t="cross",tag="交叉训练",title="单车或椭圆机",km=0,items=["已完成:"+X[k][0]],why="实际记录,来自Strava。",pre=True))
            else:
                days.append(dict(key=f"2026-{d.month}-{d.day}",d=f"{d.month}/{d.day}",w=WD[i],t="rest",tag="休息",title="休息",km=0,items=["没有记录"],why="这一天Strava上没有训练记录。"))
        weeks.append({"note":"实际记录","days":days})
    return weeks
