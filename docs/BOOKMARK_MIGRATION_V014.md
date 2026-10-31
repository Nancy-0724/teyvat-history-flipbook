# V0.14 舊閱讀位置相容

持久化檔 `data/bookmark-migrations-v07.json` 與儲存鍵 `teyvat-reader-position-v03` 不改名。V0.13的71個小節及669個區塊轉向鍵值逐項保留。

本次新增第七章原綱要五個區塊，全部轉到 `chapterId: 7, sectionId: ch07-outline`。原小節 `7:ch07-todo` 轉向同一位置；`ch07-outline` 直接沿用。新正文沒有重用舊綱要的區塊身分，因此不假裝能回到刪除文字的精確字元位置。

全表現為72個小節／674個區塊轉向。三種尺寸驗證全部轉向可達，新舊第七章URL定位可用。
