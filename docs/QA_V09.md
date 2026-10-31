# V0.9 驗證紀錄｜2026-10-31

## 內容及靜態結構

- 8 篇／60 章；第 1–4 章 draft，其餘 56 章 outline，reviewed=0。
- 460 內容區塊、19 張引用 SVG；第四章 5 張；15 組映射，13 active／2 staged。
- 第四章核定第四版的 17 段正文逐段保留。其他 59 章 Markdown 及舊 SVG 全部與 V0.8 位元組相同。
- 68 節次／486 區塊遷移，保留 V0.7 原 67／481 所有鍵；映射目標均存在。
- build.py、validate.py、prepare_site.py 及 JavaScript 語法檢查通過。

## 瀏覽器測試方法

執行環境對 localhost 與 file 導覽回報管理限制，因此使用隔離 Chromium 的嵌入式真 HTML/CSS/JS。所有 SVG 使用專案原圖的 data URI，儲存使用記憶體夾具；測試副本提供 hook 呼叫正式 `findPage` 與 `jumpTo`，不修改已交付網站來暴露測試 hook。StPageFlip 外部 CDN 停用，實際操作內建 CSS 備援。

桌面 1440×900 與手機 390×844 各完成 15 項檢查，共 30 項通過，無 JS 執行錯誤。當次分頁為 181／197 頁，不是固定頁碼。

檢查全書初始化、目錄搜尋跳章、第四章五圖載入、點擊放大與關閉、可見頁及儲存標記不變、歷史人物節次與待補錨點解析、帶有舊區塊的續讀紀錄解析，以及鍵盤往返翻頁。五圖所在頁的垂直溢出值全部為 0。

在測試中發現雙頁圖片關閉時閱讀標記退到左頁的問題；已修復為分開保存引擎跨頁位置與邏輯閱讀位置，複測通過。

結果：`qa-v09/browser-results.json`；各視窗報告及截圖位於同資料夾。重跑需另安裝 Playwright 並備有 Chromium：`python tools/test_v09_browser.py desktop` 或 `mobile`。

## 本次沒有完成

真實 StPageFlip CDN、第三方圖片下載／成功替換、Windows file://、實際 Android／iOS、多瀏覽器、磁碟 localStorage 持久化及 GitHub Pages 發佈均未驗收。現成來源網址與下載腳本不等於已取得人物圖，生成 _site 不等於上線。
