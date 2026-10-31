#!/usr/bin/env python3
"""Original historical-diagram SVG plates for Chapter 02. No external image assets."""
from pathlib import Path
from html import escape
from math import sin, cos, pi
from random import Random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'illustrations' / 'ch02'
OUT.mkdir(parents=True, exist_ok=True)
NAVY = '#273D4F'
GOLD = '#AA8655'
INK = '#334B58'
MUTED = '#806F56'
PALE = '#F7EFDF'
FONT = 'Noto Serif CJK TC, Noto Serif TC, serif'
SANS = 'Noto Sans CJK TC, Noto Sans TC, sans-serif'

def text(x, y, value, size=24, fill=INK, anchor='middle', weight=500, family=FONT, spacing='0.03em'):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{family}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(value)}</text>')

def line(x1,y1,x2,y2,color=GOLD,width=2,dash=None,extra=''):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"{d} {extra}/>'

def rect(x,y,w,h,fill=PALE,stroke='#BFA47D',radius=14,width=2,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'

def circle(x,y,r,fill=PALE,stroke=GOLD,width=2,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'

def stars(seed, num=50, x0=75, x1=1125, y0=135, y1=535):
    rng=Random(seed)
    arr=[]
    for _ in range(num):
        x=round(rng.uniform(x0,x1),1); y=round(rng.uniform(y0,y1),1)
        r=round(rng.uniform(1.0,2.6),1)
        arr.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E9D5AC" opacity="{round(rng.uniform(.32,.90),2)}"/>')
    return ''.join(arr)

def base(no,title,subtitle,body,height=650):
    W=1200; H=height
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="圖 2-{no}：{escape(title)}">
<defs>
 <linearGradient id="paper" x2="0.25" y2="1"><stop stop-color="#F9F2E3"/><stop offset="1" stop-color="#E9DAC0"/></linearGradient>
 <linearGradient id="night" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#14283C"/><stop offset="1" stop-color="#526476"/></linearGradient>
 <radialGradient id="moon"><stop stop-color="#FFFFEA"/><stop offset=".72" stop-color="#EDE4C6"/><stop offset="1" stop-color="#C1A988"/></radialGradient>
 <radialGradient id="earth"><stop stop-color="#6D929B"/><stop offset="1" stop-color="#294D60"/></radialGradient>
 <linearGradient id="lava" x1="0" y1="0" x2="0.8" y2="1"><stop stop-color="#E2B979"/><stop offset="1" stop-color="#9F5042"/></linearGradient>
 <marker id="arr" markerWidth="12" markerHeight="12" refX="8" refY="4" orient="auto"><path d="M1 1 L8 4 L1 7" fill="none" stroke="#B69664" stroke-width="1.8"/></marker>
</defs>
<rect width="{W}" height="{H}" fill="url(#paper)"/>
<rect x="18" y="17" width="1164" height="{H-34}" rx="3" fill="none" stroke="#B89A70" stroke-width="2"/>
<rect x="26" y="25" width="1148" height="{H-50}" fill="none" stroke="#D4BFA1" stroke-width="1"/>
{line(46,115,1154,115,'#B99F7B',1.6)}
{text(54,56,f'PLATE 2–{no}  ·  THE CHRONICLES OF TEYVAT',15,GOLD,'start',600,SANS,'0.14em')}
{text(54,102,title,37,NAVY,'start',600)}
{text(1139,93,subtitle,17,'#937D5B','end')}
{body}
{line(52,H-53,1148,H-53,'#BCA681',1.2)}
{text(60,H-24,'《提瓦特通史》第二章 · 原創概念示意',15,'#88765C','start',400)}
{text(1140,H-24,'非官方美術／非比例圖',14,'#88765C','end',400)}
</svg>'''

def save(no,name,title,sub,content,height=650):
    fn=OUT/name
    fn.write_text(base(no,title,sub,content,height),encoding='utf-8')
    print(fn.relative_to(ROOT))

# 1. Hierarchy with no invented ancient dragon names or regional boundaries.
b=''
b += rect(66,144,1068,124,'#294255','#A88B61',16,2)
b += text(599,188,'尼伯龍根',35,'#F5E8CE',weight=600)
b += text(599,231,'原生世界的最高統治者',24,'#E7CDA3')
b += line(600,268,600,302,'#A88755',4)
b += line(145,302,1055,302,'#A88755',3)
names=['火','水','風','雷','草','冰','岩']
colors=['#AB624B','#5794A9','#769E9A','#9C83AD','#7F9D71','#91ACC2','#A18862']
for idx,(name,color) in enumerate(zip(names,colors)):
    x=145+idx*152
    b+=line(x,302,x,339,'#A88755',2)
    b+=rect(x-62,339,124,127,'#F9F1DE','#B69A71',10,2)
    b+=circle(x,387,31,color,'#F6E3BC',2)
    b+=text(x,397,name,29,'#FBF6E8',weight=600)
    b+=text(x,444,f'{name}龍王',22,NAVY)
b+=text(600,513,'七位元素龍王 · 分掌各自的元素大權',23,'#786547')
b+=text(600,555,'古龍王國與原生元素生命',21,MUTED)
save(1,'01-seven-sovereigns.svg','古龍王權與元素大權','統治層級示意 · 非領土地圖',b)

# 2. Ancient Tollan, volcano and linked core technologies.
b=''
b+=rect(58,139,542,423,'#263C4D','#A88E66',14,2)
b+=stars(23,26,80,575,160,535)
b+=f'<path d="M98 484 L180 420 L247 307 L315 233 L366 315 L434 411 L550 486Z" fill="#64737C" stroke="#DECCA7" stroke-width="3"/>'
b+=f'<path d="M250 308 L315 233 L366 315 L345 309 L320 264 L288 313Z" fill="#CC8156" stroke="#EECC9A" stroke-width="2"/>'
b+=f'<path d="M305 262 Q278 342 268 425 L316 467 L330 426 Q317 329 337 285Z" fill="url(#lava)" opacity=".8"/>'
b+=f'<path d="M166 488 L208 458 L226 475 L266 436 L301 469 L329 432 L365 471 L403 452 L455 485" fill="none" stroke="#D5B687" stroke-width="8"/>'
b+=line(98,504,550,504,'#9DB0A8',3)
b+=text(323,177,'聖山 · 圖蘭城',31,'#F4E7C8')
b+=text(323,544,'古龍文明中心',20,'#F0D8AB')
b+=line(620,356,670,356,'#AE8C5E',3,extra='marker-end="url(#arr)"')
for j,(lab,detail) in enumerate([
    ('源火','火龍王的生命本源'),('龍裔創造','由源火分化生命'),('燃素與秘源技術','設備運作、資訊承載')]):
    x=689; y=150+j*138
    b+=rect(x,y,452,113,'#FBF4E4','#B79A72',14,2)
    b+=circle(744,y+55,30,['#B3624A','#688A77','#5D8794'][j],'#E8D3AA',2)
    b+=text(744,y+63,['火','生','機'][j],24,'#FAF4E5')
    b+=text(807,y+43,lab,26,NAVY,'start',600)
    b+=text(807,y+79,detail,20,MUTED,'start',400)
save(2,'02-tollan.svg','聖山圖蘭與古龍文明','源火 · 生命創造 · 燃素技術',b)

# 3. Interstellar visitor and dragon, abstract; no specific character portrait.
b=''
b+=rect(48,139,1104,424,'url(#night)','#9F865C',14,2)
b+=stars(44,78,75,1120,149,554)
b+=circle(288,344,140,'url(#earth)','#D7B77F',4)
b+=f'<path d="M177 349 L220 296 L252 322 L284 274 L322 324 L352 303 L398 354 L397 387 L180 387Z" fill="#8EA69D" opacity=".82"/>'
b+=f'<path d="M197 292 Q268 216 353 258 Q407 275 447 325 Q403 309 372 327 Q337 353 306 335 Q267 314 240 344 Q233 295 197 292Z" fill="none" stroke="#DBD0B3" stroke-width="7" opacity=".86"/>'
b+=circle(822,231,43,'#EADAB5','#D6AF73',3)
b+=f'<path d="M822 160 L836 216 L892 229 L836 241 L822 299 L810 241 L753 229 L810 216Z" fill="#E6C98D" opacity=".83"/>'
b+=f'<path d="M731 345 Q806 328 868 352 Q948 369 1042 322" fill="none" stroke="#C1AA90" stroke-width="2.5" stroke-dasharray="7 12"/>'
b+=f'<path d="M756 436 C823 395 919 463 1042 413" fill="none" stroke="#A36367" stroke-width="7" opacity=".55"/>'
b+=text(289,513,'始源之龍與提瓦特',23,'#E9D8B8')
b+=text(826,313,'星海記述者',27,'#F3E3C2')
b+=text(866,396,'宇宙中的毀滅威脅',22,'#F2D9B5')
b+=rect(527,174,169,62,'#EBDAB9','#BF9E6D',13,2)
b+=text(612,214,'星海相遇',23,NAVY)
b+=text(606,544,'保護眾生 · 尋求世界的延續',23,'#EAD5B2')
save(3,'03-cosmic-warning.svg','星海記述者與始源之龍','來自世界之外的警告 · 概念示意',b)

# 4. Three moons; avoid invention of separated cosmic portfolios.
b=''
b+=rect(50,144,1100,384,'url(#night)','#AA8B60',14,2)
b+=stars(12,67,70,1130,158,522)
moons=[(250,276,94,'恆月','艾莉亞','#EDDEBE'),(599,276,81,'霜月','卡儂','#DBE7E5'),(948,276,71,'虹月','桑娜妲','#D9D0DA')]
for i,(x,y,r,name,person,shade) in enumerate(moons):
    b+=circle(x,y,r,'url(#moon)',shade,4)
    b+=circle(x-12,y-14,r*.66,'none','#BAA783',2,extra='opacity=".32"')
    b+=f'<path d="M{x-66} {y+7} Q{x-6} {y-29} {x+65} {y+22}" fill="none" stroke="#7E8792" stroke-width="4" opacity=".23"/>'
    if i==2:
        b+=f'<ellipse cx="{x}" cy="{y}" rx="{r+14}" ry="{r*.42}" transform="rotate(-28 {x} {y})" fill="none" stroke="#C9A8CD" stroke-width="7" opacity=".8"/>'
    b+=text(x,413,name,31,'#F3E6CA',weight=600)
    b+=text(x,453,person,26,'#D9D9D0')
b+=text(600,503,'三月共同職責 · 維繫提瓦特的世界運轉',24,'#F2D8AB')
b+=text(600,561,'恆月與海洋潮汐的運行密切相關',21,MUTED)
save(4,'04-three-moons.svg','恆月 · 霜月 · 虹月','三輪明月與三位月神',b)

# 5. Departure landscape with three moons above Teyvat and star track.
b=''
b+=rect(52,141,1096,412,'url(#night)','#A88C68',14,2)
b+=stars(78,85,73,1128,152,536)
b+=circle(297,398,116,'url(#earth)','#D8BF94',4)
b+=f'<path d="M193 447 L228 395 L269 427 L312 371 L358 412 L385 391 L412 445Z" fill="#AAB9AA" opacity=".85"/>'
b+=f'<path d="M184 442 Q293 476 407 443" fill="none" stroke="#D7D3C2" stroke-width="4"/>'
for x,y,r in [(210,210,37),(305,196,29),(393,218,24)]:
    b+=circle(x,y,r,'url(#moon)','#E2CCAF',2)
b+=f'<path d="M433 370 Q540 316 645 306 Q737 289 855 207" stroke="#E8C991" stroke-width="4" stroke-dasharray="11 15" fill="none" marker-end="url(#arr)"/>'
b+=f'<path d="M859 199 l25 -49 l18 51 l54 12 l-50 24 l-10 54 l-29 -42 l-53 -8Z" fill="#DFC68C" opacity=".87"/>'
b+=text(298,508,'三月守望 · 世界延續',23,'#F5E4C7')
b+=text(783,379,'尼伯龍根遠行',33,'#F2E5C7',weight=600)
b+=text(783,420,'前往星海尋求延續世界的方法',22,'#E4D1B1')
b+=text(786,468,'七龍王繼續統治原生世界',19,'#D8C6A5')
save(5,'05-departure.svg','尼伯龍根遠行與三月守望','原初之主缺席的龍族時代',b)

# 6. Non-numeric, 8-event relative chronology, two rows.
b=''
sequence=[
 ('01','原生王權','七龍王與尼伯龍根'),('02','古龍文明','圖蘭 · 源火 · 燃素'),
 ('03','星海警告','記述者造訪始源之龍'),('04','三月誕生','恆月 · 霜月 · 虹月'),
 ('05','龍王遠行','尼伯龍根前往星海'),('06','三月守望','維繫世界運轉'),
 ('07','王座降臨','身披羽翼的外來者'),('08','銜枝之年','第一次王座戰爭')
]
for i,(num,title,detail) in enumerate(sequence):
    row=i//4; col=i%4
    x=68+col*278; y=178+row*191
    b+=rect(x,y,245,137,'#FBF3E3','#BBA078',12,2)
    b+=rect(x+12,y+12,50,37,'#34495B','#34495B',7,1)
    b+=text(x+37,y+39,num,21,'#EDE3CF',weight=600,family=SANS)
    b+=text(x+122,y+79,title,27,NAVY,weight=600)
    b+=text(x+122,y+111,detail,18,MUTED)
    if col<3:
        b+=line(x+247,y+69,x+275,y+69,'#B08B55',3,extra='marker-end="url(#arr)"')
    if i==3:
        b+=f'<path d="M{x+117} {y+140} V{y+172} H{68+127} V{y+188}" fill="none" stroke="#B08B55" stroke-width="3" marker-end="url(#arr)"/>'
b+=text(600,595,'依事件先後排列 · 時間距離不按比例',19,MUTED)
save(6,'06-dragon-timeline.svg','龍族統治時代相對年表','古龍秩序與新王座降臨之前',b,690)
