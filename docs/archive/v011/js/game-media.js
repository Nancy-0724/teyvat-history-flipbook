/* V0.11: actual-source images + honest fallback, stable captions, per-image provenance.
   Sources are kept in sources.json. This module never replaces fixed relation diagrams.
   An image URL is not a packaged asset; only a successful load changes the source status. */
(function () {
  'use strict';
  const db = window.TEYVAT_GAME_MEDIA || {};
  const seen = new WeakSet();
  const cache = new Map();
  const status = Object.create(null);
  function candidates(info) {
    return [...new Set(['./' + info.local, ...(navigator.onLine === false ? [] : info.urls || [])])];
  }
  function resolve(info) {
    if (cache.has(info.id)) return cache.get(info.id);
    const promise = (async () => {
      for (const url of candidates(info)) {
        const ok = await new Promise(done => {
          const probe = new Image();
          let ended = false;
          const finish = value => { if (ended) return; ended = true; clearTimeout(timer); probe.onload = probe.onerror = null; done(value); };
          const timer = setTimeout(() => finish(false), 6500);
          probe.onload = () => finish(probe.naturalWidth > 0);
          probe.onerror = () => finish(false);
          probe.src = url;
        });
        if (ok) return {url, kind:url.startsWith('./') ? 'local' : 'remote'};
      }
      return null;
    })();
    cache.set(info.id, promise);
    return promise;
  }
  function applyTo(button) {
    if (seen.has(button)) return;
    seen.add(button);
    const info = db[button.dataset.gameId];
    if (!info) return;
    const tile = button.closest('.media-tile') || button.closest('figure');
    const state = tile?.querySelector('.media-state');
    if (info.display === 'diagram') {
      button.dataset.mediaState = 'diagram';
      if (state) state.textContent = '固定圖解 · 點圖查看來源';
      status[info.id] = {state:'diagram'};
      return;
    }
    button.dataset.mediaState = 'fallback';
    resolve(info).then(result => {
      if (!button.isConnected) return;
      const img = button.querySelector('img');
      if (!img) return;
      if (!result) {
        status[info.id] = {state:'unavailable'};
        if (state) state.textContent = info.fallback_only ? '圖片未載入 · 點圖開啟來源' : '原創備援 · 來源圖未載入';
        return;
      }
      img.src = result.url;
      img.alt = info.caption;
      button.dataset.src = result.url;
      button.dataset.caption = info.caption;
      button.dataset.mediaState = result.kind;
      button.setAttribute('aria-label', '檢視圖片：' + info.caption);
      tile.classList.add('game-image-loaded');
      tile.querySelector('.caption-original')?.setAttribute('aria-hidden','true');
      tile.querySelector('.caption-loaded')?.removeAttribute('aria-hidden');
      if (state) state.textContent = result.kind === 'local' ? '本機來源圖 · 點圖查看出處' : '連網來源圖 · 點圖查看出處';
      status[info.id] = {state:result.kind,url:result.url};
    });
  }
  function scan() {
    document.querySelectorAll('#book .zoom-image[data-game-id]:not([data-game-id=""])').forEach(applyTo);
  }
  function watch() {
    const frame = document.getElementById('book-frame');
    if (!frame) return;
    new MutationObserver(scan).observe(frame,{childList:true,subtree:true});
    scan();
  }
  window.addEventListener('online', () => {
    cache.clear();
    document.querySelectorAll('#book .zoom-image[data-game-id]').forEach(button=>seen.delete(button));
    scan();
  });
  window.TEYVAT_MEDIA_STATUS = status;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',watch,{once:true}); else watch();
})();
