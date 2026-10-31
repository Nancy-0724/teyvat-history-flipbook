# 圖像配置與來源指南｜V0.14

## 當前狀態

全書28組正文配圖、29個可放大圖像，引用29個SVG路徑。前七章配圖組數為1、11、2、5、3、3、3；第五章對照組含兩幅。原47個SVG保留，新增3個第七章SVG，資產總計50個。並非29張官方原圖。

來源映射共21組，19 active、2 staged；圖蘭、三月與四影共3組固定圖解。20組舊映射內容不變，新添 `celestial-nail-ch07`。映射使用19個不重複本機來源圖路徑（第六章沿用第二章原圖路徑）。第三方圖檔沒有預封裝，不以有網址取代下載驗收。

## 第七章

圖7-1〈三月的戰後去向〉、圖7-3〈舊秩序的分化〉為原創關係圖，不設定照片替換。圖7-2〈天釘〉使用核定稿的GamesRadar+遊戲截圖來源，供器物辨識；來源與畫面年代限制放於點圖視窗。未下載到截圖時顯示「來源圖片待載入」，而非虛構天釘形象。原候選保存在核定審閱稿。

書頁只保留短圖號與圖名，圖像來源、著作資訊、素材性質及長說明在放大視窗。圖5-2仍只有一行共用圖說；前六章所有短標籤不變。

## 讀取與下載

優先載入local路徑，連網時再嘗試urls；僅圖片載入成功才切換為來源圖。固定圖解不被照片替換。原圖或資料未取得時，不聲稱已封裝或已驗收。

```bash
python tools/fetch_game_art.py --chapter 7
python tools/fetch_game_art.py --chapter 7 --check
```

Windows可用根目錄 `下載第七章配圖_連網後執行.bat`。舊的第五章／完整下載器均保留。成功下載會同步至既有 `_site`；已存在且有效的圖片不會重新下載或刪除。遠端網站可用性、熱連結及再散布條件仍由實際部署環境確認。

## 來源映射表

| ID | 章 | 狀態 | 顯示策略 | 本機路徑 |
|---|---:|---|---|---|
| `four-shades` | 4 | active | 固定圖解 | `assets/game-media/ch01/four-shades.webp` |
| `ronova` | 4 | active | 來源圖／原創示意 | `assets/game-media/ch01/ronova.jpg` |
| `istaroth` | 4 | active | 來源圖／原創示意 | `assets/game-media/ch01/istaroth.jpg` |
| `asmoday` | 4 | active | 來源圖／原創示意 | `assets/game-media/ch01/asmoday.jpg` |
| `apep` | 2 | active | 來源圖／原創示意 | `assets/game-media/ch02/apep.png` |
| `tollan` | 2 | active | 固定圖解 | `assets/game-media/ch02/tollan.webp` |
| `kukulkan` | 2 | active | 來源圖／原創示意 | `assets/game-media/ch02/kukulkan.jpg` |
| `three-moons` | 2 | active | 固定圖解 | `assets/game-media/ch02/three-moons.jpg` |
| `naberius` | 4 | active | 來源圖／原創示意 | `assets/game-media/ch01/naberius.jpg` |
| `primordial-sea-scene` | 1 | active | 來源圖／原創示意 | `assets/game-media/ch01/primordial-sea.jpg` |
| `enkanomiya-ruins` | 12 | staged | 來源圖／原創示意 | `assets/game-media/ch01/enkanomiya-ruins.jpg` |
| `three-realms-landscape` | 56 | staged | 來源圖／原創示意 | `assets/game-media/ch01/three-realms-landscape.jpg` |
| `xiuhcoatl` | 2 | active | 來源圖／原創示意 | `assets/game-media/ch02/xiuhcoatl.jpg` |
| `secret-source` | 2 | active | 來源圖／原創示意 | `assets/game-media/ch02/secret-source.jpg` |
| `sky-engineering` | 2 | active | 來源圖／原創示意 | `assets/game-media/ch02/sky-engineering.jpg` |
| `angel-example` | 5 | active | 來源圖／缺圖提示 | `assets/game-media/ch05/angel-example.jpg` |
| `ordinary-seelie` | 5 | active | 來源圖／缺圖提示 | `assets/game-media/ch05/ordinary-seelie.png` |
| `nicole-reeyn` | 5 | active | 來源圖／缺圖提示 | `assets/game-media/ch05/nicole-reeyn.jpg` |
| `apep-ch06` | 6 | active | 來源圖／原創示意 | `assets/game-media/ch02/apep.png` |
| `three-moons-ch06` | 6 | active | 來源圖／原創示意 | `assets/game-media/ch02/three-moons.jpg` |
| `celestial-nail-ch07` | 7 | active | 來源圖／缺圖提示 | `assets/game-media/ch07/celestial-nail.jpg` |

## 歷史來源

V0.13指南原文另存 `docs/archive/v013/GAME_MEDIA_GUIDE.md`。舊版數量只供追溯；本頁及V0.14交接檔為目前製作狀態。納貝里士融合後形象、尼可人物辨識及天使／仙靈對照的必要限制仍保留在來源資料，未搬回書頁成為長圖說。
