# 圖像配置與來源指南｜V0.12

## 當前狀態

全書 22 組正文配圖、23 個可放大圖像元素；引用 23 個 SVG 路徑，其中 20 個是原創示意／修訂圖、3 個是新來源圖位的文字載入提示卡。不是 23 張官方圖片。第一至第五章配圖組數為 1、11、2、5、3；第五章圖 5-2 內有兩個可獨立放大的面板。

遊戲圖清單共 18 組，16 active、2 staged；其中圖蘭、三月與四影共 3 組固定圖解。本次未成功下載外部圖檔，18 個 local 路徑均未預封裝。線上圖源已寫入閱讀器，但讀者端實際連線及站台允許熱連結與否仍需驗收。

## 第五章來源圖

圖 5-2a 使用官方尼可預告的媒體轉載畫面；5-2b 為 GameWith 收錄的普通仙靈截圖。兩者為族群形態對照，不是尼可個人的前後變化，不新增天使受造年表。圖 5-3 使用《原神》開發團隊在 PlayStation Blog 發布的角色展示圖，不當作古城復原。三張來源圖的 exact URL、來源頁、官方發布入口、權利人與限制見 sources.json。

尼可預告、PlayStation Blog 原圖在本次網頁工具可核看；GameWith 來源頁可讀，但其舊圖檔端點本輪未重新取回。保留前輪候選與其來源，不聲稱所有端點或三張圖均已在讀者端成功載入。

## 載入與來源顯示

先嘗試 local 路徑，再於連網時嘗試遠端來源；只有 Image.onload 成功才標示為來源圖，同步更新 alt、放大圖與來源圖說。失敗時保留原創示意；第五章新增人物／族群圖位則明示「圖片尚未載入」，不以虛構肖像充當官方素材。固定圖解從不自動換成照片。

書頁短圖說由 `data/figure-presentations.json` 定義；備援／來源圖片的短標籤可分開設定，預留兩者高度，不使用 sources.json 的長圖說當書頁標籤。兩圖組只顯示共用圖說，個別圖名保留在 alt、按鈕名稱與放大視窗。

圖號、名稱及必要的簡短形態限定留在頁上；素材權利資訊、來源連結留在放大視窗，長圖說與補充說明預設收合。不在書頁顯示「連網來源」「點圖查看」「不代表……」等逐圖提醒。來源網址與詳細註記仍完整保存在 sources.json 及章節來源中。

## 離線準備

Windows 執行根目錄 `下載第五章配圖_連網後執行.bat` 只處理三張新圖；舊 `下載遊戲素材_第一次連網執行.bat` 仍可處理完整映射。亦可使用：

```bash
python tools/fetch_game_art.py --chapter 5
python tools/fetch_game_art.py --chapter 5 --check
```

成功後儲存至既定 local 路徑，並同步至已存在的 `_site`。重新開啟網站即可讀取，不用改正文。圖檔未取得時回傳非零狀態；各來源的公開存取不等於獲得再散布授權，公開發布前應核對引用條件。Python 工具的下載分支以本地替身測試；真實下載與 Windows PowerShell 尚未驗收。

## 映射表

| ID | 章 | 狀態 | 顯示策略 | 本機來源圖路徑 |
|---|---:|---|---|---|
| `four-shades` | 4 | active | 固定原創圖解 | `assets/game-media/ch01/four-shades.webp` |
| `ronova` | 4 | active | 來源圖／原創備援 | `assets/game-media/ch01/ronova.jpg` |
| `istaroth` | 4 | active | 來源圖／原創備援 | `assets/game-media/ch01/istaroth.jpg` |
| `asmoday` | 4 | active | 來源圖／原創備援 | `assets/game-media/ch01/asmoday.jpg` |
| `apep` | 2 | active | 來源圖／原創備援 | `assets/game-media/ch02/apep.png` |
| `tollan` | 2 | active | 固定原創圖解 | `assets/game-media/ch02/tollan.webp` |
| `kukulkan` | 2 | active | 來源圖／原創備援 | `assets/game-media/ch02/kukulkan.jpg` |
| `three-moons` | 2 | active | 固定原創圖解 | `assets/game-media/ch02/three-moons.jpg` |
| `naberius` | 4 | active | 來源圖／原創備援 | `assets/game-media/ch01/naberius.jpg` |
| `primordial-sea-scene` | 1 | active | 來源圖／原創備援 | `assets/game-media/ch01/primordial-sea.jpg` |
| `enkanomiya-ruins` | 12 | staged | 來源圖／原創備援 | `assets/game-media/ch01/enkanomiya-ruins.jpg` |
| `three-realms-landscape` | 56 | staged | 來源圖／原創備援 | `assets/game-media/ch01/three-realms-landscape.jpg` |
| `xiuhcoatl` | 2 | active | 來源圖／原創備援 | `assets/game-media/ch02/xiuhcoatl.jpg` |
| `secret-source` | 2 | active | 來源圖／原創備援 | `assets/game-media/ch02/secret-source.jpg` |
| `sky-engineering` | 2 | active | 來源圖／原創備援 | `assets/game-media/ch02/sky-engineering.jpg` |
| `angel-example` | 5 | active | 來源圖／缺圖提示卡 | `assets/game-media/ch05/angel-example.jpg` |
| `ordinary-seelie` | 5 | active | 來源圖／缺圖提示卡 | `assets/game-media/ch05/ordinary-seelie.png` |
| `nicole-reeyn` | 5 | active | 來源圖／缺圖提示卡 | `assets/game-media/ch05/nicole-reeyn.jpg` |

## 保留規則

原 15 組的 ID、local 路徑和 URLs 全數保留；本次只新增三組、修正圖 1-1 的替換圖號、固定兩張關係圖並補來源性質。圖 2-6 改引用 `06-dragon-timeline-v011.svg`，原八階段圖保留不覆寫。納貝里士的融合後形象限制與所有史料框架繼續保留。

舊版 19／20 張圖的統計僅見歷史交接與 docs/archive/v010，不適用於本版。最新技術與內容狀態以 V0.12 交接檔為準。V0.12 只改圖說顯示層，原來源映射逐位元組不變。
