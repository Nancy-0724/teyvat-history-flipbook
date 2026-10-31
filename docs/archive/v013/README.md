# 《提瓦特通史》V0.13

一本書、八篇、六十章。第一至第六章採用已核定的歷史敘事修訂稿，6章正文草稿、54章綱要；未冒稱官方原文終校完成。

## 閱讀與更新

開啟根目錄 `index.html` 可閱讀。已有專案請以更新包覆蓋同名檔案，不先刪除原資料夾；自備或已下載的圖片繼續保留。GitHub 倉庫沿用原來的發布設定，這次未修改 `.github/workflows/pages.yml`，也未代為推送或發布。

## 本版內容

六章核定文字逐段保留，僅轉換網站章頭、圖片與註釋格式。第一至第五章既有圖像及短圖說保留；第六章加入阿佩普、三月女神及葬火之戰轉折三組圖。原44個SVG不變，另新增3個第六章SVG。來源圖沿用舊本機路徑與網址，未新增下載第三方圖檔。

正文的34則註釋可點按小註號查看；章末「本章史料與註釋」亦可開啟全部註目。來源視窗不參與正文分頁，關閉後保留閱讀位置。既有圖片放大與短圖說規則不變。

正文搜尋包含第六章；「妮可／尼可」同義輸入保留。舊閱讀鍵與全部既有轉向保留，另新增改寫段落的同主題小節轉向。

## 建置

```bash
python tools/build.py
python tools/validate.py
python tools/prepare_site.py
```

不手改生成的 `js/generated-content.js`。正文仍是 `content/part-XX/chapter-YY.md`；原文入口來源資料在 `data/chapter-source-index.json`。

既有圖片可繼續沿用。需要下載第六章圖片時，可在連網環境執行 `python tools/fetch_game_art.py --chapter 6`；失敗時仍有示意圖可讀。

## 驗證

三種尺寸共489項嵌入式Chromium檢查通過。測試使用CSS翻頁備援、SVG原檔data URI及記憶體儲存；不是實體手機、Windows直接開檔、真實翻頁CDN或線上部署驗收。細節見 `docs/QA_V013.md`。

最新交接：`docs/提瓦特通史_跨對話編纂交接_V0.13_2026-10-31.md`。核定修訂底稿保存於 `docs/editorial/historical-h1-approved/`。
