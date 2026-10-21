# -*- coding: utf-8 -*-
"""生成动作的拼音检索索引（C3）：全拼 + 首字母 + 口语别名。

没有 pypinyin 可用，改为维护一张「汉字→拼音」表（只覆盖 103 个动作名里出现的 169 个字），
再用它组合每个动作名的全拼与首字母。新增动作时若有新字，脚本会报出来。
"""
import csv, io, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, "精选100动作.csv")
OUT_PATH = os.path.join(BASE, "拼音索引.json")

PINYIN = {
"三":"san","上":"shang","下":"xia","中":"zhong","举":"ju","亚":"ya","人":"ren","仰":"yang","伸":"shen",
"位":"wei","体":"ti","侧":"ce","俄":"e","俯":"fu","倒":"dao","健":"jian","克":"ke","其":"qi","农":"nong",
"凳":"deng","分":"fen","划":"hua","前":"qian","力":"li","动":"dong","单":"dan","卧":"wo","卷":"juan",
"压":"ya","双":"shuang","反":"fan","史":"shi","合":"he","后":"hou","向":"xiang","哈":"ha","哑":"ya","四":"si",
"土":"tu","地":"di","坐":"zuo","垂":"chui","壶":"hu","外":"wai","夫":"fu","头":"tou","姿":"zi","字":"zi",
"安":"an","宽":"kuan","密":"mi","小":"xiao","尼":"ni","屈":"qu","展":"zhan","山":"shan","师":"shi","平":"ping",
"开":"kai","式":"shi","弓":"gong","引":"yin","弯":"wan","德":"de","悬":"xuan","战":"zhan","扑":"pu","打":"da",
"抓":"zhua","抬":"tai","拉":"la","挺":"ting","推":"tui","提":"ti","握":"wo","摆":"bai","撑":"cheng","斜":"xie",
"斯":"si","早":"zao","杠":"gang","杯":"bei","板":"ban","柱":"zhu","桥":"qiao","梨":"li","步":"bu","死":"si",
"比":"bi","毛":"mao","水":"shui","波":"bo","深":"shen","滚":"gun","熊":"xiong","爬":"pa","牧":"mu","犬":"quan",
"状":"zhuang","登":"deng","直":"zhi","相":"xiang","石":"shi","硬":"ying","碎":"sui","空":"kong","窄":"zhai",
"立":"li","站":"zhan","箱":"xiang","索":"suo","绳":"sheng","罗":"luo","羊":"yang","翻":"fan","者":"zhe","耳":"er",
"耸":"song","肌":"ji","股":"gu","肩":"jian","背":"bei","胸":"xiong","脊":"ji","脚":"jiao","腘":"guo","腹":"fu",
"腿":"tui","臀":"tun","臂":"bi","自":"zi","船":"chuan","荡":"dang","虫":"chong","行":"xing","西":"xi","角":"jiao",
"诺":"nuo","走":"zou","起":"qi","超":"chao","距":"ju","跪":"gui","跳":"tiao","踢":"ti","踵":"zhong","蹬":"deng",
"蹲":"dun","身":"shen","车":"che","转":"zhuan","轮":"lun","过":"guo","部":"bu","钻":"zuan","铃":"ling","锤":"chui",
"阔":"kuo","阶":"jie","阿":"a","集":"ji","面":"mian","颅":"lu","颈":"jing","飞":"fei","马":"ma","髋":"kuan",
"高":"gao","鸟":"niao",
}

# 目标肌群 → 口语别名（让"二头""翘臀"这种词也能搜到）
TARGET_ALIAS = {
    "biceps": ["ertou", "erboutou"],
    "triceps": ["santou", "sanboutou"],
    "pectorals": ["xiongji", "xiong"],
    "abs": ["fuji", "fubu"],
    "glutes": ["qiaotun", "tunbu"],
    "lats": ["beikuo"],
    "upper back": ["beibu"],
    "delts": ["sanjiaoji", "jiantou"],
    "hamstrings": ["guoshengji", "datuiHou"],
    "quads": ["gutouji"],
    "calves": ["xiaotui"],
    "spine": ["xiaBei", "shujizhu"],
    "cardiovascular system": ["youyang", "xifei"],
    "traps": ["xiefangji"],
    "adductors": ["neishouji"],
    "levator scapulae": ["tijianjiaji"],
}


def main():
    rows = list(csv.DictReader(io.open(CSV_PATH, encoding="utf-8")))
    missing = sorted({c for r in rows for c in r["标准中文名"] if "\u4e00" <= c <= "\u9fff"} - set(PINYIN))
    if missing:
        print("缺少拼音的字：", "".join(missing))
        return 1
    index = {}
    for r in rows:
        name = r["标准中文名"]
        py = "".join(PINYIN[c] for c in name if c in PINYIN)
        pyi = "".join(PINYIN[c][0] for c in name if c in PINYIN)
        alias = TARGET_ALIAS.get(r["目标肌群"], []) + [r["标准中文名"]]
        index[r["英文名"]] = {"py": py, "pyi": pyi, "alias": [a.lower() for a in alias]}
    out = {"version": "1.0", "note": "key 为 精选100动作.csv 的英文名；py 全拼、pyi 首字母、alias 口语别名", "items": index}
    io.open(OUT_PATH, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"生成 {len(index)} 条拼音索引 -> {os.path.basename(OUT_PATH)}")
    for k in list(index)[:4]:
        print("  ", k, index[k]["py"], "/", index[k]["pyi"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
