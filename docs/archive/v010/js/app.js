/* 《提瓦特通史》v0.3: fullscreen reading, contents, stable position, relayout. */
(function () {
  'use strict';
  const catalog = window.TEYVAT_BOOK;
  const chapters = window.TEYVAT_CONTENT;
  const renderer = window.TEYVAT_RENDERER;
  if (!catalog || !chapters || !renderer) { console.error('Missing reader, catalog or generated chapter content'); return; }
  const $ = (selector) => document.querySelector(selector);
  const D = {
    home:$('#home'),reader:$('#reader'),book:$('#book'),frame:$('#book-frame'),
    toc:$('#toc-drawer'),tocEntries:$('#toc-chapters'),tocSearch:$('#toc-search'),
    topToc:$('#top-toc'),floatingToc:$('#floating-toc'),current:$('#current-location'),
    pageCount:$('#page-count'),pageMeter:$('#page-meter-fill'),chapterReadout:$('#chapter-readout'),
    next:$('#next-page'),prev:$('#prev-page'),edgeNext:$('#edge-next'),edgePrev:$('#edge-prev'),
    picLayer:$('#picture-layer'),large:$('#picture-large'),caption:$('#picture-caption')
  };
  const STORE_KEY = 'teyvat-reader-position-v03'; // Same key as V0.7, so old localStorage continues to work.
  const BOOKMARK_MIGRATIONS = window.TEYVAT_BOOKMARK_MIGRATIONS || {bySection:{},byBlock:{}};
  const pad=(n)=>String(n).padStart(2,'0');
  const status = renderer.statusLabel;
  let doc=null;
  let pageflip=null;
  let fallback=null;
  let currentPage=0;
  let ready=false;
  let lastFocus=null;
  let pageWidth=0, pageHeight=0;
  let resizeTimer=null;
  let pictureAnchor=null;
  let pictureLogicalAnchor=null; // Preserve the selected leaf as well as the visible spread.
  let pictureFocus=null;
  let relayoutAfterPicture=false;

  class FallbackBook {
    constructor(node, pages, onChange) {
      this.node=node;
      this.pages=pages;
      this.onChange=onChange;
      this.index=0;
      this.busy=false;
      node.classList.add('fallback-mode');
      node.innerHTML='<div class="fallback-spread"><div class="fallback-leaf fallback-leaf-left"></div><div class="fallback-leaf fallback-leaf-right"></div><div class="fallback-turn-layer"></div></div>';
      this.left=node.querySelector('.fallback-leaf-left');
      this.right=node.querySelector('.fallback-leaf-right');
      this.layer=node.querySelector('.fallback-turn-layer');
      this.render();
    }
    portrait(){return window.matchMedia('(max-width:760px)').matches;}
    normalize(n){const i=Math.max(0,Math.min(this.pages.length-1,Math.floor(Number(n)||0)));return this.portrait()||i===0?i:(i%2===0?i-1:i);}
    render() {
      if(this.portrait()){this.left.innerHTML='';this.right.innerHTML=this.pages[this.index]||'';}
      else if(this.index===0){this.left.innerHTML='';this.right.innerHTML=this.pages[0]||'';}
      else{this.left.innerHTML=this.pages[this.index]||'';this.right.innerHTML=this.pages[this.index+1]||'';}
    }
    turnToPage(n){this.busy=false;this.index=this.normalize(n);this.layer.className='fallback-turn-layer';this.layer.innerHTML='';this.render();this.onChange(n);}
    getCurrentPageIndex(){return this.index;}
    flipNext(){this.flip(this.index===0?1:this.index+(this.portrait()?1:2));}
    flipPrev(){this.flip(this.index<=1?0:this.index-(this.portrait()?1:2));}
    flip(n){
      if(this.busy) return;
      const target=this.normalize(n);
      if(target===this.index) return;
      this.busy=true;
      const forward=target>this.index;
      this.layer.innerHTML=forward?(this.right.innerHTML||this.left.innerHTML):(this.left.innerHTML||this.right.innerHTML);
      this.layer.className=`fallback-turn-layer ${forward?'turning-next':'turning-prev'}`;
      let finished=false;
      const finish=()=>{
        if(finished) return;
        finished=true;this.busy=false;this.index=target;
        this.layer.className='fallback-turn-layer';this.layer.innerHTML='';this.render();this.onChange(this.index);
      };
      this.layer.addEventListener('animationend',finish,{once:true});
      window.setTimeout(finish,800);
    }
  }
  function getMeta(i){return doc?.pageInfo[i]||{type:'intro',title:'卷首'};}
  function toLocation(i){
    const meta=getMeta(i);
    if(meta.type==='chapter-body') return {type:'body',chapterId:meta.chapterId,sectionId:meta.sectionId,blockId:meta.blockId};
    if(meta.chapterId) return {type:'chapter',chapterId:meta.chapterId};
    if(meta.partId) return {type:'part',partId:meta.partId};
    return {type:'page',index:i};
  }
  function findPage(loc){
    if (!doc || !loc || typeof loc!=='object') return 0;
    if (loc.type==='body') {
      // Unchanged blocks retain exact position even when chapters are repaginated.
      if (loc.blockId && doc.blockStarts[loc.blockId] !== undefined) return doc.blockStarts[loc.blockId];
      // A rewritten or re-homed V0.7 block can instead follow its historical section.
      const legacyKey = `${loc.chapterId}:${loc.sectionId}`;
      const blockMoved = loc.blockId && BOOKMARK_MIGRATIONS.byBlock?.[loc.blockId];
      const sectionMoved = BOOKMARK_MIGRATIONS.bySection?.[legacyKey];
      // V0.8 used a generic outline target for future chapters. Prefer the
      // now-specific section when the saved location still knows that section.
      const genericTarget = blockMoved && `ch${pad(blockMoved.chapterId)}-outline`;
      const moved = blockMoved && sectionMoved && blockMoved.chapterId === sectionMoved.chapterId
        && blockMoved.sectionId === genericTarget ? sectionMoved : (blockMoved || sectionMoved);
      if (moved) {
        return doc.sectionStarts[`${moved.chapterId}:${moved.sectionId}`]
          ?? doc.chapterStarts[moved.chapterId]
          ?? doc.chapterStarts[loc.chapterId] ?? 0;
      }
      return doc.sectionStarts[legacyKey] ?? doc.chapterStarts[loc.chapterId] ?? 0;
    }
    if(loc.type==='chapter') return doc.chapterStarts[loc.chapterId] ?? 0;
    if(loc.type==='part') return doc.partStarts[loc.partId] ?? 0;
    return Math.max(0,Math.min(doc.pages.length-1,loc.index||0));
  }
  function loadLocation(){
    try {return JSON.parse(localStorage.getItem(STORE_KEY))||{type:'page',index:0};}
    catch(_){return {type:'page',index:0};}
  }
  function saveLocation(i){
    try {localStorage.setItem(STORE_KEY,JSON.stringify(toLocation(i)));}
    catch (_) { /* Private browsing or storage restricted. */ }
  }
  function setCurrentPage(i){
    if (!doc) return;
    currentPage=Math.max(0,Math.min(doc.pages.length-1,Number(i)||0));
    saveLocation(currentPage);
    const meta=getMeta(currentPage);
    let label=meta.title||'卷首';
    if(meta.chapterId) label=`第 ${pad(meta.partId)} 篇 · 第 ${pad(meta.chapterId)} 章　${meta.title}`;
    else if(meta.partId) label=`第 ${pad(meta.partId)} 篇　${meta.title}`;
    D.current.textContent=label;
    // Display page numbers computed from the current pagination only.
    // In a two-page spread show both visible page numbers. Never treat a
    // physical page number as a permalink, because editing changes it.
    const lastInteriorPage = doc.pages.length - 2;
    const doubleSpread = pageflip
      ? pageflip.getOrientation?.() === 'landscape'
      : fallback && !fallback.portrait();
    if (meta.type === 'cover') D.pageCount.textContent = '封面';
    else if (meta.type === 'back') D.pageCount.textContent = '封底';
    else if (doubleSpread && currentPage > 0) {
      const left = 1 + Math.floor((currentPage-1)/2)*2;
      const right = Math.min(left+1,lastInteriorPage);
      D.pageCount.textContent = left===right
        ? `第 ${left} / ${lastInteriorPage} 頁`
        : `第 ${left}–${right} / ${lastInteriorPage} 頁`;
    } else D.pageCount.textContent = `第 ${currentPage} / ${lastInteriorPage} 頁`;
    D.chapterReadout.textContent=meta.chapterId?`CHAPTER ${pad(meta.chapterId)}`:'世界通史';
    D.pageMeter.style.width=`${100*(currentPage+1)/doc.pages.length}%`;
    [D.prev,D.edgePrev].forEach(x=>x.disabled=currentPage===0);
    [D.next,D.edgeNext].forEach(x=>x.disabled=currentPage>=doc.pages.length-1);
    D.tocEntries.querySelectorAll('.toc-entry').forEach(el=>{
      const on=Number(el.dataset.chapter)===meta.chapterId;
      el.classList.toggle('active',on);
      if(on) el.setAttribute('aria-current','location'); else el.removeAttribute('aria-current');
    });
  }
  function recreateBook(){
    try {if(pageflip) pageflip.destroy();} catch(e){console.warn('Previous book cleanup:',e);}
    pageflip=null;fallback=null;
    D.book.remove();
    const next=document.createElement('div');
    next.id='book';next.className='book-root';next.setAttribute('aria-label','可翻頁的完整電子書');
    D.frame.appendChild(next);D.book=next;
  }
  function initialize(loc){
    if(ready) return;
    ready=true;
    const rect=D.frame.getBoundingClientRect();
    pageWidth=rect.width;pageHeight=rect.height;
    doc=renderer.build(D.frame);
    window.__teyvatDiagnostics={pageCount:doc.pages.length,chapterCount:Object.keys(doc.chapterStarts).length,partCount:Object.keys(doc.partStarts).length,bookmarks:doc.blockStarts};
    if(window.St && typeof window.St.PageFlip==='function') {
      try {
        D.book.innerHTML=doc.pages.join('');
        pageflip=new window.St.PageFlip(D.book,{
          width:520,height:685,size:'stretch',minWidth:275,maxWidth:770,minHeight:363,maxHeight:1014,
          showCover:true,usePortrait:true,autoSize:true,flippingTime:780,drawShadow:true,
          maxShadowOpacity:.42,mobileScrollSupport:false,swipeDistance:35,
          // Clicking in the center must not compete with image/lightbox controls.
          // Corner turns, swiping and navigation buttons remain enabled.
          disableFlipByClick:true,clickEventForward:true
        });
        pageflip.loadFromHTML(D.book.querySelectorAll('.book-page'));
        pageflip.on('flip',(e)=>{
          if (pictureAnchor !== null) {
            // Preserve both the spread and the logical reading/bookmark leaf.
            if (e.data !== pictureAnchor) pageflip.turnToPage(pictureAnchor);
            setCurrentPage(pictureLogicalAnchor ?? pictureAnchor);
            return;
          }
          setCurrentPage(e.data);
        });
      } catch(error) {
        console.warn('StPageFlip unavailable; using bundled CSS flip fallback',error);
        pageflip=null;
        D.book.innerHTML='';
      }
    }
    if(!pageflip) fallback=new FallbackBook(D.book,doc.pages,setCurrentPage);
    jumpTo(findPage(loc||loadLocation()));
  }
  function jumpTo(i){
    if(!doc)return;
    const target=Math.max(0,Math.min(doc.pages.length-1,Number(i)||0));
    if(pageflip) {pageflip.turnToPage(target);setCurrentPage(target);}
    else if(fallback) fallback.turnToPage(target);
  }
  function nextPage(){if(pageflip) pageflip.flipNext('bottom');else if(fallback) fallback.flipNext();}
  function prevPage(){if(pageflip) pageflip.flipPrev('bottom');else if(fallback) fallback.flipPrev();}
  function startReading(target=null){
    D.home.hidden=true;
    D.reader.hidden=false;
    document.body.style.overflow='hidden';
    window.scrollTo(0,0);
    initialize(target||loadLocation());
    if(window.location.hash!=='#read') history.replaceState(null,'','#read');
    if(target && ready) jumpTo(findPage(target));
  }
  function returnHome(){
    closeToc();closePicture();
    if(document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(()=>{});
    D.reader.hidden=true;D.home.hidden=false;
    document.body.style.overflow='';
    history.replaceState(null,'','#home');
  }
  function jumpPart(id){startReading({type:'part',partId:id});}
  function jumpChapter(id){startReading({type:'chapter',chapterId:id});}
  function buildOutline(){
    $('#outline-grid').innerHTML=catalog.parts.map(p=>`<button type="button" class="part-card" data-open-part="${p.id}" aria-label="翻至第 ${p.id} 篇：${p.title}"><span class="part-card-num">${pad(p.id)}</span><span class="part-card-details"><strong>${p.title}</strong><small>${p.chapters[0].id}–${p.chapters.at(-1).id} 章 · ${p.subtitle}</small></span><span class="part-card-arrow">↗</span></button>`).join('');
  }
  function buildToc(){
    D.tocEntries.innerHTML=catalog.parts.map(p=>`<details class="toc-part" data-part="${p.id}"${p.id===1?' open':''}><summary><span class="toc-part-index">${pad(p.id)}</span><span class="toc-part-title">${p.title}</span><span class="toc-part-count">${p.chapters.length} 章</span><span class="toc-part-chevron">›</span></summary><div class="toc-part-body"><button type="button" class="toc-part-jump" data-part-jump="${p.id}">↗ 前往本篇扉頁</button>${p.chapters.map(c=>`<button type="button" class="toc-entry" data-chapter="${c.id}"><span class="toc-entry-num">${pad(c.id)}</span><span class="toc-entry-text">${c.title}</span><span class="toc-entry-status">${status[chapters[c.id]?.status]||'編纂中'}</span></button>`).join('')}</div></details>`).join('');
  }
  function openToc(origin){
    lastFocus=origin||document.activeElement;
    D.toc.hidden=false;
    [D.topToc,D.floatingToc].forEach(btn=>btn.setAttribute('aria-expanded','true'));
    D.tocSearch.value='';filterToc();
    const active=getMeta(currentPage).partId||1;
    const row=D.tocEntries.querySelector(`.toc-part[data-part="${active}"]`);
    if(row) row.open=true;
    $('#toc-close').focus();
  }
  function closeToc(){
    D.toc.hidden=true;
    [D.topToc,D.floatingToc].forEach(btn=>btn.setAttribute('aria-expanded','false'));
    if(lastFocus && !D.reader.hidden && typeof lastFocus.focus==='function')lastFocus.focus();
    lastFocus=null;
  }
  function filterToc(){
    const q=D.tocSearch.value.trim().toLowerCase();
    D.tocEntries.querySelectorAll('.toc-part').forEach(row=>{
      let matches=0;
      const partMatches=row.querySelector('.toc-part-title').textContent.toLowerCase().includes(q);
      row.querySelectorAll('.toc-entry').forEach(entry=>{
        const matched=!q||partMatches||entry.textContent.toLowerCase().includes(q);
        entry.hidden=!matched;
        if(matched)matches++;
      });
      row.hidden=!!q&&matches===0;
      row.open=!!q||row.open;
      row.querySelector('.toc-part-jump').hidden=!!q;
    });
  }
  function openPicture(el){
    if(!D.picLayer.hidden)return;
    pictureLogicalAnchor=currentPage;
    pictureAnchor=pageflip?.getCurrentPageIndex?.() ?? fallback?.getCurrentPageIndex?.() ?? currentPage;
    pictureFocus=el;
    D.large.src=el.dataset.src;
    D.large.alt=el.dataset.caption;
    D.caption.textContent=el.dataset.caption;
    D.picLayer.hidden=false;
    D.frame.classList.add('picture-open');
    $('#picture-dismiss').focus({preventScroll:true});
  }
  function closePicture(){
    if(D.picLayer.hidden)return;
    D.picLayer.hidden=true;
    D.large.removeAttribute('src');
    D.frame.classList.remove('picture-open');
    const anchor=pictureAnchor;
    const logicalAnchor=pictureLogicalAnchor ?? anchor;
    pictureAnchor=null;
    pictureLogicalAnchor=null;
    if(anchor!==null){
      const live=pageflip?.getCurrentPageIndex?.() ?? fallback?.getCurrentPageIndex?.() ?? currentPage;
      if(live!==anchor)jumpTo(logicalAnchor);
      else if(currentPage!==logicalAnchor)setCurrentPage(logicalAnchor);
    }
    if(pictureFocus?.isConnected)pictureFocus.focus({preventScroll:true});
    pictureFocus=null;
    if(relayoutAfterPicture){relayoutAfterPicture=false;repaginate();}
  }
  function repaginate(){
    if(!ready||D.reader.hidden)return;
    // Do not replace and repaginate the book below an open picture.
    if(!D.picLayer.hidden){relayoutAfterPicture=true;return;}
    const rect=D.frame.getBoundingClientRect();
    if(Math.abs(pageWidth-rect.width)<14 && Math.abs(pageHeight-rect.height)<14)return;
    const loc=toLocation(currentPage);
    recreateBook();ready=false;doc=null;
    initialize(loc);
  }

  buildOutline();buildToc();
  $('#begin-book').addEventListener('click',()=>startReading());
  $('#jump-outline').addEventListener('click',()=>$('#outline').scrollIntoView({behavior:'smooth'}));
  $('#outline-grid').addEventListener('click',(e)=>{const node=e.target.closest('button[data-open-part]');if(node)jumpPart(Number(node.dataset.openPart));});
  $('#exit-reader').addEventListener('click',returnHome);
  [D.next,D.edgeNext].forEach(x=>x.addEventListener('click',nextPage));
  [D.prev,D.edgePrev].forEach(x=>x.addEventListener('click',prevPage));
  [D.topToc,D.floatingToc].forEach(x=>x.addEventListener('click',()=>openToc(x)));
  $('#toc-shade').addEventListener('click',closeToc);
  $('#toc-close').addEventListener('click',closeToc);
  $('#jump-front').addEventListener('click',()=>{jumpTo(0);closeToc();});
  D.tocSearch.addEventListener('input',filterToc);
  D.tocEntries.addEventListener('click',(e)=>{
    const p=e.target.closest('[data-part-jump]');
    const c=e.target.closest('[data-chapter]');
    if(p){jumpTo(doc.partStarts[Number(p.dataset.partJump)]);closeToc();}
    if(c){jumpTo(doc.chapterStarts[Number(c.dataset.chapter)]);closeToc();}
  });
  // Capture early on the stable frame, before StPageFlip receives mouse/touch input.
  // Using only a bubbling click listener is too late: the flip starts on pointerdown.
  const interactiveFigure=(e)=>e.target?.closest?.('.zoom-image');
  for (const type of ['pointerdown','mousedown','touchstart','pointermove','mousemove',
                      'touchmove','pointerup','mouseup','touchend','dragstart','dblclick']){
    D.frame.addEventListener(type,(e)=>{
      if(!interactiveFigure(e))return;
      e.stopPropagation();
      if(type==='dragstart')e.preventDefault();
    },{capture:true,passive:type.startsWith('touch')});
  }
  // Image click is handled at capture phase; StPageFlip never sees the interaction.
  D.frame.addEventListener('click',(e)=>{
    const image=interactiveFigure(e);
    if(!image)return;
    e.preventDefault();e.stopPropagation();
    openPicture(image);
  },true);
  // Normal chapter links still use fixed-frame delegation.
  D.frame.addEventListener('click',(e)=>{
    const p=e.target.closest?.('[data-jump-part]');
    const c=e.target.closest?.('[data-jump-chapter]');
    if(p){e.preventDefault();e.stopPropagation();jumpTo(doc.partStarts[Number(p.dataset.jumpPart)]);}
    else if(c){e.preventDefault();e.stopPropagation();jumpTo(doc.chapterStarts[Number(c.dataset.jumpChapter)]);}
  });
  $('#picture-dismiss').addEventListener('click',closePicture);
  D.picLayer.addEventListener('click',(e)=>{if(e.target===D.picLayer)closePicture();});
  $('#fullscreen-btn').addEventListener('click',async()=>{
    try {if(document.fullscreenElement)await document.exitFullscreen();else if(D.reader.requestFullscreen)await D.reader.requestFullscreen();}
    catch(error){console.warn('Native fullscreen not supported in this context',error);}
  });
  document.addEventListener('fullscreenchange',()=>{
    $('#fullscreen-icon').textContent=document.fullscreenElement?'⊟':'⛶';
    $('#fullscreen-btn').setAttribute('aria-label',document.fullscreenElement?'離開全螢幕模式':'進入全螢幕模式');
    window.setTimeout(repaginate,150);
  });
  document.addEventListener('keydown',(e)=>{
    if(D.reader.hidden) return;
    if(!D.picLayer.hidden){if(e.key==='Escape')closePicture();return;}
    if(!D.toc.hidden){if(e.key==='Escape')closeToc();return;}
    if(e.target?.matches?.('input,textarea,[contenteditable="true"]'))return;
    if(e.key==='ArrowRight'){e.preventDefault();nextPage();}
    else if(e.key==='ArrowLeft'){e.preventDefault();prevPage();}
    else if(e.key.toLowerCase()==='m'&&!e.altKey&&!e.ctrlKey&&!e.metaKey)openToc(D.floatingToc);
  });
  window.addEventListener('resize',()=>{
    if(!ready||D.reader.hidden)return;
    window.clearTimeout(resizeTimer);
    resizeTimer=window.setTimeout(repaginate,260);
  });
  const deep=location.hash.match(/^#chapter-(\d{1,2})$/);
  const oldSection=location.hash.match(/^#(ch(\d{2})-[a-zA-Z0-9_-]+)$/);
  if(deep){jumpChapter(Number(deep[1]));}
  else if(oldSection){
    // Support shared historical section links, e.g. #ch01-phanes -> new Chapter 3.
    startReading({type:'body',chapterId:Number(oldSection[2]),sectionId:oldSection[1]});
  }
  else if(location.hash==='#read'){startReading();}
}());
