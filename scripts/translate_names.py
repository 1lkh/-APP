#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 exercises.json 生成动作中文名对照表（机器翻译初稿，需人工校对）。
用法: python3 scripts/translate_names.py
"""
import json, re, os, csv

SRC = os.environ.get("SRC", "/tmp/ex.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, "..", "动作中文名对照表.md")
OUT_CSV = os.path.join(HERE, "..", "动作中文名对照表.csv")

# ---------------------------------------------------------------------------
# 词典（统一为: 英文短语 -> 中文；匹配时空格与连字符等价、忽略大小写）
# ---------------------------------------------------------------------------
DICT = {
    # —— 器械 / 器材 ——
    "resistance band": "阻力带", "olympic barbell": "奥林匹克杠铃",
    "leverage machine": "固定器械", "smith machine": "史密斯机",
    "stability ball": "瑜伽球", "exercise ball": "瑜伽球",
    "medicine ball": "药球", "wheel roller": "健腹轮",
    "stationary bike": "动感单车", "bosu ball": "波速球",
    "ez barbell": "曲杠", "ez bar": "曲杠", "ez-bar": "曲杠", "ez": "曲杠",
    "bodyweight": "自重", "body weight": "自重",
    "dumbbell": "哑铃", "barbell": "杠铃", "cable": "绳索",
    "band": "弹力带", "kettlebell": "壶铃", "smith": "史密斯机",
    "lever": "固定器械", "sled machine": "雪橇机", "sled": "雪橇机",
    "sledge": "雪橇机", "rope": "绳索", "roller": "泡沫轴",
    "bosu": "波速球", "olympic": "奥林匹克", "wheel": "健腹轮",
    "t-bar": "T杠", "tbar": "T杠", "landmine": "地雷管",
    "trap bar": "六角杠", "tire": "轮胎", "machine": "器械",
    "weighted": "负重", "assisted": "助力", "suspended": "悬挂",
    "suspension": "悬挂", "ring": "吊环", "bar": "杠", "bars": "双杠",
    "treadmill": "跑步机", "elliptical": "椭圆机", "stepper": "踏步机",
    "stepmill": "登山机", "bike": "单车", "ergometer": "测功仪",
    "rower": "划船机", "cage": "龙门架", "towel": "毛巾",
    "cambered bar": "弧形杠", "trap-bar": "六角杠", "ab wheel": "健腹轮",
    "dumbbells": "哑铃",

    # —— 身体部位 / 目标肌群 ——
    "cardiovascular system": "心肺", "serratus anterior": "前锯肌",
    "levator scapulae": "肩胛提肌", "biceps": "二头肌", "bicep": "二头肌",
    "triceps": "三头肌", "tricep": "三头肌", "pectoralis": "胸大肌",
    "pectorals": "胸大肌", "chest": "胸", "shoulder": "肩",
    "deltoid": "三角肌", "delts": "三角肌", "delt": "三角肌",
    "abdominal": "腹", "abdominals": "腹肌", "abs": "腹肌", "ab": "腹",
    "glutes": "臀大肌", "glute": "臀", "gluteus": "臀肌",
    "quads": "股四头肌", "quad": "股四头肌", "hamstring": "腘绳肌",
    "calves": "小腿", "calf": "小腿", "lat": "背阔肌", "lats": "背阔肌",
    "trap": "斜方肌", "traps": "斜方肌", "forearm": "前臂", "forearms": "前臂",
    "wrist": "腕", "neck": "颈", "back": "背", "lower back": "下背",
    "oblique": "腹斜肌", "obliques": "腹斜肌", "hip": "髋", "hips": "髋部",
    "leg": "腿", "legs": "腿", "knee": "膝", "knees": "膝",
    "adductor": "内收肌", "adductors": "内收肌", "abductor": "外展肌",
    "abductors": "外展肌", "piriformis": "梨状肌", "tibialis": "胫骨前肌",
    "spine": "脊柱", "rectus": "腹直肌", "groin": "腹股沟",
    "femoral": "股", "femoris": "股", "peroneals": "腓骨肌",
    "sternum": "胸骨", "scapula": "肩胛", "scapular": "肩胛",
    "soleus": "比目鱼肌", "gastrocnemius": "腓肠肌",

    # —— 核心动作（短语） ——
    "mountain climber": "登山者", "good morning": "早安式",
    "bench press": "卧推", "shoulder press": "肩推",
    "military press": "实力推", "chest press": "胸推",
    "leg press": "倒蹬", "overhead press": "过头推举",
    "arnold press": "阿诺德推举", "push press": "借力推",
    "floor press": "地板卧推", "close grip bench press": "窄握卧推",
    "incline bench press": "上斜卧推", "decline bench press": "下斜卧推",
    "push-up": "俯卧撑", "push up": "俯卧撑",
    "pull-up": "引体向上", "pull up": "引体向上", "chin-up": "引体向上",
    "chin-ups": "引体向上", "pull-ups": "引体向上", "l-pull-up": "L字引体向上",
    "sit-up": "仰卧起坐", "sit up": "仰卧起坐",
    "muscle-up": "双力臂", "body-up": "挺身",
    "jackknife": "折刀式", "jack knife": "折刀式",
    "concentration curl": "集中弯举", "preacher curl": "牧师凳弯举",
    "hammer curl": "锤式弯举", "wrist curl": "腕弯举",
    "bicep curl": "二头肌弯举", "biceps curl": "二头肌弯举",
    "leg curl": "腿弯举", "leg extension": "腿屈伸",
    "triceps extension": "三头肌伸展", "tricep extension": "三头肌伸展",
    "calf raise": "提踵", "lateral raise": "侧平举", "front raise": "前平举",
    "rear raise": "后平举", "leg raise": "抬腿", "hip raise": "抬臀",
    "inverted row": "反向划船", "upright row": "直立划船",
    "seated row": "坐姿划船", "bent over row": "俯身划船",
    "split squat": "分腿深蹲", "pistol squat": "手枪深蹲",
    "goblet squat": "高脚杯深蹲", "hack squat": "哈克深蹲",
    "sissy squat": "西西深蹲", "front squat": "前蹲", "back squat": "后蹲",
    "box squat": "箱式深蹲", "overhead squat": "过头深蹲",
    "sumo squat": "相扑深蹲", "wall sit": "靠墙静蹲",
    "high bar squat": "高杠深蹲", "low bar squat": "低杠深蹲",
    "romanian deadlift": "罗马尼亚硬拉", "sumo deadlift": "相扑硬拉",
    "stiff leg deadlift": "直腿硬拉", "single leg deadlift": "单腿硬拉",
    "snatch grip deadlift": "抓举握硬拉",
    "side plank": "侧平板支撑", "glute bridge": "臀桥",
    "hip thrust": "臀推", "power clean": "高翻", "hang clean": "悬垂高翻",
    "clean and jerk": "挺举", "muscle snatch": "抓举",
    "russian twist": "俄罗斯转体", "side bend": "侧屈",
    "toe touch": "触脚尖", "dead bug": "死虫式", "bird dog": "鸟狗式",
    "cat cow": "猫牛式", "face pull": "面拉",
    "v-up": "V字起身", "v-sit": "V字坐", "l-sit": "L字坐",
    "figure 8": "8字环绕", "box jump": "跳箱",
    "bulgarian split squat": "保加利亚分腿深蹲",
    "farmer's carry": "农夫行走", "farmers walk": "农夫行走",
    "jumping jack": "开合跳", "inchworm": "毛毛虫爬",
    "bicycle crunch": "自行车卷腹", "child's pose": "婴儿式",
    "captain's chair": "船长椅", "ab wheel rollout": "健腹轮滚动",
    "hip flexor stretch": "髋屈肌拉伸",

    # —— 单个动作词 ——
    "curl": "弯举", "curls": "弯举", "press": "推举", "raise": "平举",
    "row": "划船", "squat": "深蹲", "squats": "深蹲", "extension": "伸展",
    "stretch": "拉伸", "crunch": "卷腹", "crunches": "卷腹",
    "pulldown": "下拉", "deadlift": "硬拉", "fly": "飞鸟", "flyes": "飞鸟",
    "twist": "转体", "twists": "转体", "twisting": "转体", "twisted": "转体",
    "lunge": "弓步", "pullover": "上拉", "shrug": "耸肩",
    "dip": "臂屈伸", "dips": "臂屈伸", "kickback": "后屈伸",
    "kickbacks": "后屈伸", "rotation": "旋转", "rotate": "旋转",
    "rotational": "旋转", "rotary": "旋转", "clean": "高翻",
    "jump": "跳", "jumps": "跳", "lift": "提拉", "lifting": "提拉",
    "bridge": "臀桥", "snatch": "抓举", "pull": "拉",
    "pushdown": "下压", "plank": "平板支撑", "planche": "水平支撑",
    "jerk": "挺举", "abduction": "外展", "adduction": "内收",
    "bend": "侧屈", "bends": "侧屈", "step-up": "登阶", "step up": "登阶",
    "run": "跑", "sprint": "冲刺", "sprints": "冲刺",
    "walk": "走", "walking": "行走", "climber": "登山者",
    "burpee": "波比跳", "jack": "开合跳", "swing": "摆荡",
    "slam": "下砸", "throw": "抛", "march": "踏步",
    "hyperextension": "背屈伸", "handstand": "倒立",
    "windmill": "风车", "superman": "超人式", "thruster": "挺举深蹲",
    "wiper": "雨刷式", "wipers": "雨刷式", "scissors": "剪刀腿",
    "kayak": "皮划艇", "touch": "触", "touchers": "触", "toucher": "触",
    "reach": "够", "tap": "触", "hold": "保持", "hug": "抱",
    "carry": "搬运", "crawl": "爬", "climb": "攀爬",
    "slide": "滑", "hop": "跳", "hops": "跳", "rollout": "健腹轮",
    "rollerout": "健腹轮", "roll": "滚", "up": "起身", "ups": "起身",
    "curl-up": "卷腹", "sit": "坐", "sitting": "坐姿",
    "kick": "踢", "kicks": "踢", "flexion": "屈",
    "pike": "派克", "crusher": "碾压", "skullcrusher": "碎颅",
    "skull": "碎颅", "face": "面",
    "janda": "扬达", "sissy": "西西", "zercher": "泽奇",
    "pistol": "手枪", "cossack": "哥萨克", "sumo": "相扑",
    "romanian": "罗马尼亚", "turkish": "土耳其", "russian": "俄罗斯",
    "korean": "韩国", "hindu": "印度", "jefferson": "杰斐逊",
    "goblet": "高脚杯", "french": "法式", "zottman": "佐特曼",
    "arnold": "阿诺德", "cuban": "古巴", "bradford": "布拉德福德",
    "gironda": "吉隆达", "jm": "JM", "tate": "泰特", "otis": "奥蒂斯",
    "scott": "斯科特", "pendlay": "潘德雷", "svend": "斯文",
    "pallof": "帕洛夫", "farmer": "农夫", "farmers": "农夫",
    "crab": "螃蟹", "bear": "熊", "frog": "青蛙", "donkey": "驴",
    "cobra": "眼镜蛇式", "sphinx": "狮身人面式", "dog": "犬",
    "monster": "怪兽", "spider": "蜘蛛", "gorilla": "大猩猩",
    "pirate": "海盗", "boxing": "拳击", "bowling": "保龄球",
    "bicycle": "自行车", "mountain": "登山", "ski": "滑雪", "skier": "滑雪",
    "batting": "挥棒", "battling": "战绳", "flutter": "打水",
    "maltese": "马耳他", "london": "伦敦", "straddle": "分腿",
    "stork": "鹳式", "saw": "锯", "seesaw": "跷跷板", "waiter": "侍者",
    "swimmer": "游泳", "yoga": "瑜伽",

    # —— 姿势 / 变体 / 修饰 ——
    "standing": "站姿", "seated": "坐姿", "sitted": "坐姿",
    "sitting": "坐姿", "lying": "卧姿", "incline": "上斜",
    "decline": "下斜", "flat": "平", "one arm": "单臂", "one-arm": "单臂",
    "single": "单", "single-arm": "单臂", "single-leg": "单腿",
    "alternate": "交替", "alternating": "交替",
    "reverse": "反向", "reverse-grip": "反握", "revers": "反向",
    "wide-grip": "宽握", "wide": "宽", "close-grip": "窄握",
    "close": "窄", "narrow": "窄", "neutral": "中立",
    "underhand": "反握", "overhand": "正握", "pronated": "正握",
    "pronate-grip": "正握", "supinated": "反握", "supination": "旋后",
    "pronation": "旋前", "overhead": "过头", "over": "过",
    "front": "前", "rear": "后", "side": "侧", "lateral": "侧",
    "high": "高", "low": "低", "bent": "俯身", "bent-over": "俯身",
    "upright": "直立", "kneeling": "跪姿", "prone": "俯卧",
    "supine": "仰卧", "half": "半", "full": "全程", "partial": "半程",
    "isometric": "等长", "plyo": "爆发", "plyometric": "爆发",
    "two": "双", "one": "单", "three": "三", "double": "双",
    "stiff": "直腿", "straight": "直", "straight-arm": "直臂",
    "straight arm": "直臂", "straight-leg": "直腿", "straight leg": "直腿",
    "extended": "伸展", "deep": "深", "hammer": "锤式",
    "cross": "交叉", "cross-over": "交叉", "crossover": "交叉",
    "crossovers": "交叉", "parallel": "平行", "diagonal": "对角",
    "vertical": "垂直", "horizontal": "水平", "internal": "内旋",
    "external": "外旋", "elevated": "垫高", "raised": "抬升",
    "bottoms-up": "倒置", "bottoms": "倒置", "captain": "船长",
    "captains": "船长", "butterfly": "蝴蝶", "angle": "角度",
    "angled": "斜", "archer": "弓箭手", "apart": "分开",
    "around": "环绕", "behind head": "颈后", "behind": "后",
    "between": "之间", "both": "双", "bottom": "底部", "top": "顶部",
    "grip": "握", "gripless": "无握", "gripper": "握力",
    "palm": "掌", "palms": "掌心", "palm-in": "掌心向内",
    "finger": "指", "hand": "手", "hands": "手", "arm": "臂", "arms": "臂",
    "elbow": "肘", "elbows": "肘", "head": "头", "heel": "脚跟",
    "ankle": "踝", "ankles": "踝", "feet": "脚", "foot": "脚",
    "toe": "脚尖", "toes": "脚尖", "floor": "地面", "ground": "地面",
    "wall": "靠墙", "bench": "凳", "box": "箱", "chair": "椅",
    "step": "台阶", "stepbox": "踏板", "platform": "踏板", "pad": "垫",
    "board": "板", "rack": "架", "pin": "销", "strap": "带",
    "straps": "带", "handle": "把手", "attachment": "附件",
    "with": "用", "against": "对抗", "above": "上方", "across": "横跨",
    "through": "穿过", "from": "从", "into": "至", "on": "上", "off": "离",
    "out": "出", "in": "内", "up-down": "上下", "side-to-side": "左右",
    "backward": "向后", "forward": "向前", "outstretched": "伸展",
    "clasped": "相扣", "reversed": "反向", "dynamic": "动态",
    "static": "静态", "quick": "快", "slow": "慢", "advanced": "进阶",
    "beginner": "入门", "intermediate": "中级", "modified": "改良",
    "unilateral": "单侧", "contralateral": "对侧", "multiple": "多",
    "negative": "离心", "power": "爆发力", "speed": "速度",
    "range": "幅度", "motion": "运动", "position": "位", "pose": "式",
    "style": "式", "variation": "变式", "sequence": "序列",
    "big": "大", "greatest": "最大", "impossible": "不可能",
    "rocking": "摇摆", "scissor": "剪刀", "self": "自", "semi": "半",
    "short": "短", "skin": "皮", "squad": "组", "star": "星",
    "twin": "双", "world": "世界", "balance": "平衡", "balancing": "平衡",
    "anti": "抗", "lever": "杠杆", "cambered": "弧",
    "squatting": "蹲", "military": "实力", "kettlebell": "壶铃",
    "fixed": "固定", "concentration": "集中", "hack": "哈克",
    "push": "推", "medicine": "药", "exercise": "练习",
    "figure": "8字", "and": "和", "release": "释放",
    "response": "回应", "l": "L字",

    # —— 补充：单字母前缀 / 器械别名 / 数据源拼写错误 ——
    "v-bar": "V杠", "v": "V字", "t": "T字", "w": "W字", "y": "Y字",
    "sz-bar": "曲杠", "sz": "曲杠", "t-raise": "T字平举",
    "y-raise": "Y字平举", "w-press": "W字推举",
    "arm blaster": "臂托", "blaster": "臂托", "hanging": "悬垂",
    "inverse": "反向", "support": "支撑", "supported": "支撑",
    "cross body": "体前交叉", "body": "体", "inner": "内侧",
    "inside": "内侧", "outside": "外侧", "upper": "上", "lower": "下",
    "lower body": "下半身", "lowerbody": "下半身", "stance": "站距",
    "wide stance": "宽站距", "drop": "下放", "drag": "拖拽",
    "drive": "驱动", "chin": "下巴", "chin tuck": "收下巴",
    "pelvic tilt": "骨盆卷动", "pelvictilt": "骨盆卷动",
    "pelvic": "骨盆", "tilt": "卷动", "raises": "平举", "presses": "推举",
    "circles": "画圈", "circular": "画圈", "circle": "画圈",
    "slingers": "甩绳", "slingers hanging": "甩绳悬垂",
    "pulley": "滑轮", "tuck": "团身", "iron": "铁",
    "tennis ball": "网球", "tennisball": "网球", "squeeze": "挤压",
    "pass": "传递", "posterior": "后侧", "hyper": "超",
    "air": "空", "air bike": "空中单车", "air squat": "空蹲",
    "all fours": "四点支撑", "allfours": "四点支撑", "astride": "跨立",
    "back and forth": "前后", "forth": "前后", "pec": "胸",
    "guillotine": "断头台", "basic": "基础", "ropes": "绳索",
    "stabilization": "稳定", "butt": "臀", "butt-ups": "臀起",
    "judo": "柔道", "judo flip": "柔道翻转", "judoflip": "柔道翻转",
    "middle": "中", "pro": "专业", "stirrups": "马镫",
    "thibaudeau": "蒂博多", "clap": "击掌", "clock": "时钟",
    "cocoons": "茧式", "curtsey": "屈膝礼", "cycle": "骑行",
    "diamond": "钻石", "peacher": "牧师凳", "elevator": "升降",
    "pyramid": "金字塔", "legged": "腿", "gravity": "重力",
    "flag": "人体旗帜", "human flag": "人体旗帜",
    "frankenstein": "弗兰肯斯坦", "reps": "次", "ham": "腘绳",
    "glute-ham": "臀腘", "keens": "膝", "hyght": "高位", "depth": "深度",
    "flexor": "屈肌", "renegade": "叛徒", "kipping": "借力",
    "lean": "倾斜", "left hook": "左勾拳", "lefthook": "左勾拳",
    "catch": "接", "mixed": "混合", "mixed grip": "正反握",
    "prisoner": "囚徒", "plus": "加", "quarter": "四分之一",
    "reclining": "躺", "thrusts": "推", "runners": "跑步者",
    "runner's stretch": "跑步者拉伸", "stride": "跨步",
    "front lever": "前水平", "back lever": "后水平",
    "reverse hyper": "反向背屈伸", "degrees": "度",
    "potty": "如厕式", "sledge hammer": "甩大锤",
    "get up": "起立", "turkish get up": "土耳其起立",
    "can opener": "开罐器", "full can": "满罐式",
    "flexor depresor retractor": "屈肌下压回缩",
    "flexordepresorretractor": "屈肌下压回缩",
    "depresor": "下压", "retractor": "回缩", "breeding": "哺育",
    "equipment": "", "supper": "晚餐", "major": "大",
    "point": "点", "point stance": "点站姿", "pointstance": "点站姿",
    "power point": "PowerPoint", "3 point stance": "三点支撑",
    "cat": "猫", "spell caster": "施法者", "spell": "施法", "caster": "施法者",
    "upward": "向上", "facing": "朝", "downward": "向下",
    "upward facing dog": "上犬式", "downward facing dog": "下犬式",
    "closer": "并拢", "stalder": "斯塔尔德", "skater": "滑冰",
    "trainer": "训练器", "flip": "翻转", "fallout": "外展",
    "wind": "风", "round": "绕", "rollerer": "健腹轮", "outer": "外侧",
    "benches": "凳", "staircase": "楼梯", "hang": "悬垂", "split": "分腿",
    "rocky": "洛奇",
}

# 整名兜底（优先精确匹配）
WHOLE = {
    "3/4 sit-up": "四分之三仰卧起坐",
    "45° side bend": "45度侧屈",
    "skin the cat": "翻猫式",
}

# 拍摄视角/版本噪音：删除
NOISE_RE = [
    r"\bv\.?\s*\d+\b",
    r"\(male\)", r"\(female\)", r"\(man\)", r"\(woman\)",
    r"\(back pov\)", r"\(side pov\)", r"\(front pov\)", r"\(pov\)",
    r"\bpov\b",
    r"\b(?:male|female|man|woman)\b",
]

STOP = {"the", "of", "to", "for", "a", "an", "at", "by", "or", "into",
        "onto", "off", "from", "up", "down", "over", "under"}


def clean(name: str) -> str:
    s = name.strip()
    s = s.replace("в°", "°")  # 修复数据源西里尔字母乱码
    for pat in NOISE_RE:
        s = re.sub(pat, " ", s, flags=re.IGNORECASE)
    s = s.replace("(", "（").replace(")", "）")
    s = s.replace(" - ", " ").replace(" -", " ")
    s = re.sub(r"\s+", " ", s).strip(" -– ")
    return s


def build_re(pat: str) -> str:
    """构造匹配一个短语的正则（空格/连字符等价、忽略大小写、词边界）。"""
    body = []
    for ch in pat:
        if ch in (" ", "-"):
            body.append(r"[ \-]+")
        else:
            body.append(re.escape(ch))
    return r"(?<![a-zA-Z0-9])" + "".join(body) + r"(?![a-zA-Z0-9])"


PATS = sorted(DICT.items(), key=lambda kv: -len(kv[0]))
COMPILED = [(re.compile(build_re(p)), zh) for p, zh in PATS]


def translate_seq(s: str) -> str:
    def repl(mobj):
        inner = mobj.group(1).strip()
        return "" if not inner else "（" + translate_seq(inner) + "）"
    s = re.sub(r"（([^（）]*)）", repl, s)

    for rx, zh in COMPILED:
        s = rx.sub(zh, s)

    s = s.replace("°", "度")
    for w in STOP:
        s = re.sub(r"(?<![a-zA-Z0-9])" + w + r"(?![a-zA-Z0-9])", "", s, flags=re.IGNORECASE)

    # 残留英文词两侧加空格（便于校对），中文连写、去掉中文与标点间的空格
    # 只处理 2 个及以上字母的连续串，避免拆散「V字/T字/Y字/W字/L字」这类单字母前缀
    s = re.sub(r"([a-zA-Z]{2,}(?:[a-zA-Z\-]*[a-zA-Z])?)", r" \1 ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff（）、，。])", r"\1", s)
    s = re.sub(r"([（）、，。])\s+(?=[\u4e00-\u9fff])", r"\1", s)
    return s.strip()


def translate_name(name: str) -> str:
    s = clean(name)
    low = s.lower().strip()
    for whole, zh in sorted(WHOLE.items(), key=lambda kv: -len(kv[0])):
        if low == whole:
            return zh
        if low.startswith(whole + " ") or low.startswith(whole):
            rest = s[len(whole):].strip()
            rest_zh = translate_name(rest) if rest else ""
            return zh + (" " + rest_zh if rest_zh else "")
    return translate_seq(s)


def main():
    data = json.load(open(SRC))
    rows, leftover = [], []
    for ex in data:
        en = ex["name"].strip()
        zh = translate_name(en)
        r = {"id": ex["id"], "en": en, "zh": zh,
             "body_part": ex.get("body_part", ""),
             "equipment": ex.get("equipment", ""),
             "target": ex.get("target", ""),
             "gif": ex.get("gif_url", "")}
        rows.append(r)
        if re.search(r"[a-zA-Z]", zh):
            leftover.append((en, zh))

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "英文名", "中文名", "身体部位", "器械", "目标肌群", "gif"])
        for r in rows:
            w.writerow([r["id"], r["en"], r["zh"], r["body_part"],
                        r["equipment"], r["target"], r["gif"]])

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# 动作中文名对照表\n\n")
        f.write("> 自动生成初稿，基于 [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset)。\n")
        f.write("> 共 %d 条。**中文名为机器翻译，需人工校对**。\n\n" % len(rows))
        f.write("| # | 英文名 | 中文名 | 部位 | 器械 | 目标肌群 |\n")
        f.write("|---|--------|--------|------|------|----------|\n")
        for r in rows:
            f.write(f'| {r["id"]} | {r["en"]} | {r["zh"]} | {r["body_part"]} | {r["equipment"]} | {r["target"]} |\n')

    print("rows:", len(rows), "| 仍含英文的条数:", len(leftover))
    print("->", OUT_MD)
    print("->", OUT_CSV)


if __name__ == "__main__":
    main()
