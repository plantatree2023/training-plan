import json, datetime as dt, sys
sys.path.insert(0, "/home/claude/gen")
from legacy import LEGACY

WD = ["周一","周二","周三","周四","周五","周六","周日"]

def t2s(s):  # "25:30" -> seconds
    m, x = s.split(":"); return int(m) * 60 + int(x)
def fp(sec):  # pace m'ss"
    sec = int(round(sec)); return f"{sec // 60}'{sec % 60:02d}\""
def fc(sec):  # clock m:ss
    sec = int(round(sec)); return f"{sec // 60}:{sec % 60:02d}"
def rh(x): return round(x * 2) / 2
def rng(a, b): return f"<b>{fp(a)}–{fp(b)}</b>"

def paces(t5k):
    p = t5k / 5
    T = p + 17
    return dict(p=p, I=p - 6, T=T, Elo=p + 93, Ehi=p + 128, Slo=T + 35, Shi=T + 50)

HOLI = {
    "2026-12-24": "平安夜,时间紧可以缩短",
    "2026-12-25": "圣诞节:可以挪到周六,长跑挪到周日",
    "2026-12-31": "跨年夜,时间紧可以缩短",
    "2027-1-1": "元旦:可以挪到周六,长跑挪到周日",
    "2027-5-31": "阵亡将士纪念日,时间可以灵活安排",
    "2027-7-5": "独立日假期,时间可以灵活安排",
    "2027-9-6": "劳动节,时间可以灵活安排",
    "2027-11-25": "感恩节,可以休息",
}

def day(date, t, tag, title, km, items, why):
    key = f"{date.year}-{date.month}-{date.day}"
    items = list(items)
    if key in HOLI: items.append(HOLI[key])
    if date.month in (6, 7, 8) and t in ("easy", "long"):
        items.append("天热时以心率为准,配速慢一些没关系")
    return {"key": key, "d": f"{date.month}/{date.day}", "w": WD[date.weekday()], "t": t, "tag": tag,
            "title": title, "km": km, "items": items, "why": why}

def easy_items(P, extra=None):
    it = [f"心率 <b>≤150</b>,配速约 {rng(P['Elo'], P['Ehi'])}"]
    if extra: it += extra
    return it

# ---------- quality sessions ----------
def tue_session(kind, P, M):
    I = P["I"]
    if kind == "1000":
        reps = 6 if M >= 48 else 5; rep = 1000; lo, hi = I - 2, I + 3; rest = "2分30秒"; jog = .3
        name = "1000米间歇"; why = "1000米一组,在接近最大摄氧量的强度下累积时间,是提高5K最直接的训练。"
    elif kind == "800":
        reps = 8 if M >= 50 else (7 if M >= 46 else 6); rep = 800; lo, hi = I - 4, I + 1; rest = "2分钟"; jog = .25
        name = "800米间歇"; why = "800米比1000米短一点、配速略快,组数多,练最大摄氧量的同时练速度。"
    elif kind == "1200":
        reps = 5 if M >= 50 else 4; rep = 1200; lo, hi = I, I + 5; rest = "3分钟"; jog = .35
        name = "1200米间歇"; why = "每组更长,练在接近最大摄氧量时坚持更久,对5K后半程最有用。"
    else:
        reps = 4 if M >= 50 else 3; rep = 1600; lo, hi = I + 3, I + 8; rest = "3分钟"; jog = .4
        name = "1600米间歇"; why = "最长的一种间歇,配速略慢于其他间歇,连接最大摄氧量和比赛配速。"
    km = rh(2 + reps * rep / 1000 + (reps - 1) * jog + 1.5)
    items = ["热身 <b>2公里</b> 慢跑 + 4组加速跑",
             f"<b>{reps}×{rep}米</b> 配速 {rng(lo, hi)}(每组 {fc(lo * rep / 1000)}–{fc(hi * rep / 1000)})",
             f"组间慢跑 <b>{rest}</b>", "放松慢跑 <b>1.5公里</b>", "最后一组与第一组用时差 <b>≤3秒</b>"]
    return km, name, items, why

def fri_session(kind, P, M, race_pace=None):
    T = P["T"]
    hr = "心率 <b>165–172</b>,不超过175"
    if kind == "cruise":
        reps = 4 if M >= 50 else 3
        km = rh(2 + reps * 2 + (reps - 1) * .2 + 1)
        return km, "巡航间歇", ["热身 <b>2公里</b> 慢跑", f"<b>{reps}×2公里</b> 配速 {rng(T, T + 5)}", "组间慢跑 <b>1分钟</b>", "放松慢跑 <b>1公里</b>", hr], \
            "把阈值配速拆成几段,组间只休息1分钟,能在阈值强度下累积更多时间。"
    if kind == "tempo":
        L = 6 if M >= 50 else (5 if M >= 44 else 4)
        km = 2 + L + 1
        return km, f"{L}公里连续节奏跑", ["热身 <b>2公里</b> 慢跑", f"<b>{L}公里</b> 连续,配速 {rng(T, T + 6)}", "放松慢跑 <b>1公里</b>", hr], \
            "连续的阈值跑,练长时间顶住较高强度的能力。"
    if kind == "2x3":
        L = 4 if M >= 52 else 3
        km = 2 + 2 * L + .3 + 1
        return rh(km), f"2×{L}公里节奏跑", ["热身 <b>2公里</b> 慢跑", f"<b>2×{L}公里</b> 配速 {rng(T, T + 5)}", "组间慢跑 <b>2分钟</b>", "放松慢跑 <b>1公里</b>", hr], \
            "比连续节奏跑多一点总量,中间短暂恢复,质量更容易保证。"
    # race pace
    reps = 4 if M >= 50 else 3
    km = rh(2 + reps * 1.6 + (reps - 1) * .25 + 1)
    rp = race_pace
    return km, "比赛配速1600米", ["热身 <b>2公里</b> 慢跑", f"<b>{reps}×1600米</b> 配速 {rng(rp - 2, rp + 2)}(下次测试的目标配速)", "组间慢跑 <b>2分钟</b>", "放松慢跑 <b>1公里</b>"], \
        "测试前的专项课:用下次测试的目标配速跑,让身体记住这个节奏。"

def build_week(mon, M, P, bi, tue_kind, fri_kind, race_pace, hills):
    tkm, tname, titems, twhy = tue_session(tue_kind, P, M)
    fkm, fname, fitems, fwhy = fri_session(fri_kind, P, M, race_pace)
    L = min(18, max(11, rh(0.3 * M)))
    w = rh(0.12 * M) if M >= 48 else 0
    e = rh((M - tkm - fkm - L - w) / 2)
    if e < 4: L -= (4 - e) * 2; e = 4
    k = [2, 3, 4][bi % 3]
    d = [mon + dt.timedelta(i) for i in range(7)]
    thu_extra = ["跑后 <b>6–8×10秒</b> 坡道冲刺,走下坡恢复"] if hills else ["跑后 <b>4×20秒</b> 加速跑"]
    days = [
        day(d[0], "easy", "轻松跑", "轻松跑 + 力量", e, easy_items(P, ["跑后力量训练 <b>20–30分钟</b>"]),
            "质量课前的轻松跑,维持跑量;力量训练保护膝盖和小腿。"),
        day(d[1], "interval", "间歇跑", tname, tkm, titems, twhy),
    ]
    if w:
        days.append(day(d[2], "easy", "轻松跑", "轻松跑 + 力量", w, easy_items(P, ["跑后力量训练 <b>20–30分钟</b>", "腿沉就换成椭圆机"]),
                        "跑量到了48公里以上,周三改成轻松跑来分摊跑量;仍然是两次质量课之间的恢复日。"))
    else:
        days.append(day(d[2], "cross", "交叉训练", "椭圆机或单车 + 力量", 0, ["椭圆机或单车 <b>45分钟</b>,心率 <b>135–150</b>", "力量训练 <b>20–30分钟</b>"],
                        "两次质量课之间的恢复日。补有氧但不增加冲击。"))
    days += [
        day(d[3], "easy", "轻松跑", "轻松跑", e, easy_items(P, thu_extra),
            "维持跑量;" + ("坡道冲刺练腿部力量和跑步经济性,冲击比平地冲刺小。" if hills else "加速跑保持步频和速度感,为周五做准备。")),
        day(d[4], "tempo", "节奏跑", fname, fkm, fitems, fwhy),
        day(d[5], "long", "长距离", "长距离跑,后段稳定跑", L,
            [f"前 <b>{rh(L - k):g}公里</b> 轻松,心率 <b>≤150</b>", f"最后 <b>{k}公里</b> 配速 {rng(P['Slo'], P['Shi'])},心率 <b>155–165</b>"],
            "一周最长的一次。后段稳定跑练疲劳时保持配速的能力。"),
        day(d[6], "rest", "休息", "完全休息", 0, ["不安排训练"], "两次质量课加一次长跑后,必须留出完整的休息日。"),
    ]
    return days

def down_week(mon, M, P):
    I = P["I"]
    L = rh(0.3 * M)
    e = rh((M - 8.5 - 5 - L) / 2)
    d = [mon + dt.timedelta(i) for i in range(7)]
    return [
        day(d[0], "easy", "轻松跑", "轻松跑 + 力量", e, easy_items(P, ["跑后力量训练 <b>20–30分钟</b>"]), "减量周开始。跑量降到约八成,让身体吸收前几周的训练。"),
        day(d[1], "interval", "间歇跑", "1000米间歇(减量)", 8.5,
            ["热身 <b>2公里</b> 慢跑", f"<b>4×1000米</b> 配速 {rng(I - 2, I + 3)}", "组间慢跑 <b>2分30秒</b>", "放松慢跑 <b>1.5公里</b>"],
            "减量不减强度:保留一次最大摄氧量刺激,组数减少。"),
        day(d[2], "cross", "交叉训练", "椭圆机或单车 + 力量", 0, ["椭圆机或单车 <b>40分钟</b>,心率 <b>135–150</b>", "力量训练 <b>20–30分钟</b>"], "低冲击的有氧加力量。"),
        day(d[3], "easy", "轻松跑", "轻松跑", e, easy_items(P, ["跑后 <b>4×20秒</b> 加速跑"]), "维持跑步习惯和步频。"),
        day(d[4], "easy", "轻松跑", "轻松跑(本周不做节奏跑)", 5, easy_items(P, ["也可以换成椭圆机 <b>40分钟</b>"]), "本周只安排一次质量课,这是减量周的主要减法。"),
        day(d[5], "long", "长距离", "长距离跑(全程轻松)", L, ["全程心率 <b>≤150</b>", "不做后段提速"], "维持耐力,把恢复放在第一位。"),
        day(d[6], "rest", "休息", "完全休息", 0, ["不安排训练"], "减量周结束时,腿应该明显比前几周新鲜。"),
    ]

def test_items(median, lo_s, hi_s, race=False):
    p = median / 5
    return ["比赛当天早点到,留足热身时间" if race else "傍晚在跑道或平路测,条件和之前一致",
            "热身 <b>2公里</b> + 4组加速跑",
            f"第1公里 {rng(p + 6, p + 9)}",
            f"第2到4公里 {rng(p - 1, p + 2)}",
            "最后1公里有余力就冲",
            f"预计 <b>{lo_s}–{hi_s}</b>,中位数约 <b>{fc(median)}</b>"]

def test_week(mon, P, median, lo_s, hi_s, label):
    I = P["I"]
    d = [mon + dt.timedelta(i) for i in range(7)]
    return [
        day(d[0], "easy", "轻松跑", "轻松跑 + 力量", 6, easy_items(P, ["跑后 <b>4–6组</b> 加速跑", "力量训练用轻到中等重量"]), "测试周开始。力量训练减轻,避免影响周五。"),
        day(d[1], "interval", "间歇跑", "600米间歇", 7.5,
            ["热身 <b>2公里</b> 慢跑", f"<b>5×600米</b> 配速 {rng(I - 4, I + 1)}(每组 {fc((I - 4) * .6)}–{fc((I + 1) * .6)})", "组间慢跑 <b>2分钟</b>", "放松慢跑 <b>1.5公里</b>", "测试前最后一次强度课,别跑过头"],
            "测试前最后一次强度刺激,量比平时少,保持速度感又不累积疲劳。"),
        day(d[2], "cross", "交叉训练", "休息或轻松椭圆机", 0, ["完全休息,或椭圆机 <b>30分钟</b> 轻松", "只做膝后静止练习,不做其他力量"], "两天后就测试,以恢复为主。"),
        day(d[3], "easy", "轻松跑", "测试前轻松跑", 4, ["很慢的 <b>4公里</b> + <b>4×20秒</b> 加速跑(八成力)", "不要骑车"], "测试前一天。很短很慢,让腿在周五不发沉。"),
        day(d[4], "interval", "5K测试", f"5K测试({label})", 8, test_items(median, lo_s, hi_s), "每月一次的检验。按成绩查配速表,更新下一个月所有训练的配速。"),
        day(d[5], "easy", "恢复跑", "恢复跑", 4, ["很慢的 <b>3–4公里</b>,心率 <b>≤140</b>", "不骑车,不做力量"], "测试后的恢复跑,帮助腿放松。"),
        day(d[6], "rest", "休息", "完全休息", 0, ["不安排训练"], "测试后休息一天,下周开始新一轮。"),
    ]

D = lambda y, m, d: dt.date(y, m, d)
weeks = []
def add(days, note): weeks.append({"note": note, "days": days})

ROT_T = ["1000", "800", "1200", "1600"]
ROT_F = ["cruise", "tempo", "2x3"]

def cycle(start, Ms, base, next_med, test_mon, test_label, lo_s, hi_s, rot=0, down_last=False):
    P = paces(t2s(base))
    rp = t2s(next_med) / 5
    for i, M in enumerate(Ms):
        mon = start + dt.timedelta(7 * i)
        hills = mon.month in (5, 6, 7, 8)
        if down_last and i == len(Ms) - 1:
            add(down_week(mon, M, P), "减量周")
            continue
        last_build = (i == len(Ms) - 1) or (down_last and i == len(Ms) - 2)
        fk = "race" if last_build else ROT_F[(i + rot) % 3]
        add(build_week(mon, M, P, i, ROT_T[(i + rot) % 4], fk, rp, hills), "2 次质量课")
    add(test_week(test_mon, P, t2s(next_med), lo_s, hi_s, test_label), f"测试周 · {test_mon.month}/{test_mon.day + 4} 5K测试")

# C1: Dec 21 - Jan 24 (test 1/22)
cycle(D(2026,12,21), [40, 42, 44, 35], "25:30", "24:40", D(2027,1,18), "1月", "24:05", "25:20", rot=0, down_last=True)

# C2: Jan 25 - Feb 14 race
P = paces(t2s("24:40")); rp = t2s("24:00") / 5
add(build_week(D(2027,1,25), 44, P, 0, "1200", "cruise", rp, False), "2 次质量课")
add(build_week(D(2027,2,1), 40, P, 1, "800", "race", rp, False), "比赛前最后一个训练周")
d = [D(2027,2,8) + dt.timedelta(i) for i in range(7)]
I = P["I"]
add([
    day(d[0], "easy", "轻松跑", "轻松跑 + 加速跑", 6, easy_items(P, ["跑后 <b>4–6组</b> 加速跑", "力量训练用轻重量"]), "比赛周开始。跑量降到平时的六成左右,强度保留。"),
    day(d[1], "interval", "间歇跑", "比赛配速1000米", 7, ["热身 <b>2公里</b> 慢跑", f"<b>3×1000米</b> 配速 {rng(rp - 2, rp + 2)}(比赛配速)", "组间慢跑 <b>2分钟</b>", "放松慢跑 <b>1.5公里</b>"], "比赛前最后一次强度课,只用比赛配速,让身体记住节奏。"),
    day(d[2], "cross", "交叉训练", "休息或轻松椭圆机", 0, ["完全休息,或椭圆机 <b>30分钟</b> 轻松", "只做膝后静止练习"], "以恢复为主。"),
    day(d[3], "easy", "轻松跑", "轻松跑", 5, easy_items(P, ["跑后 <b>4×20秒</b> 加速跑"]), "维持节奏,不增加疲劳。"),
    day(d[4], "easy", "轻松跑", "轻松跑", 4, easy_items(P), "很轻松地跑,睡够。"),
    day(d[5], "easy", "轻松跑", "赛前激活跑", 3, ["很慢的 <b>3公里</b> + <b>4×20秒</b> 加速跑", "晚饭多吃米饭或面"], "比赛前一天。让腿动一动,第二天起跑不发沉。"),
    day(d[6], "interval", "5K比赛", "5K比赛", 8, test_items(t2s("24:00"), "23:20", "24:40", race=True) + ["目标:跑进 <b>23:40</b>,刷新Strava上的历史最佳"], "这次训练周期的目标比赛。"),
], "比赛周 · 2/14 5K比赛")

# Feb recovery + rebuild
P = paces(t2s("24:00"))
d = [D(2027,2,15) + dt.timedelta(i) for i in range(7)]
add([
    day(d[0], "rest", "休息", "完全休息", 0, ["不安排训练"], "比赛后第一天,完全休息。"),
    day(d[1], "easy", "轻松跑", "恢复跑", 4, ["很慢的 <b>4公里</b>,心率 <b>≤140</b>"], "很轻的恢复跑,帮助腿放松。"),
    day(d[2], "cross", "交叉训练", "椭圆机或单车", 0, ["椭圆机或单车 <b>30分钟</b> 轻松", "膝后静止练习"], "低冲击的恢复。"),
    day(d[3], "easy", "轻松跑", "轻松跑", 5, easy_items(P), "恢复跑量。"),
    day(d[4], "rest", "休息", "休息", 0, ["不安排训练"], "比赛后的恢复周,多休息一天。"),
    day(d[5], "long", "长距离", "轻松长跑", 8, ["全程心率 <b>≤150</b>"], "慢慢恢复长跑。"),
    day(d[6], "easy", "轻松跑", "轻松跑", 4, easy_items(P), "恢复周结束。"),
], "恢复周")
d = [D(2027,2,22) + dt.timedelta(i) for i in range(7)]
T = P["T"]
add([
    day(d[0], "easy", "轻松跑", "轻松跑 + 力量", 5, easy_items(P, ["跑后力量训练 <b>20–30分钟</b>"]), "回到正常训练,力量训练恢复。"),
    day(d[1], "easy", "轻松跑", "轻松跑 + 加速跑", 6, easy_items(P, ["跑后 <b>6×20秒</b> 加速跑"]), "先用加速跑唤醒速度,还不做间歇。"),
    day(d[2], "cross", "交叉训练", "椭圆机或单车 + 力量", 0, ["椭圆机或单车 <b>45分钟</b>,心率 <b>135–150</b>", "力量训练 <b>20–30分钟</b>"], "低冲击的有氧加力量。"),
    day(d[3], "easy", "轻松跑", "轻松跑", 6, easy_items(P), "恢复跑量。"),
    day(d[4], "tempo", "节奏跑", "3公里连续节奏跑", 6.5, ["热身 <b>2公里</b> 慢跑", f"<b>3公里</b> 连续,配速 {rng(T, T + 6)}", "放松慢跑 <b>1.5公里</b>", "心率 <b>165–172</b>"], "比赛后第一次质量课,只做一次、量不大。"),
    day(d[5], "long", "长距离", "长距离跑", 10, ["全程心率 <b>≤150</b>"], "恢复到10公里长跑。"),
    day(d[6], "rest", "休息", "完全休息", 0, ["不安排训练"], "下周开始新一轮训练。"),
], "重建周")

cycle(D(2027,3,1), [42, 44, 46], "24:00", "23:40", D(2027,3,22), "3月", "23:05", "24:20", rot=2)
cycle(D(2027,3,29), [44, 46, 48], "23:40", "23:20", D(2027,4,19), "4月", "22:45", "24:00", rot=1)
cycle(D(2027,4,26), [46, 48, 50], "23:20", "23:00", D(2027,5,17), "5月", "22:25", "23:40", rot=3)
cycle(D(2027,5,24), [48, 50, 52, 42], "23:00", "22:45", D(2027,6,21), "6月", "22:10", "23:30", rot=0, down_last=True)
cycle(D(2027,6,28), [50, 52, 54], "22:45", "22:35", D(2027,7,19), "7月", "22:00", "23:20", rot=2)
cycle(D(2027,7,26), [52, 54, 55], "22:35", "22:20", D(2027,8,16), "8月", "21:45", "23:00", rot=1)
cycle(D(2027,8,23), [52, 55, 55, 44], "22:20", "22:00", D(2027,9,20), "9月", "21:25", "22:40", rot=3, down_last=True)
cycle(D(2027,9,27), [50, 52, 54], "22:00", "21:45", D(2027,10,18), "10月", "21:10", "22:25", rot=0)

# C11: Oct 25 - Nov 20 goal race
P = paces(t2s("21:45")); rp = t2s("21:35") / 5
add(build_week(D(2027,10,25), 50, P, 0, "1000", "cruise", rp, False), "2 次质量课")
add(build_week(D(2027,11,1), 48, P, 1, "1200", "race", rp, False), "2 次质量课")
add(down_week(D(2027,11,8), 40, P), "减量周 · 目标赛前两周")
d = [D(2027,11,15) + dt.timedelta(i) for i in range(7)]
I = P["I"]
add([
    day(d[0], "easy", "轻松跑", "轻松跑 + 加速跑", 6, easy_items(P, ["跑后 <b>4–6组</b> 加速跑", "力量训练用轻重量"]), "比赛周开始。跑量降下来,强度保留。"),
    day(d[1], "interval", "间歇跑", "比赛配速1000米", 7, ["热身 <b>2公里</b> 慢跑", f"<b>3×1000米</b> 配速 {rng(rp - 2, rp + 2)}(比赛配速)", "组间慢跑 <b>2分钟</b>", "放松慢跑 <b>1.5公里</b>"], "比赛前最后一次强度课,只用比赛配速。"),
    day(d[2], "cross", "交叉训练", "休息或轻松椭圆机", 0, ["完全休息,或椭圆机 <b>30分钟</b> 轻松"], "以恢复为主。"),
    day(d[3], "easy", "轻松跑", "轻松跑", 5, easy_items(P, ["跑后 <b>4×20秒</b> 加速跑"]), "维持节奏,不增加疲劳。"),
    day(d[4], "easy", "轻松跑", "赛前激活跑", 3, ["很慢的 <b>3公里</b> + <b>4×20秒</b> 加速跑", "晚饭多吃米饭或面"], "比赛前一天,让腿动一动。"),
    day(d[5], "interval", "5K比赛", "5K目标赛", 8, test_items(t2s("21:35"), "21:00", "22:10", race=True) + ["一年训练的目标比赛"], "全年训练的目标比赛。"),
    day(d[6], "rest", "休息", "完全休息", 0, ["不安排训练"], "比赛后完全休息。"),
], "比赛周 · 11/20 5K目标赛")
d = [D(2027,11,22) + dt.timedelta(i) for i in range(7)]
add([
    day(d[0], "rest", "休息", "完全休息", 0, ["不安排训练"], "比赛后继续休息。"),
    day(d[1], "easy", "轻松跑", "恢复跑", 4, ["很慢的 <b>4公里</b>,心率 <b>≤140</b>"], "很轻的恢复跑。"),
    day(d[2], "cross", "交叉训练", "椭圆机或单车", 0, ["椭圆机或单车 <b>30分钟</b> 轻松"], "低冲击的恢复。"),
    day(d[3], "rest", "休息", "休息", 0, ["不安排训练"], "节日休息。"),
    day(d[4], "easy", "轻松跑", "轻松跑", 5, easy_items(P), "恢复跑量。"),
    day(d[5], "long", "长距离", "轻松长跑", 8, ["全程心率 <b>≤150</b>"], "慢慢恢复。"),
    day(d[6], "rest", "休息", "复盘", 0, ["回顾这一年的数据,规划2028年"], "一年结束,复盘后再定下一年的目标。"),
], "恢复周")

ALL = LEGACY + weeks
# sanity: continuity of dates
prev = None
for w in ALL:
    assert len(w["days"]) == 7, w["days"][0]["key"]
    for x in w["days"]:
        y, m, dd = map(int, x["key"].split("-")); cur = dt.date(y, m, dd)
        if prev: assert cur == prev + dt.timedelta(1), (prev, cur)
        assert WD[cur.weekday()] == x["w"], x["key"]
        prev = cur
for w in ALL:
    w["km"] = rh(sum(x["km"] for x in w["days"]))
print(len(ALL), "weeks", ALL[0]["days"][0]["key"], "->", ALL[-1]["days"][-1]["key"])
for w in ALL: print(w["days"][0]["d"], w["km"], w["note"])
json.dump({"weeks": ALL}, open("/home/claude/plan_site/plan.json", "w"), ensure_ascii=False, separators=(",", ":"))
