#!/usr/bin/env python3
"""Seven original, diagrammatic illustrations for chapter 01. Uses no external assets."""
from pathlib import Path
from xml.sax.saxutils import escape

DIR=Path(__file__).resolve().parents[1]/'assets/illustrations/ch01'
DIR.mkdir(parents=True,exist_ok=True)

INK='#354654'; GOLD='#AC8250'; PAPER='#F3EAD8'; BLUE='#3C7A91'; DARK='#243F51'; SILVER='#D6BE98'

def txt(x,y,s,sz=24,color=INK,anchor='middle',weight=500,spacing='0.03em'):
    return f'<text x="{x}" y="{y}" fill="{color}" text-anchor="{anchor}" font-size="{sz}" font-weight="{weight}" letter-spacing="{spacing}" font-family="Noto Serif CJK TC, Noto Serif TC, serif">{escape(s)}</text>'

def circle(x,y,r,fill,stroke=GOLD,sw=2,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def line(x1,y1,x2,y2,color=GOLD,width=2,dash=None,extra=''):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {d} {extra}/>'

def box(x,y,w,h,fill='url(#card)',stroke=GOLD,rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>'

def start(title,no,sub='歷史結構示意／依古代文獻編製'):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560" role="img" aria-label="圖 {no}：{escape(title)}">
    <defs>
      <linearGradient id="paper" x2="0.6" y2="1"><stop stop-color="#F8F0DF"/><stop offset="1" stop-color="#E8D9BC"/></linearGradient>
      <linearGradient id="card" x2="1" y2="1"><stop stop-color="#FBF5E8"/><stop offset="1" stop-color="#E8DBC6"/></linearGradient>
      <linearGradient id="sea" x2="0" y2="1"><stop stop-color="#527F93"/><stop offset="1" stop-color="#183D55"/></linearGradient>
      <linearGradient id="sky" x2="0" y2="1"><stop stop-color="#24384E"/><stop offset="1" stop-color="#557586"/></linearGradient>
      <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
      <marker id="arr" markerWidth="11" markerHeight="11" refX="7" refY="4" orient="auto"><path d="M1 1 L8 4 L1 7" fill="none" stroke="#927043" stroke-width="1.5"/></marker>
    </defs>
    <rect width="1200" height="560" fill="url(#paper)"/>
    <rect x="18" y="17" width="1164" height="526" rx="4" fill="none" stroke="#B89A70" stroke-width="2"/>
    <rect x="27" y="26" width="1146" height="508" rx="2" fill="none" stroke="#D2BEA2" stroke-width="1"/>
    {line(47,115,1153,115,'#B8A07B',1.5)}
    {txt(60,60,f'PLATE 0{no}  ·  THE CHRONICLES OF TEYVAT',15,GOLD,'start',600,'0.15em')}
    {txt(60,102,title,35,DARK,'start',600)}
    {txt(1140,91,sub,17,'#947B5D','end',400)}
    '''

def end():
    return txt(1140,519,'《提瓦特通史》原創示意圖  ·  非官方視覺化',13,'#8D7D65','end',400)+'</svg>'

def write(filename,title,no,body,sub='歷史結構示意／依古代文獻編製'):
    f=DIR/filename
    f.write_text(start(title,no,sub)+body+end(),encoding='utf-8')
    print(f)

# 01: primordial sea, original elemental life, dragons
body='''<path d="M47 416 Q90 374 147 399 T259 400 T369 399 T482 409 T597 399 T710 405 T827 393 T944 401 T1153 403 L1153 498 L47 498Z" fill="url(#sea)" opacity=".90"/>
<path d="M47 423 Q101 397 149 422 T255 419 T356 422 T456 421 T562 422 T657 424 T763 417 T863 420 T971 423 T1071 420 T1153 424" fill="none" stroke="#C5D5CA" stroke-width="3" opacity=".7"/>
<path d="M48 451 Q101 425 149 451 T255 448 T356 451 T456 450 T562 451 T657 453 T763 446 T863 449 T971 452 T1071 449 T1153 453" fill="none" stroke="#A7C1C0" stroke-width="2" opacity=".48"/>
<path d="M208 360 Q283 293 358 347 Q390 367 416 337 Q453 306 478 326 Q446 364 402 373 Q359 396 306 373 Q267 366 208 360Z" fill="#48778B" stroke="#D5BF91" stroke-width="3"/>
<path d="M320 344 Q288 298 272 278 L311 301 Q327 274 362 259 L347 309 Q383 316 399 338 Q360 332 320 344Z" fill="#385F70" stroke="#D5BF91" stroke-width="2"/>
<path d="M445 333 L466 312 L466 341 L439 355Z" fill="#385F70" stroke="#D5BF91" stroke-width="2"/>
<path d="M370 365 Q421 387 454 367" fill="none" stroke="#DBCDAE" stroke-width="3"/>
''' 
body+=circle(682,299,104,'#FCF6E8','#C7AD7D',3)+circle(682,299,80,'none','#D2BA93',2)
for x,y in [(682,201),(771,267),(737,373),(627,373),(593,267),(682,299)]:
    body+=circle(x,y,8,'#6B978E','#F1E6CE',1)
body+=txt(682,292,'原始大海',29,DARK)+txt(682,329,'生命共同起源',18,'#826647')
body+=txt(246,172,'原初水龍',26,DARK)+txt(246,204,'古老海洋的支配者',18,'#816E53')+line(285,215,330,274,GOLD,2)
body+=txt(938,186,'七龍王',28,DARK)+txt(938,218,'七種原始元素大權',19,'#816E53')
for i,(cx,cy,col) in enumerate([(848,278,'#B65C45'),(898,265,'#5D9EA7'),(948,278,'#B1A45B'),(996,265,'#887B9C'),(1046,278,'#6D8B63'),(898,327,'#86A5BD'),(998,329,'#A98F69')]):
    body+=circle(cx,cy,18,col,'#F7EAD2',3)
body+=txt(941,369,'原始元素生命秩序',17,'#645E50')+txt(120,470,'胎海（Primordial Sea）',18,'#ECE2CC','start')
write('01-primordial-sea.svg','原始大海與原生生命',1,body)

# 02: cosmos > world barrier diagram
body='''<rect x="47" y="140" width="1106" height="341" rx="10" fill="url(#sky)"/>
<circle cx="580" cy="306" r="147" fill="none" stroke="#D9B980" stroke-width="13"/>
<circle cx="580" cy="306" r="136" fill="#D7DACB" stroke="#C6AE82" stroke-width="2"/>
<circle cx="580" cy="306" r="108" fill="#C7D0C4" stroke="#95AAA1" stroke-width="2"/>
<path d="M480 374 L517 325 L546 349 L604 276 L647 338 L677 322 L709 374Z" fill="#768A89"/>
<path d="M478 374 Q568 339 705 373 L705 399 L475 399Z" fill="#9EAE9D"/>
<path d="M554 369 L600 327 L620 357 L658 343" fill="none" stroke="#D6DDCF" stroke-width="3"/>
'''
for x,y,r in [(100,193,2),(174,340,2.3),(248,213,2),(301,425,2),(338,168,1.8),(872,179,2),(922,356,2.2),(1050,237,2.6),(1084,407,1.9),(770,422,1.9),(392,290,2),(806,254,2)]:
    body+=circle(x,y,r,'#E9D3A8','none',0)
body+=txt(195,278,'外部宇宙',32,'#F2E7D0')+txt(195,315,'世界之外',17,'#D8C4A3')
body+=txt(581,232,'內部世界',28,DARK)+txt(581,261,'「世界的縮影」',19,'#5F706C')
body+=txt(942,276,'世界屏障',30,'#E9D6B3')+txt(942,310,'「蛋殼」之喻',18,'#D5BB92')
body+=f'<path d="M860 322 C812 348 760 353 731 343" fill="none" stroke="#D6BB89" stroke-width="3" marker-end="url(#arr)"/>'
body+=txt(580,459,'原初之人所建立的內外界線',18,'#E8D9BB')
write('02-world-barrier.svg','原初之人與世界屏障',2,body,'古籍中的蛋殼比喻 · 非實測天體圖')

# 03: four shades
body=box(393,139,414,84,fill='#314958',stroke='#A9895A')+txt(600,177,'原初之人／天上王座',29,'#F4E8D4')+txt(600,204,'四影出自同一創造者',16,'#D8C39C')
body+=line(600,224,600,256,GOLD,3)+line(160,256,1040,256,GOLD,2)
positions=[150,450,750,1050]
for x in positions: body+=line(x,256,x,285,GOLD,2)
items=[('生之執政','納貝里士','生命創造與形態','#5C8671','life'),('死之執政','若娜瓦','生命終結與死亡法則','#89666A','death'),('時之執政','伊斯塔露','時間流動與歷史','#8F7AA7','time'),('空之執政','阿斯莫代','空間與界線','#587D9B','space')]
for x,(head,name,detail,accent,kind) in zip(positions,items):
    body+=box(x-132,290,264,188,fill='#F5ECD9',stroke='#C0A67C',rx=9)
    body+=f'<rect x="{x-132}" y="290" width="264" height="7" rx="2" fill="{accent}"/>'
    body+=circle(x,344,29,'none',accent,3)
    if kind=='life': body+=f'<path d="M{x-14} 353 Q{x-4} 345 {x} 332 Q{x+4} 347 {x+15} 353 M{x} 332 L{x} 363" fill="none" stroke="{accent}" stroke-width="3"/>'
    if kind=='death': body+=f'<path d="M{x-10} 334 L{x+10} 354 M{x+10} 334 L{x-10} 354" stroke="{accent}" stroke-width="3"/><path d="M{x-14} 363 H{x+14}" stroke="{accent}" stroke-width="2"/>'
    if kind=='time': body+=f'<path d="M{x-12} 328 H{x+12} L{x-9} 361 H{x+9} L{x-12} 328" fill="none" stroke="{accent}" stroke-width="2.5"/>'
    if kind=='space': body+=f'<rect x="{x-12}" y="331" width="24" height="24" fill="none" stroke="{accent}" stroke-width="2" transform="rotate(45 {x} 343)"/>'
    body+=txt(x,398,head,24,DARK)+txt(x,430,name,21,accent)+txt(x,457,detail,16,'#6F6859')
write('03-four-shades.svg','四個發光的影子與四執政',3,body,'權能分類對照 · 依文獻與後來確認的身分整理')

# 04: War chronology
body='''<path d="M90 305 L1110 305" stroke="#A17F4D" stroke-width="4" fill="none" marker-end="url(#arr)"/>
'''
steps=[(145,'王座降臨','天上永恆王座抵達'),(435,'衝突開始','四影被創造'),(730,'四十餘年戰爭','七位龍王交戰'),(1030,'王國臣服','原始統治權更替')]
for i,(x,t,s) in enumerate(steps):
    body+=circle(x,305,15,'#D6B67B','#745B38',3)
    body+=box(x-118,152 if i%2==0 else 338,236,92,fill='#F5EAD4')
    body+=txt(x,(152 if i%2==0 else 338)+36,t,23,DARK)+txt(x,(152 if i%2==0 else 338)+67,s,17,'#887256')
    body+=line(x,244 if i%2==0 else 322,x,290 if i%2==0 else 338,'#A17F4D',2)
body+=txt(598,499,'鴿子銜枝之年　→　銜枝後四十餘年',18,'#755C38')
write('04-throne-war.svg','第一次王座戰爭相對時序',4,body,'事件先後示意 · 時距非比例')

# 05: Human civilization line
body='''<path d="M72 389 Q140 352 225 386 T400 382 T577 389 T756 386 T934 383 T1123 385" fill="none" stroke="#A68C63" stroke-width="4"/>
'''
stages=[(150,'天地改造','山川、河流'),(371,'創造生命','鳥獸、草木'),(600,'人類出現','與原初之人立約'),(827,'早期生產','農耕與採礦'),(1050,'文化形成','詩歌與聚集')]
for i,(x,a,b) in enumerate(stages):
    body+=circle(x,389,9,'#AC8756','#F6E9D4',3)
    body+=box(x-94,194,188,150,fill='#F3E8D2',stroke='#C0A980')
    body+=txt(x,300,a,23,DARK)+txt(x,326,b,15,'#847253')
    if i==0:
        body+=f'<path d="M{x-66} 268 L{x-30} 224 L{x-8} 246 L{x+17} 213 L{x+61} 268Z" fill="#718F84" stroke="#D8CCAE" stroke-width="2"/>'
    elif i==1:
        body+=f'<path d="M{x-52} 251 Q{x-15} 220 {x+18} 249 L{x+52} 235 L{x+43} 261 L{x+51} 278 Q{x+2} 288 {x-52} 251Z" fill="#618C99"/>'
    elif i==2:
        body+=circle(x,232,13,'#9B7859','none',0)+f'<path d="M{x} 247 V275 M{x} 253 L{x-20} 266 M{x} 253 L{x+20} 266" fill="none" stroke="#9B7859" stroke-width="6"/>'
    elif i==3:
        body+=f'<path d="M{x} 268 V219 M{x} 238 L{x-19} 222 M{x} 248 L{x+18} 231 M{x-12} 270 V243" fill="none" stroke="#8A955D" stroke-width="4" stroke-linecap="round"/>'
    else:
        body+=f'<path d="M{x-36} 236 Q{x-19} 223 {x} 236 Q{x+19} 223 {x+36} 236 V271 Q{x+18} 260 {x} 272 Q{x-18} 260 {x-36} 271Z" fill="#D8C29D" stroke="#927649" stroke-width="2"/><path d="M{x} 236 V272" stroke="#927649" stroke-width="2"/>'
body+=txt(595,460,'環境形成  →  生命創造  →  人類社會的初步建立',19,'#785E3D')
write('05-humanity.svg','世界改造與早期人類文明',5,body,'歷史階段示意 · 非比例年表')

# 06: three realms
body='''<circle cx="426" cy="306" r="140" fill="#3B889C" fill-opacity=".18" stroke="#40849A" stroke-width="4"/>
<circle cx="776" cy="306" r="140" fill="#AE875B" fill-opacity=".16" stroke="#A98757" stroke-width="4"/>
<circle cx="602" cy="347" r="136" fill="#8B708F" fill-opacity=".12" stroke="#806785" stroke-width="4"/>
'''
body+=txt(399,230,'光界',34,'#27677D')+txt(400,264,'原始元素生命',19,'#356C79')+txt(400,289,'七龍王與龍族',17,'#356C79')
body+=txt(809,230,'人界',34,'#86673C')+txt(809,264,'人類生存秩序',19,'#86673C')+txt(809,289,'地脈與受造生命',17,'#86673C')
body+=txt(601,389,'虛無界',29,'#77607A')+txt(601,418,'深淵的侵蝕性力量',17,'#77607A')
body+=box(526,286,152,47,fill='#F4EAD8',stroke='#BDA377',rx=7)+txt(602,317,'力量互相作用',19,DARK)
body+=txt(600,152,'三界為力量與生命領域的分類，並非三個互不相通的國家',17,'#806E55')
write('06-three-realms.svg','光界、人界與虛無界',6,body,'世界力量結構 · 非地理邊界')

# 07 Relative timeline years with visible ranges
body='''<path d="M93 302 H1110" stroke="#AB8C60" stroke-width="4" marker-end="url(#arr)"/>
'''
ticks=[(131,'王座之前','龍族統治'),(305,'銜枝之年','王座降臨'),(476,'四十餘年','龍王敗北'),(651,'四百餘年','人類誕生'),(828,'箱舟開門','文明建立'),(1018,'狂歡節','天上照護')]
for i,(x,a,b) in enumerate(ticks):
    body+=circle(x,302,12,'#F8ECD5','#97784F',3)
    yl=186 if i%2==0 else 359
    body+=box(x-82,yl,164,85,fill='#F7EEDF',stroke='#BDA47E')
    body+=txt(x,yl+35,a,21,DARK)+txt(x,yl+64,b,16,'#856B4E')
    body+=line(x,yl+85 if i%2==0 else yl,x,289 if i%2==0 else 315,'#AC8C61',2)
body+=txt(600,486,'年代依《日月前事》的相對順序排列，不代表絕對紀年',18,'#806649')
write('07-timeline.svg','創世紀元相對年表',7,body,'時間相對先後 · 時距非比例')
