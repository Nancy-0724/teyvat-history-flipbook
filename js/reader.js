/* 《提瓦特通史》v0.3 — book builder and content-aware adaptive pagination.
 * Content is compiled from independent Markdown files to generated-content.js.
 * A chapter can grow by one paragraph or many sections without editing this file.
 */
(function () {
  'use strict';
  const book = window.TEYVAT_BOOK;
  const content = window.TEYVAT_CONTENT;
  if (!book || !content) {
    console.error('書目或章節資料未載入；請先執行 python tools/build.py');
    return;
  }
  const PAD = (n) => String(n).padStart(2,'0');
  const statusLabel = {outline:'編纂中',draft:'草稿',reviewed:'已核對'};
  const esc = (text) => String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const view = (src, caption, float = false) => {
    return `<figure class="page-figure editorial-figure${float ? ' figure-float' : ''}"><button type="button" class="zoom-image" data-src="${esc(src)}" data-caption="${esc(caption)}" aria-label="放大圖表：${esc(caption)}"><img src="${esc(src)}" alt="${esc(caption)}" loading="lazy"></button><figcaption>${esc(caption)}</figcaption></figure>`;
  };

  function renderPaperPage(heading, html, index, className='') {
    return `<div class="book-page${className ? ' '+className : ''}"><div class="page-inner"><div class="page-heading"><span>${heading}</span><span>提瓦特通史 · 數位典籍</span></div><div class="page-body">${html}</div><div class="page-footer"><span>TEYVAT · CHRONICLES</span><span>${String(index).padStart(3,'0')}</span></div></div></div>`;
  }

  function createMeasurer(frame) {
    const small = window.matchMedia('(max-width:760px)').matches;
    const rect = frame.getBoundingClientRect();
    const w = Math.max(275, rect.width / (small ? 1 : 2));
    const h = Math.max(360, rect.height);
    const box = document.createElement('div');
    box.className = 'pagination-probe';
    box.style.width = `${w}px`;
    box.style.height = `${h}px`;
    box.innerHTML = renderPaperPage('章節正文', '', 0);
    document.body.appendChild(box);
    const body = box.querySelector('.page-body');
    const cache = new Map();
    function fits(blocks) {
      const key = blocks.map(b => b.blockId).join('|');
      if (cache.has(key)) return cache.get(key);
      body.innerHTML = blocks.map(b=>b.html).join('');
      // The body is deliberately scrollable as a safety net, but the paginator
      // moves complete blocks to the next leaf whenever they would overflow.
      const isFit = body.scrollHeight <= body.clientHeight + 2;
      if (cache.size > 1500) cache.clear();
      cache.set(key,isFit);
      return isFit;
    }
    return { fits, destroy: () => box.remove() };
  }

  function build(frame) {
    const pages = [];
    const pageInfo = [];
    const partStarts = {};
    const chapterStarts = {};
    const sectionStarts = {};
    const blockStarts = {};
    function addPage(heading, html, meta={}, className='') {
      const idx = pages.length;
      const layout = meta.title === '全書目錄（上）' ? 'page-contents-upper' : meta.title === '序' ? 'page-preface' : meta.type === 'part-index' ? 'page-part-index' : meta.type === 'end' ? 'page-afterword' : '';
      pages.push(renderPaperPage(heading,html,idx,(className+' '+layout).trim()));
      pageInfo.push({index:idx,...meta});
      return idx;
    }
    function addFlowPage(heading, html, meta={}, className='') {
      // Front/back matter is paginated too, instead of relying on a clipped
      // static sheet. Only layout changes; the original text stays in order.
      const holder=document.createElement('div');holder.innerHTML=html;
      const blocks=[...holder.children].map((el,i)=>({html:el.outerHTML,blockId:'editorial-'+i,heading:el.matches('h2,h3,.micro-cap')}));
      const measure=createMeasurer(frame);
      let buffer=[],first=true;
      function flush(){if(!buffer.length)return;addPage(heading+(first?'':' · 續'),buffer.map(b=>b.html).join(''),meta,className);first=false;buffer=[];}
      try {
        for(let i=0;i<blocks.length;i++) {
          const block=blocks[i];
          if(block.heading&&buffer.length&&i+1<blocks.length) {
            const keep=[block];
            for(let j=i+1;j<blocks.length&&keep.length<4;j++){keep.push(blocks[j]);if(!blocks[j].heading)break;}
            if(!measure.fits([...buffer,...keep]))flush();
          }
          if(buffer.length&&!measure.fits([...buffer,block]))flush();
          buffer.push(block);
        }
        flush();
      } finally { measure.destroy(); }
    }
    function addHard(html, meta={}, cls='page-hardcover') {
      const idx=pages.length;
      pages.push(`<div class="book-page ${cls}" data-density="hard">${html}</div>`);
      pageInfo.push({index:idx,...meta});
      return idx;
    }
    addHard(`<div class="hardcover-frame"><small>WORLD HISTORY OF TEYVAT</small><div class="hardcover-symbol">✧</div><h2>提 瓦 特<br>通 史</h2><p>從原初紀元到七國新世代</p><em>一 本 通 史　｜　八 大 篇 章　｜　六 十 章</em></div>`,{type:'cover',title:'封面'});
    addPage('卷首 · 扉頁',`<div class="frontispiece-kicker">A HISTORICAL READER</div><div class="frontispiece-emblem">✧</div><h2 class="frontispiece-title">提瓦特<br>通史</h2><p class="frontispiece-subtitle">從原初紀元到七國新世代</p><p class="micro">全書八篇 · 六十章 · 非官方歷史研究</p><div class="reading-remark">全書持續編纂中。各章依完成度標示「編纂中／草稿／已核對」；尚待驗證的敘述不代表遊戲已確認之正史。</div>`,{type:'intro',title:'扉頁'},'page-frontispiece');
    addFlowPage('卷首 · 序', `<span class="micro-cap">EDITOR'S PREFACE</span><h2>從故事走向歷史</h2><p class="lead">提瓦特的歷史散落於任務對話、人物記憶、石碑、典籍及地方傳說中。若只依遊戲更新順序閱讀，很容易將玩家得知真相的時間誤認為事件發生的年代。</p>${view('./assets/archive.svg','編纂示意圖：事件、證詞與文獻分別登錄')}<p>本書沿時間與制度變化組織材料，討論世界秩序的形成、文明興衰，以及重大災變對不同國家的影響。每章逐步補入原始出處、史料比較、年表和插圖。</p><p class="margin-script"><b>本版說明</b>八篇六十章均有獨立的內容檔案與可跳轉位置；目前已有 ${Object.values(content).filter(item => item.status !== 'outline').length} 章收錄正文，仍待最終史料校對；其餘章節維持編纂中。新增文字會在重新建置網站時自動分頁。</p>`,{type:'intro',title:'序'});
    addPage('卷首 · 全書目錄 · 上', `<span class="micro-cap">CONTENTS · PART I—IV</span><h2 class="toc-title">全書目錄（上）</h2><p class="micro">點選篇章即可直接翻至該篇扉頁。</p><div class="printed-part-list">${book.parts.slice(0,4).map(p => `<button type="button" data-jump-part="${p.id}"><span class="num">${PAD(p.id)}</span><span class="title">${esc(p.title)}</span><span class="end">${p.chapters.length} 章　↗</span></button>`).join('')}</div>${view('./assets/atlas.svg','八篇歷史主題示意圖')}<p class="reading-remark">點擊閱讀器左下角「全書目錄」可展開六十章，也能搜尋章名、人物與正文，跳到相關段落。</p>`,{type:'intro',title:'全書目錄（上）'});
    addPage('卷首 · 全書目錄 · 下', `<span class="micro-cap">CONTENTS · PART V—VIII</span><h2 class="toc-title">全書目錄（下）</h2><p class="micro">八大篇章依歷史研究主題與大致相對年代安排。</p><div class="printed-part-list">${book.parts.slice(4).map(p => `<button type="button" data-jump-part="${p.id}"><span class="num">${PAD(p.id)}</span><span class="title">${esc(p.title)}</span><span class="end">${p.chapters.length} 章　↗</span></button>`).join('')}</div><h3>閱讀方式</h3><p>電腦版為雙頁；手機為單頁。拖曳頁角或點擊箭頭翻頁，點擊插圖可查看放大圖說。全書目錄能在閱讀任何位置快速跳轉。</p>`,{type:'intro',title:'全書目錄（下）'});

    const probe = createMeasurer(frame);
    try {
      for (const part of book.parts) {
        const chapters=part.chapters;
        partStarts[part.id]=pages.length;
        addPage(`第 ${PAD(part.id)} 篇 · 扉頁`, `<div class="part-cover-inner"><div class="part-number">PART ${PAD(part.id)} · ${esc(part.english)}</div><div class="part-large-no">${PAD(part.id)}</div><h2 class="part-title">${esc(part.title)}</h2><p class="part-subtitle">${esc(part.subtitle)}</p><div class="part-quote">${esc(part.question)}</div><span class="part-range">第 ${chapters[0].id} — ${chapters[chapters.length-1].id} 章　／　共 ${chapters.length} 章</span></div>`,{type:'part',partId:part.id,title:part.title},'page-partcover');
        addPage(`第 ${PAD(part.id)} 篇 · 篇章目錄`, `<span class="micro-cap">PART ${PAD(part.id)} · CHAPTER INDEX</span><h2 class="toc-title">${esc(part.title)}</h2><p class="micro">章名可點擊直接跳轉，並顯示目前的編纂狀態。</p><div class="printed-chapter-list">${chapters.map(ch => `<button type="button" data-jump-chapter="${ch.id}"><span class="num">${PAD(ch.id)}</span><span class="title">${esc(ch.title)}</span><span class="end">${statusLabel[content[ch.id].status]}　↗</span></button>`).join('')}</div><p class="reading-remark">研究提示：${esc(part.question)}</p>`,{type:'part-index',partId:part.id,title:`${part.title} · 目錄`});
        for (const chapter of chapters) {
          const item = content[chapter.id];
          if (!item) throw new Error(`Missing compiled content for chapter ${chapter.id}`);
          const mark = statusLabel[item.status] || '編纂中';
          chapterStarts[chapter.id]=pages.length;
          addPage(`第 ${PAD(part.id)} 篇 · 第 ${PAD(chapter.id)} 章`, `<span class="chapter-serial">CHAPTER ${PAD(chapter.id)} · PART ${PAD(part.id)}</span><h2 class="chapter-opentitle">${esc(chapter.title)}</h2><div class="chapter-cover-rule"></div><p class="chapter-lead">${esc(chapter.summary)}</p><span class="chapter-status">${mark}${item.updated ? `　·　更新 ${esc(item.updated)}` : ''}</span><div class="chapter-open-mark">✦</div><p class="margin-script"><b>編纂說明</b>${item.status === 'outline' ? '此章僅為研究課綱；摘要中的名稱與主張仍待查證，不代表已確認的史實。' : item.status === 'draft' ? '此章仍為草稿，所引史料與歷史結論須逐項校對。' : '此章已列為核對完成，後續實裝版本仍可能修訂。'}</p>`,{type:'chapter',partId:part.id,chapterId:chapter.id,title:chapter.title},'page-chapter-open');
          const blocks=item.blocks;
          if (!blocks.length) continue;
          const label = `第 ${PAD(part.id)} 篇 · 第 ${PAD(chapter.id)} 章`;
          let buffer=[];
          function flush() {
            if (!buffer.length) return;
            const html=buffer.map(b=>b.html).join('');
            const pageIndex=addPage(label,html,{type:'chapter-body',partId:part.id,chapterId:chapter.id,title:chapter.title,sectionId:buffer[0].sectionId,blockId:buffer[0].blockId},item.status==='outline'?'page-outline-body':'page-chapter-body');
            for (const block of buffer) {
              blockStarts[block.blockId]=pageIndex;
              const key = `${chapter.id}:${block.sectionId}`;
              if (!(key in sectionStarts)) sectionStarts[key]=pageIndex;
            }
            buffer=[];
          }
          for (let i=0;i<blocks.length;i++) {
            const block=blocks[i];
            // Keep consecutive h2/h3 headings with the first prose block;
            // otherwise a section title can be stranded at a page bottom.
            if (block.kind==='heading' && buffer.length && i+1<blocks.length) {
              const keep=[block];
              for(let j=i+1;j<blocks.length && keep.length<4;j++) {
                keep.push(blocks[j]);
                if(blocks[j].kind!=='heading')break;
              }
              if(!probe.fits([...buffer,...keep]))flush();
            }
            if (buffer.length && !probe.fits([...buffer,block])) flush();
            buffer.push(block);
            if (!probe.fits(buffer)) {
              // A single oversized table/paragraph is kept scrollable rather
              // than cut off or silently dropped; subsequent blocks get new leaves.
              flush();
            }
          }
          flush();
        }
      }
    } finally {
      probe.destroy();
    }
    addFlowPage('卷末 · 編纂後記',`<span class="micro-cap">AFTERWORD</span><h2>未完的歷史</h2><p class="lead">當遊戲新版本提出更多史料時，年表、人物關係與既有敘述可能改變。本書保留史料來源與修訂狀態，逐篇逐章完善。</p>${view('./assets/chronicle.svg','歷史母年表示意圖')}<p>八篇六十章的閱讀位置已建立；新增任一 Markdown 章節、插圖或史料後，重新執行內容建置即可更新網站。</p><p class="margin-script"><b>非官方聲明</b>此為非官方研究企劃。原創 SVG 是教學示意，不代表《原神》官方設定；正式素材引用須個別確認授權與合理使用條件。</p>`,{type:'end',title:'編纂後記'});
    addHard(`<div class="backcover-copy"><span>✧</span><p>讓散落在時代中的線索<br>逐頁連成一部歷史。</p><small>TEYVAT HISTORY · IN PROGRESS</small></div>`,{type:'back',title:'封底'},'page-backcover');
    return {pages,pageInfo,partStarts,chapterStarts,sectionStarts,blockStarts};
  }

  window.TEYVAT_RENDERER = {build, statusLabel};
}());
