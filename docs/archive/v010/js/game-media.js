/* Game screenshot display layer for V0.9 active mappings (staged entries remain dormant).
   Images are kept as chapter SVG originals unless a real shot loads.
   Local asset is attempted first; while online, official/game-capture source URLs are tried next.
   No remote images are mandatory for reading and images are never embedded as data URIs. */
(function () {
  'use strict';
  const db = window.TEYVAT_GAME_MEDIA || {};
  const seen = new WeakSet();
  const status = Object.create(null);
  const localFirst = (entry) => ['./' + entry.local, ...(navigator.onLine === false ? [] : entry.urls || [])];
  function applyTo(button) {
    if (seen.has(button)) return;
    seen.add(button);
    const info = db[button.dataset.gameId];
    if (!info || info.display === 'diagram') return; // Keep explanatory charts visible.
    const target = button.querySelector('img');
    if (!target) return;
    const fig = button.closest('figure');
    const caption = fig ? fig.querySelector('figcaption') : null;
    const candidates = localFirst(info);
    let index = 0;
    function attempt() {
      if (index >= candidates.length || !button.isConnected) return;
      const source = candidates[index++];
      const probe = new Image();
      probe.onload = () => {
        if (!button.isConnected) return;
        target.src = source;
        target.alt = info.caption;
        button.dataset.src = source;
        button.dataset.caption = info.caption;
        button.setAttribute('aria-label', '檢視圖片：' + info.caption);
        if (caption) caption.textContent = info.caption;
        if (fig) fig.classList.add('game-image-loaded');
        status[info.id] = source;
      };
      probe.onerror = attempt;
      probe.src = source;
    }
    // Figure order/size is preserved: only the loaded picture URL and description change.
    attempt();
  }
  function scan() {
    document.querySelectorAll('.page-figure .zoom-image[data-game-id]:not([data-game-id=""])')
      .forEach(applyTo);
  }
  const watch = () => {
    const frame = document.getElementById('book-frame');
    if (!frame) return;
    // The book node is recreated on responsive resizing; observe its stable parent.
    new MutationObserver(scan).observe(frame, {childList:true, subtree:true});
    scan();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch, {once:true});
  else watch();
})();
