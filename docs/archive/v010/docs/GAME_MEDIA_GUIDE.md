> V0.10 補充：第五章已啟用既存原創 `assets/illustrations/ch05/01-humanity.svg`，不是新增遊戲圖片映射。原15組映射仍為13 active／2 staged，原local路徑與網址全部保留；沒有封裝第三方圖像。以下原有映射與來源說明仍適用。

# 遊戲圖片與原創插圖配置指南｜V0.9

第四章核定正文已整合。全書引用 19 張 SVG，15 組遊戲來源中 13 active／2 staged。五個第四章圖位分置各節的第一個介紹段落之後，不把生命圖誤當死亡小節插圖。

## 離線與連網行為

本 ZIP 沒有第三方人物／遊戲圖片位元組；第四章五張原創 SVG 均已封裝，可離線閱讀。圖說明確標為概念圖／關係圖，不假裝是官方肖像。

`four-shades` 的 `display: "diagram"` 會讓 `game-media.js` 保留原創四影關係圖，來源網址仍存檔但不自動替換。其他 active 圖先嘗試舊 `local`，連網時再嘗試遠端網址；成功才同時替換圖片、放大來源、替代文字與圖說。失敗不移除原 SVG。

`local` 全部保持 V0.7 原路徑，不能因圖已在第四章便自行改成 ch04 路徑。`placement` 管理正文是否引用，`display` 管理是否保留示意圖，兩者不同。

## 來源表

| ID | 章 | 狀態 | 顯示策略 | SVG 路徑 | 本機人物／遊戲圖路徑 |
|---|---:|---|---|---|---|
| `four-shades` | 4 | active | 固定原創關係圖 | `assets/illustrations/ch04/01-four-shades.svg` | `assets/game-media/ch01/four-shades.webp` |
| `ronova` | 4 | active | 成功時才替換 | `assets/illustrations/ch04/03-ronova.svg` | `assets/game-media/ch01/ronova.jpg` |
| `istaroth` | 4 | active | 成功時才替換 | `assets/illustrations/ch04/04-istaroth.svg` | `assets/game-media/ch01/istaroth.jpg` |
| `asmoday` | 4 | active | 成功時才替換 | `assets/illustrations/ch04/05-asmoday.svg` | `assets/game-media/ch01/asmoday.jpg` |
| `apep` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/07-apep.svg` | `assets/game-media/ch02/apep.png` |
| `tollan` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/02-tollan.svg` | `assets/game-media/ch02/tollan.webp` |
| `kukulkan` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/08-kukulkan.svg` | `assets/game-media/ch02/kukulkan.jpg` |
| `three-moons` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/04-three-moons.svg` | `assets/game-media/ch02/three-moons.jpg` |
| `naberius` | 4 | active | 成功時才替換 | `assets/illustrations/ch04/02-naberius.svg` | `assets/game-media/ch01/naberius.jpg` |
| `primordial-sea-scene` | 1 | active | 成功時才替換 | `assets/illustrations/ch01/12-primordial-sea-scene.svg` | `assets/game-media/ch01/primordial-sea.jpg` |
| `enkanomiya-ruins` | 12 | staged | 成功時才替換 | `assets/illustrations/ch12/01-enkanomiya-scene.svg` | `assets/game-media/ch01/enkanomiya-ruins.jpg` |
| `three-realms-landscape` | 56 | staged | 成功時才替換 | `assets/illustrations/ch56/02-three-realms-scene.svg` | `assets/game-media/ch01/three-realms-landscape.jpg` |
| `xiuhcoatl` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/09-xiuhcoatl.svg` | `assets/game-media/ch02/xiuhcoatl.jpg` |
| `secret-source` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/10-secret-source.svg` | `assets/game-media/ch02/secret-source.jpg` |
| `sky-engineering` | 2 | active | 成功時才替換 | `assets/illustrations/ch02/11-sky-engineering.svg` | `assets/game-media/ch02/sky-engineering.jpg` |

## 歷史與來源限制

納貝里士幕間人物圖必須註明與萊茵多特融合後形象，不能標作遠古單獨肖像。阿斯莫代過場圖屬後世開場，不標作創世戰爭實景。概念圖不是官方人物外觀。

來源清單保留舊版頁面與鏡像；第四章另附官方幕間影片發布入口。本次確認官方發布資料，但外部圖檔未成功下載，不宣稱所有鏡像仍有效，也不使用新搜尋到的玩家推論擴寫正文。

圖片下載工具、來源記錄及舊 SVG 全部保留。若需離線人物圖，可在有網路的環境執行 `python tools/fetch_game_art.py`，或依來源合法另存至指定路徑。公開發佈前仍應核對圖片使用權。

## 建置與檢查

```sh
python tools/build.py
python tools/validate.py
python tools/prepare_site.py
```

`active` 圖必須由正文引用，`staged` 不得已在正文使用。第十二章、第五十六章圖片仍 staged；第五章人類創世原創 SVG 也仍未引用。

詳見 `docs/QA_V09.md`。本次 Chromium 嵌入式 CSS 備援測試通過，不代表第三方圖片或 StPageFlip CDN 已經實機驗收。
