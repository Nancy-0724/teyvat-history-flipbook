# V0.7 驗證紀錄

日期：2026-10-27。維持前兩章已核定正文，更新圖片事件、圖說與圖片圖位。

## 驗證完成

- `python tools/build.py`：8 篇、60 章、766 個區塊、25 張引用 SVG；`draft=2`、`outline=58`、`reviewed=0`。
- `python tools/validate.py`：60 章、固定錨點、15 組遊戲素材映射及 25 張存在的 SVG 均通過。
- `python tools/prepare_site.py`：產生可供部署的 `_site`。
- JavaScript `node --check`：`js/app.js`、`js/game-media.js`、`js/game-media-data.js` 通過。
- 前兩章 Markdown 與 V0.6 比對：除新增七張圖片與四執政既有圖片序號調整之外，其餘所有非圖片正文行原樣保留。
- SVG XML：第一章 14、第二章 11 張全部解析成功。
- Chromium 隔離測試（真實 HTML/CSS/JS 透過 setContent 注入）：桌面 1440×900 CSS 備援 212 頁、手機 390×844 CSS 備援 237 頁；點圖開啟及關閉後，當前頁和本機閱讀位置保持不變，放大視窗關閉時焦點回到原圖片。
- StPageFlip 模擬事件測試（非真正 3D 套件）：桌面／手機版 `pointerdown`、`mousedown` 均在圖片捕獲階段中止，未傳入翻頁監聽器；開啟圖片到關閉後，模擬翻頁庫的索引不變。設置 `disableFlipByClick:true`。

## 尚未驗收

- 隔離環境阻擋導覽至本機 `file://` 與 `http://localhost` 網址；未能載入實際 CDN 之 StPageFlip 3D 套件。
- 無法取得第三方遊戲圖片實際檔案；所有 15 組僅包含下載 URL、圖說及 SVG 備援。Windows 客戶端需要執行一次性下載工具；個別站台可能仍需手動另存。
- 未測試使用者本機 Windows／Edge／Chrome 的最終操作、不同瀏覽器跨裝置顯示、實際第三方圖片載入成功率。

提醒：教科書正文仍標記 `draft`，不得將此一程式／圖片層驗證認定為史料校勘完成。
