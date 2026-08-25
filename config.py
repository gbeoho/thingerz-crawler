"""
Thingerz Social Media Content Crawler — Configuration
======================================================
Matches thingerz.com category/sub-category/district structure.
Every 6h, for each (sub_category, district), search across 6 platforms.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ── Directory ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "thingerz_crawler.db")
LOG_DIR = os.path.join(DATA_DIR, "logs")

# ── Tracks & Categories ────────────────────────────────────────────────
TRACKS = {
    "fun": {
        "name_zh": "娛樂·興趣",
        "name_en": "Fun",
        "categories": ["arts", "performance", "food", "beauty"],
    },
    "learning": {
        "name_zh": "學習·行業",
        "name_en": "Learning",
        "categories": ["commercial", "education", "wedding", "community"],
    },
}

CATEGORIES: Dict[str, dict] = {
    # Learning
    "commercial": {"track": "learning", "zh": "商業與專業服務", "en": "Commerce & Professional"},
    "education":  {"track": "learning", "zh": "教學與培訓",      "en": "Education & Training"},
    "wedding":    {"track": "learning", "zh": "婚禮與生活",      "en": "Wedding & Lifestyle"},
    "community":  {"track": "learning", "zh": "親子與社區",      "en": "Parenting & Community"},
    # Fun
    "arts":         {"track": "fun", "zh": "藝術與設計", "en": "Arts & Design"},
    "performance":  {"track": "fun", "zh": "表演與娛樂", "en": "Performance & Entertainment"},
    "food":         {"track": "fun", "zh": "飲食與手作", "en": "Food & Handcraft"},
    "beauty":       {"track": "fun", "zh": "美容與形象", "en": "Beauty & Image"},
}

# ── Sub-categories (54 total) ──────────────────────────────────────────
SUB_CATEGORIES: Dict[str, dict] = {
    # commercial
    "s001": {"category": "commercial", "zh": "市場研究與分析", "en": "Market Research & Analysis"},
    "s002": {"category": "commercial", "zh": "品牌推廣",       "en": "Brand Promotion"},
    "s003": {"category": "commercial", "zh": "網上生意",       "en": "Online Business"},
    "s004": {"category": "commercial", "zh": "專業顧問",       "en": "Professional Consulting"},
    "s005": {"category": "commercial", "zh": "室內設計",       "en": "Interior Design"},
    "s006": {"category": "commercial", "zh": "醫療服務",       "en": "Medical Services"},
    "s007": {"category": "commercial", "zh": "餐飲與酒類",     "en": "Food & Beverage"},
    "s008": {"category": "commercial", "zh": "活動與配對",     "en": "Events & Matching"},
    # education
    "s009": {"category": "education", "zh": "技能教學",         "en": "Skill Teaching"},
    "s010": {"category": "education", "zh": "表演教練",         "en": "Performance Coaching"},
    "s011": {"category": "education", "zh": "音樂學習",         "en": "Music Learning"},
    "s012": {"category": "education", "zh": "視覺創作課程",     "en": "Visual Creation Courses"},
    "s013": {"category": "education", "zh": "語言與翻譯",       "en": "Language & Translation"},
    "s014": {"category": "education", "zh": "心理／自我提升",   "en": "Psychology / Self-improvement"},
    # arts
    "s015": {"category": "arts", "zh": "平面設計",     "en": "Graphic Design"},
    "s016": {"category": "arts", "zh": "服飾設計",     "en": "Fashion Design"},
    "s017": {"category": "arts", "zh": "手作工藝",     "en": "Handcraft"},
    "s018": {"category": "arts", "zh": "配件設計",     "en": "Accessory Design"},
    "s019": {"category": "arts", "zh": "攝影與影像",   "en": "Photography & Image"},
    "s020": {"category": "arts", "zh": "印刷與工藝",   "en": "Printing & Craft"},
    "s021": {"category": "arts", "zh": "藝術裝置",     "en": "Art Installation"},
    "s022": {"category": "arts", "zh": "繪畫與素描",   "en": "Drawing & Sketch"},
    # performance
    "s023": {"category": "performance", "zh": "音樂演出",       "en": "Music Performance"},
    "s024": {"category": "performance", "zh": "舞蹈表演",       "en": "Dance Performance"},
    "s025": {"category": "performance", "zh": "戲劇與短劇",     "en": "Theatre & Skits"},
    "s026": {"category": "performance", "zh": "魔術與奇技",     "en": "Magic & Stunts"},
    "s027": {"category": "performance", "zh": "特技與雜耍",     "en": "Acrobatics & Juggling"},
    "s028": {"category": "performance", "zh": "互動娛樂",       "en": "Interactive Entertainment"},
    # food
    "s029": {"category": "food", "zh": "烘焙",           "en": "Baking"},
    "s030": {"category": "food", "zh": "餐飲教學",       "en": "Cooking Education"},
    "s031": {"category": "food", "zh": "飲品與品味",     "en": "Drinks & Tasting"},
    "s032": {"category": "food", "zh": "食物創作",       "en": "Food Creation"},
    "s033": {"category": "food", "zh": "香氛與感官",     "en": "Fragrance & Sensory"},
    "s034": {"category": "food", "zh": "園藝與種植",     "en": "Gardening & Planting"},
    "s035": {"category": "food", "zh": "飲食品牌",       "en": "Food Brand"},
    # wedding
    "s036": {"category": "wedding", "zh": "婚禮策劃",         "en": "Wedding Planning"},
    "s037": {"category": "wedding", "zh": "婚禮設計",         "en": "Wedding Design"},
    "s038": {"category": "wedding", "zh": "婚禮造型",         "en": "Wedding Styling"},
    "s039": {"category": "wedding", "zh": "婚禮甜點",         "en": "Wedding Desserts"},
    "s040": {"category": "wedding", "zh": "親子活動",         "en": "Parent-child Activities"},
    "s041": {"category": "wedding", "zh": "日常生活美學",     "en": "Daily Life Aesthetics"},
    "s042": {"category": "wedding", "zh": "節慶與禮品",       "en": "Festivals & Gifts"},
    # beauty
    "s043": {"category": "beauty", "zh": "化妝",             "en": "Makeup"},
    "s044": {"category": "beauty", "zh": "護膚",             "en": "Skincare"},
    "s045": {"category": "beauty", "zh": "造型與形象",       "en": "Styling & Image"},
    "s046": {"category": "beauty", "zh": "美感內容",         "en": "Aesthetic Content"},
    "s047": {"category": "beauty", "zh": "個人品牌形象",     "en": "Personal Brand Image"},
    "s048": {"category": "beauty", "zh": "美容服務",         "en": "Beauty Services"},
    # community
    "s049": {"category": "community", "zh": "親子教育",       "en": "Parent-child Education"},
    "s050": {"category": "community", "zh": "兒童活動",       "en": "Children's Activities"},
    "s051": {"category": "community", "zh": "社區組織",       "en": "Community Organization"},
    "s052": {"category": "community", "zh": "公共參與",       "en": "Public Participation"},
    "s053": {"category": "community", "zh": "社交配對",       "en": "Social Matching"},
    "s054": {"category": "community", "zh": "公眾講座",       "en": "Public Lectures"},
    # new additions
    "s055": {"category": "education", "zh": "AI學習",           "en": "AI Learning"},
    "s056": {"category": "arts",      "zh": "COSPLAY教學",     "en": "Cosplay Teaching"},
    "s057": {"category": "commercial", "zh": "風水命理",       "en": "Feng Shui & Divination"},
    "s058": {"category": "performance", "zh": "極限運動",      "en": "Extreme Sports"},
    "s059": {"category": "performance", "zh": "小丑/氣球藝術", "en": "Clown & Balloon Art"},
    "s060": {"category": "arts",      "zh": "珠寶設計教學",   "en": "Jewellery Design"},
    "s061": {"category": "community", "zh": "寵物/動物溝通",   "en": "Pets & Animal Communication"},
    "s062": {"category": "education", "zh": "音響設備及教學", "en": "Audio Equipment & Teaching"},
    "s063": {"category": "commercial", "zh": "汽車維修及裝置", "en": "Car Repair & Installation"},
    "s064": {"category": "food", "zh": "燒賣腸粉關注組", "en": "Siu Mai & Cheong Fun Focus"},
    # ── s065-071 (2026-08-14 additions, full 71-sub site taxonomy) ──
    "s065": {"category": "education", "zh": "身心靈提升", "en": "Mind Body & Spirit"},
    "s066": {"category": "arts",      "zh": "手錶設計及維修", "en": "Watch Design & Repair"},
    "s067": {"category": "arts",      "zh": "動漫及動畫", "en": "Anime & Animation"},
    "s068": {"category": "community", "zh": "玩具(四驅車,陀螺)", "en": "Toys (Mini-4WD & Beyblade)"},
    "s069": {"category": "wedding",   "zh": "生活小配件", "en": "Lifestyle Accessories"},
    "s070": {"category": "education", "zh": "體育運動教學", "en": "Sports & Coaching"},
    "s071": {"category": "performance", "zh": "ASMR音效", "en": "ASMR Sound Effects"},
    "s075": {"category": "performance", "zh": "空間/打卡場地", "en": "HK Spaces & Photo Spots"},
    "s076": {"category": "arts", "zh": "Roblox Studio 遊戲製作", "en": "Roblox Studio Game Making"},
}

# ── 18 Districts of Hong Kong ──────────────────────────────────────────
HK_DISTRICTS = [
    "中西區", "東區", "南區", "灣仔區",
    "九龍城區", "觀塘區", "深水埗區", "黃大仙區", "油尖旺區",
    "離島區", "葵青區", "北區", "西貢區", "沙田區", "大埔區",
    "荃灣區", "屯門區", "元朗區",
]

# English aliases for search queries
DISTRICT_ALIASES = {
    "中西區": ["Central & Western", "Central and Western", "中環", "上環", "西環"],
    "東區": ["Eastern District", "筲箕灣", "柴灣", "北角", "太古", "西灣河"],
    "南區": ["Southern District", "香港仔", "鴨脷洲", "薄扶林"],
    "灣仔區": ["Wan Chai", "銅鑼灣", "跑馬地"],
    "九龍城區": ["Kowloon City", "九龍塘", "何文田", "紅磡"],
    "觀塘區": ["Kwun Tong", "牛頭角", "藍田", "油塘", "官塘"],
    "深水埗區": ["Sham Shui Po", "長沙灣", "石硤尾"],
    "黃大仙區": ["Wong Tai Sin", "鑽石山", "慈雲山", "樂富"],
    "油尖旺區": ["Yau Tsim Mong", "旺角", "尖沙咀", "太子", "油麻地"],
    "離島區": ["Islands District", "東涌", "大嶼山", "長洲", "南丫島"],
    "葵青區": ["Kwai Tsing", "葵涌", "青衣"],
    "北區": ["North District", "上水", "粉嶺", "沙頭角"],
    "西貢區": ["Sai Kung", "將軍澳", "坑口"],
    "沙田區": ["Sha Tin", "馬鞍山", "大圍", "火炭"],
    "大埔區": ["Tai Po", "太和"],
    "荃灣區": ["Tsuen Wan", "荃景圍"],
    "屯門區": ["Tuen Mun", "屯門碼頭"],
    "元朗區": ["Yuen Long", "天水圍", "錦田", "洪水橋"],
}

# District name/alias check for post-filtering YouTube results.
# A video only counts for a district if its title/description/author
# actually mentions the district or one of its sub-district aliases.
DISTRICT_KEYWORDS = {
    "中西區": ["中西區", "中環", "上環", "西環", "central", "sheung wan", "sai ying pun"],
    "東區": ["東區", "筲箕灣", "柴灣", "北角", "太古", "西灣河", "shau kei wan", "chai wan", "north point"],
    "南區": ["南區", "香港仔", "鴨脷洲", "薄扶林", "aberdeen", "ap lei chau"],
    "灣仔區": ["灣仔", "銅鑼灣", "跑馬地", "wan chai", "causeway bay", "happy valley"],
    "九龍城區": ["九龍城", "九龍塘", "何文田", "紅磡", "kowloon city", "kowloon tong", "hung hom"],
    "觀塘區": ["觀塘", "牛頭角", "藍田", "油塘", "官塘", "kwun tong", "ngau tau kok", "lam tin", "yau tong"],
    "深水埗區": ["深水埗", "長沙灣", "石硤尾", "sham shui po", "cheung sha wan", "shek kip mei"],
    "黃大仙區": ["黃大仙", "鑽石山", "慈雲山", "樂富", "wong tai sin", "diamond hill", "tsz wan shan", "lok fu"],
    "油尖旺區": ["油尖旺", "旺角", "尖沙咀", "太子", "油麻地", "mong kok", "tsim sha tsui", "yau ma tei"],
    "離島區": ["離島", "東涌", "大嶼山", "長洲", "南丫島", "tung chung", "lantau", "cheung chau", "lamma"],
    "葵青區": ["葵青", "葵涌", "青衣", "kwai tsing", "kwai chung", "tsing yi"],
    "北區": ["北區", "上水", "粉嶺", "沙頭角", "sheung shui", "fanling", "sha tau kok"],
    "西貢區": ["西貢", "將軍澳", "坑口", "sai kung", "tseung kwan o", "hang hau"],
    "沙田區": ["沙田", "馬鞍山", "大圍", "火炭", "sha tin", "ma on shan", "tai wai", "fo tan"],
    "大埔區": ["大埔", "太和", "tai po", "tai wo"],
    "荃灣區": ["荃灣", "荃景圍", "tsuen wan", "tsuen king circuit"],
    "屯門區": ["屯門", "屯門碼頭", "tuen mun", "tuen mun pier"],
    "元朗區": ["元朗", "天水圍", "錦田", "洪水橋", "yuen long", "tin shui wai", "kam tin", "hung shui kiu"],
}

# ── Platforms ──────────────────────────────────────────────────────────
# Only YouTube is enabled — other platforms (IG/Threads/Douyin/XHS/Bilibili)
# produce stub records without real district-relevant results (no API keys),
# and Bilibili has ~1% district match rate with politics/sex contamination.
# Re-enable a platform only after real search APIs are configured.
PLATFORMS = {
    "youtube":     {"name_zh": "YouTube",     "enabled": True, "rate_per_min": 10},
    "instagram":   {"name_zh": "Instagram",   "enabled": False, "rate_per_min": 5},
    "douyin":      {"name_zh": "抖音/TikTok",  "enabled": False, "rate_per_min": 5},
    "threads":     {"name_zh": "Threads",     "enabled": False, "rate_per_min": 10},
    "xiaohongshu": {"name_zh": "小紅書",       "enabled": False, "rate_per_min": 5},
    "bilibili":    {"name_zh": "Bilibili",    "enabled": False, "rate_per_min": 30},
}

# ── Cron ───────────────────────────────────────────────────────────────
CRON_SCHEDULE = "0 */6 * * *"   # every 6 hours
MAX_RESULTS_PER_PLATFORM = 10   # top results per (sub_cat × district × platform)

# ── Intent-based Search Keywords ───────────────────────────────────────
# Real-world search terms people use when looking for services/teachers.
# Each sub_category gets terms that find actual teaching/demo/portfolio content.
# The crawler cycles through these randomly, 2 per run, to discover quality content.
INTENT_KEYWORDS = {
    # ── commercial ──
    "s001": ["市場研究 分析 報告", "market research report", "市調 分析"],
    "s002": ["品牌推廣 案例", "brand promotion case", "品牌行銷 策略"],
    "s003": ["網上生意 教學", "online business tutorial", "電商 教學"],
    "s004": ["專業顧問 服務", "consulting service", "顧問 分享"],
    "s005": ["室內設計 作品", "interior design portfolio", "室內設計 案例"],
    "s006": ["醫療服務 介紹", "medical service", "醫生 分享 健康"],
    "s007": ["餐飲 創業 教學", "F&B business", "餐飲 經營 分享"],
    "s008": ["活動 策劃 教學", "event planning", "活動 配對 分享",
             "電腦通訊節 2026", "會展 展覽 活動"],
    # ── education ──
    "s009": ["技能 教學 示範", "skill teaching demo", "教練 訓練 課程", "tutorial lesson coaching"],
    "s010": ["表演 教練 課程", "performance coaching", "演技 訓練 教學"],
    "s011": ["小提琴 老師 教學", "violin teacher lesson", "鋼琴 老師 教學", "樂器 課程 導師"],
    "s012": ["視覺創作 課程", "visual art course", "繪畫 教學 課程"],
    "s013": ["語言 教學 課程", "language teacher", "英文 補習 教學"],
    "s014": ["心理 輔導 分享", "psychology self improvement", "自我提升 教學"],
    # ── arts ──
    "s015": ["平面設計 教學", "graphic design tutorial", "設計 作品 portfolio"],
    "s016": ["服飾設計 作品", "fashion design portfolio", "時裝 設計 教學"],
    "s017": ["手作 教學  DIY", "handcraft tutorial", "手工 教學 示範"],
    "s018": ["配件設計 作品", "accessory design", "首飾 設計 教學"],
    "s019": ["攝影 教學 技巧", "photography tutorial", "攝影 作品 示範"],
    "s020": ["印刷 工藝 教學", "printing craft", "印刷 設計 教學"],
    "s021": ["藝術裝置 作品", "art installation", "藝術 展覽 分享"],
    "s022": ["繪畫 教學 示範", "drawing tutorial", "素描 教學 課程"],
    # ── performance ──
    "s023": ["音樂演出 教學", "music performance lesson", "樂器 演奏 示範"],
    "s024": ["舞蹈 教學 課程", "dance lesson tutorial", "舞蹈 排練 示範"],
    "s025": ["戲劇 教學 訓練", "theatre training", "短劇 表演 示範"],
    "s026": ["魔術 教學 示範", "magic tutorial", "魔術 表演 教學"],
    "s027": ["特技 教學 訓練", "acrobatics training", "雜耍 教學 示範"],
    "s028": ["互動娛樂 教學", "interactive entertainment", "娛樂 表演 示範"],
    # ── food ──
    "s029": ["烘焙 教學 食譜", "baking tutorial", "蛋糕 製作 教學"],
    "s030": ["烹飪 教學 課程", "cooking class", "廚藝 教學 示範",
             "冷水杯麵 食譜", "日式 即食 杯麵 開箱"],
    "s031": ["飲品 調製 教學", "drink recipe tutorial", "咖啡 教學 拉花"],
    "s032": ["食物 創作 教學", "food creation", "美食 製作 示範",
             "冷水杯麵 開箱 食譜", "零食 開箱 食評"],
    "s033": ["香氛 製作 教學", "fragrance DIY", "香水 教學 示範"],
    "s034": ["園藝 教學 種植", "gardening tutorial", "種植 教學 示範"],
    "s035": ["飲食品牌 介紹", "food brand story", "餐飲 品牌 案例"],
    # ── wedding ──
    "s036": ["婚禮策劃 作品", "wedding planning portfolio", "婚禮 統籌 教學"],
    "s037": ["婚禮設計 作品", "wedding design portfolio", "婚禮 佈置 教學"],
    "s038": ["婚禮造型 教學", "wedding styling", "新娘 化妝 教學"],
    "s039": ["婚禮甜點 作品", "wedding dessert", "結婚 蛋糕 教學"],
    "s040": ["親子活動 教學", "parent child activity", "親子 遊戲 教學"],
    "s041": ["生活美學 教學", "lifestyle aesthetics", "生活 品味 分享"],
    "s042": ["節慶 禮品 DIY", "festival gift DIY", "禮物 製作 教學"],
    # ── beauty ──
    "s043": ["化妝 教學 示範", "makeup tutorial", "化妝 技巧 教學"],
    "s044": ["護膚 教學 技巧", "skincare routine", "護膚 產品 分享"],
    "s045": ["造型 穿搭 教學", "styling tutorial", "形象 設計 教學"],
    "s046": ["美感 內容 分享", "aesthetic content", "美學 生活 分享"],
    "s047": ["個人品牌 教學", "personal branding", "品牌 形象 建立"],
    "s048": ["美容服務 介紹", "beauty service", "美容 療程 分享"],
    # ── community ──
    "s049": ["親子教育 教學", "parenting education", "育兒 教學 分享"],
    "s050": ["兒童活動 教學", "children activity", "小朋友 興趣班 教學"],
    "s051": ["社區組織 活動", "community organization", "社區 活動 分享"],
    "s052": ["公共參與 活動", "public participation", "社區 參與 講座"],
    "s053": ["社交配對 活動", "social matching", "交友 活動 分享"],
    "s054": ["公眾講座 分享", "public lecture", "講座 教學 分享"],
    # ── newer sub-categories ──
    "s055": ["AI學習 香港", "人工智能 教學", "DeepSeek V4 Pro 教學", "AI 工具 應用 教學"],
    "s056": ["COSPLAY教學", "角色扮演 教學"],
    "s057": ["風水命理", "風水 師傅"],
    "s058": ["重氧運動", "HYROX", "功能性訓練"],
    "s059": ["小丑 表演", "氣球藝術"],
    "s060": ["珠寶設計教學", "首飾設計"],
    "s061": ["寵物溝通", "動物傳心"],
    # ── s062-064 (2026-08-10 additions) ──
    "s062": ["音響 教學 器材", "hifi 音響 分享", "喇叭 耳機 評測", "音響 課程 導師",
             "香港高級視聽展 2026", "音響展 現場"],
    "s063": ["汽車維修 教學", "汽車保養 示範", "汽車改裝 教學", "車房 維修 分享"],
    "s064": ["燒賣 關注組", "腸粉 關注組", "燒賣 掃街 食評", "腸粉 製作 教學"],
    # ── s065-071 (2026-08-14 additions) ──
    "s065": ["身心靈 課程 香港", "冥想 教學", "靈性 成長 分享", "禪修 工作坊"],
    "s066": ["手錶 維修 教學", "腕錶 保養 師傅", "鐘錶 維修 分享", "手錶 改裝 教學"],
    "s067": ["動漫 介紹 香港", "動畫 製作 教學", "動漫 周邊 開箱", "配音 動畫 分享"],
    "s068": ["四驅車 教學", "陀螺 對戰 教學", "玩具 開箱 分享", "模型 製作 教學"],
    "s069": ["生活小配件 開箱", "實用 小物 香港", "生活 好物 介紹", "配件 收納 教學"],
    "s070": ["體育 訓練 教學 香港", "健身 教練 課程", "運動 教學 示範", "球類 訓練 教學"],
    "s071": ["ASMR 音效", "ASMR 製作 教學", "舒壓 音效 分享"],
    "s075": ["香港 打卡 場地", "特色空間 開箱", "空間 導覽 香港", "場地 介紹 攻略", "香港 景點 打卡位"],
    "s076": ["Roblox Studio 教學", "Roblox 遊戲製作", "Roblox 遊戲開發", "Roblox Studio 遊戲", "Roblox 製作 教程"],
}

# Quality signals — if title/description contains these, content likely shows real standard
QUALITY_SIGNALS = [
    "教學", "示範", "課程", "導師", "教練", "老師", "訓練",
    "作品", "portfolio", "案例", "分享", "tutorial", "lesson",
    "class", "demo", "coach", "teacher", "course", "training",
    "tips", "技巧", "方法", "入門", "進階", "初學",
]

# Food-review sub-categories whose "quality" is a review/tasting/showcase rather
# than a tutorial. For these we allow an additional food-content signal so that
# local HK restaurant reviews / street-food tours / 探店 actually pass the bar
# (previously they all scored LOW because QUALITY_SIGNALS is teaching-focused).
FOOD_SUBCATEGORIES = {"s007", "s030", "s031", "s032", "s035"}
FOOD_SIGNALS = [
    "食評", "探店", "美食", "吃貨", "飲食", "餐廳", "食記",
    "review", "食咩", "食乜", "推薦", "攻略", "抵食", "好食",
    "菜單", "品嚐", "tasting", "food tour", "foodie",
]

# Content blocklist — remove politics, sex, and inappropriate content
CONTENT_BLOCKLIST = [
    # Politics / sensitive
    "暴乱", "香港暴乱", "政治", "抗议", "示威",
    "六四", "天安门事件", "天安门广场", "Tiananmen", "平反六四",
    "香港独立", "港独", "台独", "台湾独立", "藏独", "疆独",
    "法轮功", "Falun Gong",
    "占中", "反送中", "雨伞运动", "光复", "光復",
    "西藏独立", "新疆独立", "东突厥斯坦",
    "革命", "推翻中共", "独裁", "民运", "反华",
    "白纸运动", "自由花", "镇压", "屠城", "集中营",
    "武汉肺炎", "新冠源头中国", "中必输",
    # Politics: HK / TW / CN figures, institutions, elections, protests (high-precision)
    "李家超", "特首", "行政长官", "施政报告", "立法会", "区议会", "选委",
    "两会", "人大", "政协", "港区国安法", "国安法", "一国两制", "基本法",
    "中联办", "港澳办", "庆回归", "爱国者治港", "公民科",
    "陈玉珍", "民进党", "立法院", "赖清德", "蔡英文", "柯文哲", "侯友宜", "台湾政治",
    "离岛建设条例", "统战", "立委", "选罢法",
    "区议员", "区议员抗議", "议员抗议", "请愿", "集会", "罢工", "绝食",
    "新疆集中营", "维吾尔", "世维", "天安门", "反送中", "占中",
    # Politics: English unambiguous
    "carrie lam", "john lee", "legislative council", "legco", "vote tomorrow",
    "chief executive visit", "protests continue", "hongkongers rally", "national security program",
    # Unsuitable: crime / trafficking / fear content (esp. children's categories)
    "人贩子", "拐卖", "贩卖人口", "失踪男孩", "虐童", "儿童色情",
    # ... traditional-Chinese variants (HK search returns traditional)
    "人販子", "拐賣", "販賣人口", "失蹤男孩", "虐童", "兒童色情",
    "區議員", "立法會", "區議會", "選舉", "政黨", "特首", "行政長官", "施政報告",
    "李家超", "陳玉珍", "民進黨", "立法院", "賴清德", "蔡英文", "柯文哲", "侯友宜",
    "一國兩制", "基本法", "港區國安法", "國安法", "愛國者治港", "中聯辦", "港澳辦", "慶回歸",
    "抗議", "示威", "遊行", "請願", "集會", "絕食", "佔中", "反送中",
    "兩會", "人大", "政協", "天安門", "六四", "法輪功", "新疆", "維吾爾", "世維", "集中營",
    "台湾政治", "台灣政治", "統戰", "台獨",
    # Sex / adult (avoid broad matches like "AV" which hits "have", "travel", etc.)
    "自慰", "手淫", "性爱", "做爱", "色情", "A片", "黄片", "成人内容",
    "站街", "嫖娼", "卖淫", "扫黄",
    "性侵", "强奸", "裸聊", "约炮", "炮友", "援交", "一夜情",
    "嫩模", "三级", "裸体", "全裸", "艳照", "偷拍", "露点", "探花",
    "限制级电影", "成人电影",
    "性交", "口交", "肛交", "性行为",
    "淫秽", "淫荡", "SM", "调教捆绑", "制服诱惑", "包养", "出台",
    "福利姬", "私拍", "私房照", "大尺度", "露骨", "黄播", "色播",
    "nude", "naked", "fuck", "shit", "porn", "sex", "erotic", "erotica",
    "milf", "horny", "boobs", "blowjob", "bdsm",
    "阴道", "阴茎", "生殖器", "精液", "射精", "勃起", "奶子",
    # Garbage / spam
    "暗访一条街", "异性交流圈",
    # Web-dramas / 短劇 (clear drama markers only — NOT part-numbers, which appear in legit tutorials)
    "短劇", "短剧", "爽剧", "免费短剧", "逆袭", "赘婿", "战神归来",
    "修仙小说", "都市修仙", "玄幻小说", "穿越重生", "穿越之", "穿越回", "穿越到",
    "三炷香", "時空門", "时空之门",
    # Celebrity gossip / tabloid (specific named-gossip channels, not generic 八卦)
    "李泳漢", "李泳汉", "施明", "娛樂新聞", "藝人動態", "明星動態", "狗仔隊",
    # Violent / disturbing
    "杀人", "碎尸",
]

# ── Optional: thingerz.com API push ────────────────────────────────────
THINGERZ_API_URL: Optional[str] = os.getenv("THINGERZ_API_URL")
THINGERZ_API_KEY: Optional[str] = os.getenv("THINGERZ_API_KEY")

# ── Logging ────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")