#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 exercises.json 精选约 100 个最经典动作，输出人工校对过的标准中文名。
中文名为人工黄金标准（非机器翻译），可直接用于生产。
用法: python3 scripts/select_top100.py
"""
import json, re, os, csv

SRC = os.environ.get("SRC", "/tmp/ex.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, "..", "精选100动作.md")
OUT_CSV = os.path.join(HERE, "..", "精选100动作.csv")

# (匹配关键词, 标准中文名) —— 关键词尽量精确，脚本按「精确>最短包含」匹配
GOLDEN = [
    # —— 胸部 Chest ——
    ("push-up", "俯卧撑"),
    ("wide hand push up", "宽距俯卧撑"),
    ("diamond push-up", "钻石俯卧撑"),
    ("decline push-up", "下斜俯卧撑"),
    ("incline push-up", "上斜俯卧撑"),
    ("kneeling push-up", "跪姿俯卧撑"),
    ("barbell bench press", "杠铃卧推"),
    ("barbell incline bench press", "上斜杠铃卧推"),
    ("dumbbell bench press", "哑铃卧推"),
    ("dumbbell fly", "哑铃飞鸟"),
    ("chest dip", "双杠臂屈伸"),

    # —— 背部 Back ——
    ("pull-up", "引体向上"),
    ("chin-up", "反握引体向上"),
    ("wide grip pull-up", "宽握引体向上"),
    ("muscle up", "双力臂"),
    ("barbell deadlift", "杠铃硬拉"),
    ("romanian deadlift", "罗马尼亚硬拉"),
    ("sumo deadlift", "相扑硬拉"),
    ("barbell bent over row", "俯身杠铃划船"),
    ("kettlebell one arm row", "单臂壶铃划船"),
    ("cable seated row", "坐姿绳索划船"),
    ("cable lat pulldown", "高位下拉"),
    ("inverted row", "反向划船"),
    ("hyperextension", "背屈伸（山羊挺身）"),
    ("barbell shrug", "杠铃耸肩"),
    ("good morning", "早安式"),

    # —— 肩部 Shoulders ——
    ("dumbbell standing overhead press", "站姿哑铃过头推举"),
    ("dumbbell one arm shoulder press", "单臂哑铃肩推"),
    ("arnold press", "阿诺德推举"),
    ("dumbbell lateral raise", "哑铃侧平举"),
    ("dumbbell front raise", "哑铃前平举"),
    ("dumbbell reverse fly", "俯身哑铃反向飞鸟"),
    ("barbell upright row", "直立划船"),
    ("cable rear delt row", "绳索后三角肌划船"),

    # —— 手臂 Arms ——
    ("dumbbell bicep curl", "哑铃弯举"),
    ("barbell curl", "杠铃弯举"),
    ("hammer curl", "锤式弯举"),
    ("dumbbell concentration curl", "集中弯举"),
    ("dumbbell preacher curl", "牧师凳弯举"),
    ("triceps pushdown", "绳索下压"),
    ("bench dip", "凳上臂屈伸"),
    ("skull crusher", "仰卧三头肌伸展（碎颅式）"),
    ("dumbbell kickback", "哑铃俯身臂屈伸"),
    ("close-grip push-up", "窄距俯卧撑"),

    # —— 腿部 Legs ——
    ("barbell full squat", "杠铃深蹲"),
    ("front squat", "前蹲"),
    ("goblet squat", "高脚杯深蹲"),
    ("dumbbell squat", "哑铃深蹲"),
    ("single leg squat", "单腿深蹲"),
    ("barbell split squat", "杠铃分腿深蹲"),
    ("dumbbell lunge", "哑铃弓步蹲"),
    ("barbell hack squat", "杠铃哈克深蹲"),
    ("smith leg press", "倒蹬"),
    ("leg extension", "腿屈伸"),
    ("leg curl", "腿弯举"),
    ("standing calf raise", "站姿提踵"),
    ("barbell glute bridge", "杠铃臀桥"),
    ("low glute bridge on floor", "地面臀桥"),
    ("dumbbell step up", "登阶"),

    # —— 核心 Core ——
    ("crunch floor", "卷腹"),
    ("reverse crunch", "反向卷腹"),
    ("sit-up", "仰卧起坐"),
    ("front plank with twist", "平板转体"),
    ("side plank hip adduction", "侧平板髋外展"),
    ("lying leg raise", "仰卧抬腿"),
    ("hanging leg raise", "悬垂抬腿"),
    ("band bicycle crunch", "自行车卷腹"),
    ("russian twist", "俄罗斯转体"),
    ("mountain climber", "登山者"),
    ("dead bug", "死虫式"),
    ("superman push-up", "超人俯卧撑"),
    ("wheel rollerout", "健腹轮滚动"),
    ("band v-up", "V字起身"),

    # —— 有氧 / 全身 Cardio ——
    ("burpee", "波比跳"),
    ("jack jump", "开合跳"),
    ("jump squat", "深蹲跳"),
    ("box jump", "跳箱"),
    ("walking high knees lunge", "行走高抬腿弓步"),
    ("battling", "战绳"),
    ("air bike", "空中单车"),
    ("flutter", "打水踢腿"),
    ("kettlebell swing", "壶铃摆荡"),
    ("farmers walk", "农夫行走"),
    ("bear crawl", "熊爬"),
    ("inchworm", "毛毛虫爬"),
    ("thruster", "挺举深蹲"),
    ("turkish get up", "土耳其起立"),
    ("power clean", "高翻"),
    ("barbell one arm snatch", "单臂杠铃抓举"),
    ("barbell clean and press", "杠铃高翻推举"),

    # —— 拉伸 / 柔韧 Stretch ——
    ("hamstring stretch", "腘绳肌拉伸"),
    ("quad stretch", "股四头肌拉伸"),
    ("calf stretch", "小腿拉伸"),
    ("chest stretch", "胸部拉伸"),
    ("shoulder stretch", "肩部拉伸"),
    ("lat stretch", "背阔肌拉伸"),
    ("hip flexor stretch", "髋屈肌拉伸"),
    ("piriformis stretch", "梨状肌拉伸"),
    ("spine stretch", "脊柱拉伸"),
    ("neck stretch", "颈部拉伸"),
    ("upward facing dog", "上犬式"),
    ("sissy squat", "西西深蹲"),
    ("smith sumo squat", "史密斯相扑深蹲"),
]


def normalize(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"\([^)]*\)", " ", s)          # 去括号内容
    s = re.sub(r"\bv\.?\s*\d+\b", " ", s)     # 去 v.2
    s = re.sub(r"\b(?:male|female|man|woman|pov)\b", " ", s)
    s = s.replace("-", " ").replace("’", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    data = json.load(open(SRC))
    norm_map = {normalize(x["name"]): x for x in data}
    # 同名（规范化后）可能有多个，保留名字最短的
    shortest = {}
    for x in data:
        nk = normalize(x["name"])
        if nk not in shortest or len(x["name"]) < len(shortest[nk]["name"]):
            shortest[nk] = x

    results, missing = [], []
    for kw, zh in GOLDEN:
        nkw = normalize(kw)
        hit = shortest.get(nkw)                       # 精确（规范化后）
        if not hit:                                    # 最短包含
            cands = [(len(x["name"]), x) for k, x in shortest.items() if nkw in k]
            if cands:
                cands.sort(key=lambda t: t[0])
                hit = cands[0][1]
        if not hit:
            missing.append((kw, zh))
            continue
        results.append({
            "kw": kw, "zh": zh, "en": hit["name"],
            "body_part": hit.get("body_part", ""),
            "equipment": hit.get("equipment", ""),
            "target": hit.get("target", ""),
            "gif": hit.get("gif_url", ""),
        })

    # 按身体部位排序输出
    order = ["chest", "back", "shoulders", "upper arms", "upper legs",
             "lower legs", "waist", "cardio", "lower arms", "neck"]
    results.sort(key=lambda r: (order.index(r["body_part"]) if r["body_part"] in order else 99, r["zh"]))

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["标准中文名", "英文名", "身体部位", "器械", "目标肌群", "gif"])
        for r in results:
            w.writerow([r["zh"], r["en"], r["body_part"], r["equipment"], r["target"], r["gif"]])

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# 精选 100 动作（标准中文名，可直接进生产）\n\n")
        f.write("> 人工校对的标准译名，覆盖全身主要肌群；基于 [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset)。\n")
        f.write("> 素材 GIF/图片为 © Gym visual，需保留署名。\n\n")
        f.write("| 标准中文名 | 英文名 | 部位 | 器械 | 目标肌群 |\n")
        f.write("|-----------|--------|------|------|----------|\n")
        for r in results:
            f.write(f'| {r["zh"]} | {r["en"]} | {r["body_part"]} | {r["equipment"]} | {r["target"]} |\n')

    print("命中:", len(results), "| 未找到:", len(missing))
    for m in missing:
        print("  MISSING:", m)
    print("->", OUT_MD)
    print("->", OUT_CSV)


if __name__ == "__main__":
    main()
