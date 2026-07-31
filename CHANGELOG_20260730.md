# Thingerz Crawler — 改動記錄 (2026-07-30)

> 此文件記錄咗 crawler 嘅改動，俾 OpenCode 了解變更內容。

---

## 改動背景

原本 crawler 嘅搜尋方式係 `"{子分類名稱} {地區} 香港"`，例如 `"音樂學習 大埔區 香港"`。呢個 query 太闊，會搵到大量 generic 內容（純音樂分享、學生練習片），而唔係真正展示「服務/教學水平」嘅影片。

**目標：** 令 crawler 搵到真正展示「Standard」嘅內容 — 即係教學示範、作品展示、課程片段、導師 portfolio 等，令用戶可以睇片核實服務質素。

---

## 改動 1: `config.py` — 新增 INTENT_KEYWORDS

**位置：** `config.py` 第 155 行起

**新增內容：**
- `INTENT_KEYWORDS` — 每個 sub_category 對應嘅真實搜尋詞列表（2-4 個）
- `QUALITY_SIGNALS` — 品質訊號 keyword list，用嚟判斷內容係咪教學/示範類

**例子：**
```python
# 以前：只搜 "音樂學習 大埔區 香港"
# 而家加上：
"s011": ["小提琴 老師 教學", "violin teacher lesson",
         "鋼琴 老師 教學", "樂器 課程 導師"]
```

**所有 54 個 sub_category 都有對應嘅搜尋詞**，包括中英文：
- 商業類 → `"品牌推廣 案例"`, `"室內設計 作品"`, `"consulting service"`
- 教育類 → `"小提琴 老師 教學"`, `"violin teacher lesson"`, `"教練 訓練 課程"`
- 興趣類 → `"烘焙 教學 食譜"`, `"舞蹈 教學 課程"`, `"makeup tutorial"`
- 社區類 → `"親子教育 教學"`, `"兒童活動 教學"`, `"社區 活動 分享"`

---

## 改動 2: `main.py` — 更新 `build_queries()`

**位置：** `main.py` 第 42 行起

**改動內容：**
- 每次 run 隨機抽 2 個 intent keyword 加入搜尋
- 每個 keyword 生成 2 種 query 組合：`"{keyword} {地區} 香港"` + `"{地區} {keyword}"`
- 中英文地區名都支援
- 每次 run 抽唔同 keyword，確保隨時間覆蓋晒所有搜尋詞

**以前：**
```
音樂學習 大埔區 香港      ← 太闊
音樂學習 大埔區
音樂學習 Tai Po Hong Kong
```

**而家（每次 run 隨機抽 2 個）：**
```
音樂學習 大埔區 香港
小提琴 老師 教學 大埔區 香港    ← 新增：精準 intent
大埔區 小提琴 老師 教學          ← 新增：地區行先
音樂學習 Tai Po Hong Kong
violin teacher lesson Tai Po     ← 新增：英文 intent
```

---

## 改動 3: `main.py` — 新增 `compute_quality_score()`

**位置：** `main.py` 第 87 行起

**改動內容：**
- 新嘅 scoring 機制取代舊嘅 view-count-only scoring
- 每個 item 嘅 score 由以下因素決定：

| 因素 | 影響 | 原因 |
|------|------|------|
| 品質訊號命中數 | +0.08/個 (上限+0.4) | 標題/描述有「教學、示範、課程、tutorial」等字眼 |
| 觀看次數 | +0~0.15 | 多人睇嘅內容通常質素較高 |
| 片長 < 30秒 | -0.1 | Shorts/Reels 通常冇教學價值 |
| 片長 > 5分鐘 | +0.05 | 長片更可能係完整教學 |
| 高觀看 + 0讚好 | -0.05 | 可疑低質素 |

**以前：** score = view_count / 100000 (cap 1.0)
**而家：** score = baseline(0.3) + quality_signal_boost + view_boost + duration_adjustment

---

## 點樣運作

1. **Cron 1 每 6 小時 run 一次**
2. 每次 run 會隨機抽 2 個 intent keyword per sub_category
3. 加埋原本嘅 generic query，每個 sub_category × district 組合有 6-10 個 query
4. 結果用 `compute_quality_score()` 評分
5. 高分內容（教學示範類）會優先顯示
6. 下次 run 會抽另一組 keyword，逐步覆蓋所有搜尋詞

---

## 測試方法

```bash
cd /opt/data/thingerz-crawler

# Dry run — 睇吓而家會搜咩 query
python3 main.py --dry-run

# 完整 crawl
python3 main.py

# 睇 stats
python3 main.py --stats
```

---

## API 整合 (2026-07-30)

Crawler 收集咗 **28,468 條內容**（33/54 子分類），但 thingerz.com 未有 API endpoint 接收。

**API Spec:** `/opt/data/thingerz-crawler/API_SPEC.md`
- Endpoint: `POST /api/content`
- Auth: `X-API-Key` header
- Payload: JSON array of content items
- Full taxonomy reference included

**Exported Data:**
- `data/full_export.json` — 28,468 items (29.5MB)
- `data/sample_export.json` — 100 items sample

**To enable push:**
```bash
export THINGERZ_API_URL=https://thingerz.com/api/content
export THINGERZ_API_KEY=your_key
python3 main.py --push
```