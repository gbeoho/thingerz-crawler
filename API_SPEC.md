# Thingerz Crawler → API Integration Spec

## Overview

The Thingerz Content Crawler collects videos from 6 platforms (YouTube, Bilibili, Instagram, Douyin, Threads, Xiaohongshu) across 54 sub-categories × 18 HK districts. 

**Current status:** 28,180 items collected in local SQLite, but **not pushed to thingerz.com** because the API endpoint doesn't exist yet.

## What the Crawler Sends

The crawler runs every 6 hours and pushes via `POST` to a configurable endpoint.

### Endpoint

```
POST https://thingerz.com/api/content
```

### Authentication

```
Header: X-API-Key: {api_key}
```

### Request Body

```json
{
  "key": "your_api_key_here",
  "content": [
    {
      "platform": "youtube",
      "platform_id": "dQw4w9WgXcQ",
      "sub_category": "s011",
      "district": "大埔區",
      "title": "小提琴教學 初學者課程 大埔區",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "thumbnail_url": "https://i.ytimg.com/vi/...",
      "author_name": "音樂導師",
      "author_url": "https://www.youtube.com/channel/...",
      "description": "這是一段小提琴教學影片...",
      "view_count": 15000,
      "like_count": 1200,
      "comment_count": 85,
      "duration_sec": 480,
      "published_at": "2026-07-01",
      "score": 0.80,
      "fetched_at": "2026-07-30T12:00:00Z"
    }
  ],
  "updated_at": "2026-07-30T12:00:00Z"
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | Yes | API key for authentication |
| `content` | array | Yes | Array of content items |
| `content[].platform` | string | Yes | One of: `youtube`, `bilibili`, `instagram`, `douyin`, `threads`, `xiaohongshu` |
| `content[].platform_id` | string | Yes | Native ID on the platform (video ID, post ID) |
| `content[].sub_category` | string | Yes | Sub-category ID: `s001` to `s054` |
| `content[].district` | string | Yes | HK district: 中西區, 東區, 南區, 灣仔區, 九龍城區, 觀塘區, 深水埗區, 黃大仙區, 油尖旺區, 離島區, 葵青區, 北區, 西貢區, 沙田區, 大埔區, 荃灣區, 屯門區, 元朗區 |
| `content[].title` | string | Yes | Video/post title |
| `content[].url` | string | Yes | Public URL to the content |
| `content[].thumbnail_url` | string | No | Thumbnail image URL |
| `content[].author_name` | string | Yes | Creator/channel name |
| `content[].author_url` | string | No | Link to author's profile |
| `content[].description` | string | No | Content description (up to 500 chars) |
| `content[].view_count` | integer | No | Number of views |
| `content[].like_count` | integer | No | Number of likes |
| `content[].comment_count` | integer | No | Number of comments |
| `content[].duration_sec` | integer | No | Video duration in seconds |
| `content[].published_at` | string | No | Publish date (ISO format) |
| `content[].score` | float | No | Quality score 0.0-1.0 (higher = better teaching/demo content) |
| `content[].fetched_at` | string | No | When crawler fetched this (ISO format) |
| `updated_at` | string | Yes | Timestamp of this push |

### Expected Response

**Success (200):**
```json
{
  "status": "ok",
  "received": 100,
  "duplicates_skipped": 5,
  "errors": 0
}
```

**Auth Error (401):**
```json
{
  "status": "error",
  "message": "Invalid API key"
}
```

## Deduplication

The crawler uses `(platform, platform_id)` as a unique key. The website should also deduplicate on this combination — if the same video is pushed again (e.g. from a different sub_category query), it should be updated, not duplicated.

## Taxonomy Reference

### 54 Sub-categories (s001-s054)

| ID | 中文 | English | Category |
|----|------|---------|----------|
| s001 | 市場研究與分析 | Market Research | commercial |
| s002 | 品牌推廣 | Brand Promotion | commercial |
| s003 | 網上生意 | Online Business | commercial |
| s004 | 專業顧問 | Professional Consulting | commercial |
| s005 | 室內設計 | Interior Design | commercial |
| s006 | 醫療服務 | Medical Services | commercial |
| s007 | 餐飲與酒類 | Food & Beverage | commercial |
| s008 | 活動與配對 | Events & Matching | commercial |
| s009 | 技能教學 | Skill Teaching | education |
| s010 | 表演教練 | Performance Coaching | education |
| s011 | 音樂學習 | Music Learning | education |
| s012 | 視覺創作課程 | Visual Creation Courses | education |
| s013 | 語言與翻譯 | Language & Translation | education |
| s014 | 心理／自我提升 | Psychology / Self-improvement | education |
| s015 | 平面設計 | Graphic Design | arts |
| s016 | 服飾設計 | Fashion Design | arts |
| s017 | 手作工藝 | Handcraft | arts |
| s018 | 配件設計 | Accessory Design | arts |
| s019 | 攝影與影像 | Photography & Image | arts |
| s020 | 印刷與工藝 | Printing & Craft | arts |
| s021 | 藝術裝置 | Art Installation | arts |
| s022 | 繪畫與素描 | Drawing & Sketch | arts |
| s023 | 音樂演出 | Music Performance | performance |
| s024 | 舞蹈表演 | Dance Performance | performance |
| s025 | 戲劇與短劇 | Theatre & Skits | performance |
| s026 | 魔術與奇技 | Magic & Stunts | performance |
| s027 | 特技與雜耍 | Acrobatics & Juggling | performance |
| s028 | 互動娛樂 | Interactive Entertainment | performance |
| s029 | 烘焙 | Baking | food |
| s030 | 餐飲教學 | Cooking Education | food |
| s031 | 飲品與品味 | Drinks & Tasting | food |
| s032 | 食物創作 | Food Creation | food |
| s033 | 香氛與感官 | Fragrance & Sensory | food |
| s034 | 園藝與種植 | Gardening & Planting | food |
| s035 | 飲食品牌 | Food Brand | food |
| s036 | 婚禮策劃 | Wedding Planning | wedding |
| s037 | 婚禮設計 | Wedding Design | wedding |
| s038 | 婚禮造型 | Wedding Styling | wedding |
| s039 | 婚禮甜點 | Wedding Desserts | wedding |
| s040 | 親子活動 | Parent-child Activities | wedding |
| s041 | 日常生活美學 | Daily Life Aesthetics | wedding |
| s042 | 節慶與禮品 | Festivals & Gifts | wedding |
| s043 | 化妝 | Makeup | beauty |
| s044 | 護膚 | Skincare | beauty |
| s045 | 造型與形象 | Styling & Image | beauty |
| s046 | 美感內容 | Aesthetic Content | beauty |
| s047 | 個人品牌形象 | Personal Brand Image | beauty |
| s048 | 美容服務 | Beauty Services | beauty |
| s049 | 親子教育 | Parent-child Education | community |
| s050 | 兒童活動 | Children's Activities | community |
| s051 | 社區組織 | Community Organization | community |
| s052 | 公共參與 | Public Participation | community |
| s053 | 社交配對 | Social Matching | community |
| s054 | 公眾講座 | Public Lectures | community |

### 8 Categories

| Category | Track | Sub-categories |
|----------|-------|----------------|
| commercial | learning | s001-s008 |
| education | learning | s009-s014 |
| arts | fun | s015-s022 |
| performance | fun | s023-s028 |
| food | fun | s029-s035 |
| wedding | learning | s036-s042 |
| beauty | fun | s043-s048 |
| community | learning | s049-s054 |

### 2 Tracks

| Track | 中文 | Categories |
|-------|------|------------|
| fun | 娛樂·興趣 | arts, performance, food, beauty |
| learning | 學習·行業 | commercial, education, wedding, community |

### 18 HK Districts

中西區, 東區, 南區, 灣仔區, 九龍城區, 觀塘區, 深水埗區, 黃大仙區, 油尖旺區, 離島區, 葵青區, 北區, 西貢區, 沙田區, 大埔區, 荃灣區, 屯門區, 元朗區

## Setup Steps

1. Build the `POST /api/content` endpoint on thingerz.com
2. Generate an API key
3. Set these env vars on the crawler server:
   ```
   THINGERZ_API_URL=https://thingerz.com/api/content
   THINGERZ_API_KEY=your_generated_key
   ```
4. The next crawler run will automatically push data

## Testing

To test the push manually:
```bash
cd /opt/data/thingerz-crawler
THINGERZ_API_URL=https://thingerz.com/api/content THINGERZ_API_KEY=test_key python3 main.py --push
```

## Sample Data Export

A sample of 100 items has been exported to `/opt/data/thingerz-crawler/data/sample_export.json` for reference.