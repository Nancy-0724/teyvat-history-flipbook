# V0.7 → V0.8 歷史書籤遷移說明

因第一章舊稿同時涵蓋原初之人、四執政、第一次王座戰爭、人類文明和三界，此次去重須移動舊內容，但原讀者仍應在續讀時找到合理的歷史主題位置。

## 實作方式

- **保留既有瀏覽器儲存鍵**：`teyvat-reader-position-v03`，不清除已記錄的讀者進度。
- 保留所有 60 個 `chapter` ID；第一、二章能保留的原有小節錨點仍使用原 ID。
- 新增 `data/bookmark-migrations-v07.json`，記錄 **481 個原 V0.7 區塊 ID**及**67 個歷史小節 ID**。`tools/build.py` 產生 `js/bookmark-migrations.js`，`js/app.js` 先嘗試原始區塊 ID，若已改寫或移動則查區塊或小節轉向；最後才回退目標章首。
- 舊式網址片段 `#ch01-phanes` 等也能導向新版的正確章節；`#chapter-3` 原有章首跳轉維持。新的章內定點仍採固定小節錨點，不應以動態實體頁碼作永久連結。
- 已移至未完成章節的歷史主題（如四執政→第四章，人類創造→第五章，三界→第五十六章）會**暫時導向該章的綱要**；等該章完成正文後，可在保留既有轉向資料下再提升精度。

## 代表性去重轉向

| 舊錨點 | 新位置 | 原因 |
|---|---|---|
| `ch01-primordial-sea` | `ch01-primordial-sea` | 生命起源仍在第一章 |
| `ch01-progenitor-dragon` | `ch02-nibelung` | 尼伯龍根與古龍王權屬第二章 |
| `ch01-phanes` / `ch01-world-barrier` | `ch03-arrival` | 高天王座降臨屬第三章 |
| `ch01-first-war` | `ch03-first-throne-war` | 第一次王座戰爭完整收束於第三章 |
| `ch01-authority-transfer` | `ch03-elemental-authority` | 元素大權變更屬第三章 |
| `ch01-naberius` / `ch01-ronova` | `ch04-outline` | 四執政人物傳記留給第四章 |
| `ch01-humanity` | `ch05-outline` | 人類創造留給第五章 |
| `ch01-realms` | `ch56-outline` | 三界體系詳細內容留給第五十六章 |
| `ch02-new-throne` | `ch03-arrival` | 舊第二章最後一節改由第三章敘述 |
| `ch02-moon-response` | `ch03-moon-witnesses` | 三月對外來者態度統一於第三章 |

## 注意事項

V0.8 遷移的是**原閱讀位置所屬的歷史主題**，不是承諾逐字逐段定位在同一行。段落改寫、分章與不同螢幕分頁後，對於同一事件只能盡量回到所屬小節；移往 `outline` 的內容將先回到該章綱要。僅能記錄頁碼而沒有章節或區塊 ID 的早期進度，不能推測其確切跨版本位置。

請不要刪除 `data/bookmark-migrations-v07.json`，也不要手工修改生成檔 `js/bookmark-migrations.js`。往後章節挪移時應持續保留此歷史表並新增新轉向資料。
