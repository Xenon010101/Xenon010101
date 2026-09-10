from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
PALETTES = {
    'dark': dict(bg='#0D1117', panel='#1C141B', ink='#F0F6FC', muted='#9DAEC2', line='#3B2833', cyan='#E34455', violet='#B73550', grid='#33222C'),
    'light': dict(bg='#FCF7F8', panel='#F7EDF0', ink='#152337', muted='#52657D', line='#E6CFD6', cyan='#A51D35', violet='#731B37', grid='#E8D8DE'),
}

def text(x, y, value, size, color, weight=400, spacing=None, mono=False, extra=''):
    font = 'Consolas, Courier New, monospace' if mono else 'Segoe UI, Arial, Helvetica, sans-serif'
    ls = f' letter-spacing="{spacing}"' if spacing is not None else ''
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}"{ls} {extra}>{escape(value)}</text>'

def start(w,h,p,title,desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs>
 <linearGradient id="spectrum" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{p['cyan']}"/><stop offset="1" stop-color="{p['violet']}"/></linearGradient>
 <radialGradient id="halo"><stop stop-color="{p['cyan']}" stop-opacity=".2"/><stop offset=".5" stop-color="{p['violet']}" stop-opacity=".08"/><stop offset="1" stop-color="{p['bg']}" stop-opacity="0"/></radialGradient>
 <radialGradient id="core" cx=".3" cy=".2" r=".9"><stop stop-color="{p['cyan']}" stop-opacity=".16"/><stop offset=".55" stop-color="{p['panel']}"/><stop offset="1" stop-color="{p['bg']}"/></radialGradient>
 <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" stroke="{p['grid']}" stroke-width=".65"/></pattern>
 <clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="{p['bg']}"/>
<rect width="{w}" height="{h}" fill="url(#grid)" opacity=".55"/>
'''

def end(w,h,p):
    return f'</g><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="19.5" stroke="{p["line"]}"/></svg>\n'

def orbit(p,cx,cy,scale=1):
    s = f'<g transform="translate({cx} {cy}) scale({scale})">'
    s += '<circle r="290" fill="url(#halo)"/>'
    s += f'<circle r="210" stroke="{p["line"]}" stroke-dasharray="2 11"/><circle r="181" stroke="{p["line"]}" stroke-width=".75"/>'
    # Radial calibration marks make the abstract structure feel engineered.
    for n in range(72):
        a=2*math.pi*n/72
        r=201 if n%6==0 else 206
        s += f'<path d="M{r*math.cos(a):.2f} {r*math.sin(a):.2f} L{214*math.cos(a):.2f} {214*math.sin(a):.2f}" stroke="{p["muted"]}" opacity="{.65 if n%6==0 else .25}"/>'
    s += '<circle r="117" fill="url(#core)" stroke="url(#spectrum)" stroke-opacity=".5"/>'
    for angle in [-32,32,90]:
        s += f'<ellipse rx="211" ry="76" transform="rotate({angle})" stroke="url(#spectrum)" stroke-width="1.5" opacity=".8"/>'
    for n in [-72,-36,0,36,72]:
        ry=math.sqrt(117**2-n**2)*.3
        s += f'<ellipse cy="{n}" rx="{math.sqrt(117**2-n**2):.2f}" ry="{ry:.2f}" stroke="{p["cyan"]}" opacity=".12"/>'
    s += f'<path d="M-48-47L44 47M44-47L-48 47" stroke="url(#spectrum)" stroke-width="14"/>'
    s += f'<path d="M-48-47L44 47M44-47L-48 47" stroke="{p["ink"]}" stroke-width="1.4" opacity=".7"/>'
    for x,y,c in [(170,-111,p['cyan']),(-168,-108,p['violet']),(0,211,p['cyan'])]:
        s += f'<circle cx="{x}" cy="{y}" r="13" fill="{c}" opacity=".1"/><circle cx="{x}" cy="{y}" r="5" fill="{c}"/>'
    s += '</g>'
    return s

def hero(theme,mobile=False):
    p=PALETTES[theme]; w,h=(640,700) if mobile else (1200,480)
    s=start(w,h,p,'Anmol Patel | Xenon','AI, full-stack, and open source. Original orbital artwork with a luminous X at its center.')
    if mobile:
        s+=text(36,47,'XENON010101  /  ENGINEERED INTELLIGENCE',16,p['muted'],spacing=1,mono=True)
        s+=text(32,127,'Anmol Patel',67,p['ink'],700,spacing=-3)
        s+=text(36,170,'AI  /  FULL-STACK  /  OPEN SOURCE',21,p['cyan'],600,spacing=.6)
        s+=orbit(p,320,420,.9)
        s+=f'<path d="M36 652H604" stroke="{p["line"]}"/>'
        s+=text(36,681,'CURIOSITY → CODE → IMPACT',18,p['muted'],mono=True)
    else:
        s+=f'<rect x="0" y="0" width="6" height="480" fill="url(#spectrum)"/>'
        s+=text(48,56,'XENON010101',19,p['cyan'],600,spacing=2,mono=True)
        s+=text(48,104,'ENGINEERED INTELLIGENCE',15,p['muted'],spacing=3,mono=True)
        s+=text(42,215,'Anmol',103,p['ink'],700,spacing=-5)
        s+=text(42,320,'Patel',103,p['ink'],700,spacing=-5)
        s+=text(48,367,'AI  /  FULL-STACK  /  OPEN SOURCE',21,p['cyan'],600,spacing=.7)
        s+=orbit(p,910,220,.87)
        s+=f'<path d="M48 411H1152" stroke="{p["line"]}"/>'
        s+=text(48,448,'CURIOSITY → CODE → IMPACT',16,p['muted'],mono=True,spacing=1.4)
        s+=text(1152,448,'LEARN. BUILD. ITERATE.',14,p['muted'],mono=True,extra='text-anchor="end"')
    (OUT/f'hero-{"mobile-" if mobile else ""}{theme}.svg').write_text(s+end(w,h,p),encoding='utf-8')

def card(theme,kind,mobile=False):
    p=PALETTES[theme]; w,h=(640,460) if mobile else (1200,300)
    labels={
        'trading-agent': ('01 / APPLIED INTELLIGENCE','Signals into','perspective.','Market signals converge into an abstract analysis path.'),
        'focustube': ('02 / INTENTIONAL EXPERIENCES','Less noise.','More focus.','A luminous play symbol sits within quiet concentric frames.'),
        'presentai': ('03 / FEEDBACK SYSTEMS','Present. Reflect.','Improve.','Presentation geometry connects to a structured feedback loop.'),
    }
    label,line1,line2,desc=labels[kind]
    s=start(w,h,p,kind,desc)
    s+=f'<rect width="{w}" height="3" fill="url(#spectrum)"/>'
    s+=text(32 if mobile else 40,44 if mobile else 49,label,20 if mobile else 17,p['muted'],mono=True,spacing=1)
    s+=text(30 if mobile else 36,106 if mobile else 130,line1,54 if mobile else 61,p['ink'],600,spacing=-2)
    s+=text(30 if mobile else 36,164 if mobile else 197,line2,54 if mobile else 61,p['cyan'] if kind!='focustube' else p['violet'],600,spacing=-2)
    if mobile:
        s+='<g transform="translate(-620 175)">'
    else:
        s+=f'<rect x="40" y="250" width="84" height="3" fill="url(#spectrum)"/><circle cx="141" cy="251" r="3" fill="{p["cyan"]}"/>'
        s+='<g>'
    s+='<circle cx="926" cy="150" r="270" fill="url(#halo)"/>'
    if kind=='trading-agent':
        s+=f'<path d="M650 237H1160M650 55V237" stroke="{p["line"]}"/>'
        for x,y,b in [(680,181,22),(724,160,38),(768,184,24),(812,127,34),(856,145,25),(900,100,37),(944,122,23),(988,83,26),(1032,66,21),(1076,85,24),(1120,47,30)]:
            col=p['cyan'] if x%88==64 else p['violet']
            s+=f'<path d="M{x} {y-15}V{y+b+15}" stroke="{col}" opacity=".55"/><rect x="{x-7}" y="{y}" width="14" height="{b}" rx="2" fill="{col}" opacity=".5"/>'
        s+='<path d="M654 219C702 219 710 170 754 185S810 168 838 163S880 109 917 126S968 107 1001 94S1081 99 1148 46" stroke="url(#spectrum)" stroke-width="3"/>'
        s+=f'<circle cx="1148" cy="46" r="13" fill="{p["cyan"]}" opacity=".15"/><circle cx="1148" cy="46" r="5" fill="{p["cyan"]}"/>'
    elif kind=='focustube':
        for x,y,rw,rh,op in [(660,34,482,234,.35),(690,51,422,200,.6),(731,72,340,158,1)]:
            s+=f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" rx="{16}" stroke="{p["line"]}" fill="{p["panel"]}" fill-opacity=".25" opacity="{op}"/>'
        s+='<circle cx="901" cy="150" r="76" stroke="url(#spectrum)" stroke-dasharray="2 8" opacity=".55"/>'
        s+='<circle cx="901" cy="150" r="51" fill="url(#core)" stroke="url(#spectrum)" stroke-width="2"/>'
        s+='<path d="M891 127L923 150L891 173Z" fill="url(#spectrum)"/>'
        s+=f'<path d="M760 254H1042" stroke="{p["line"]}"/><path d="M760 254H914" stroke="{p["violet"]}" stroke-width="3"/><circle cx="914" cy="254" r="5" fill="{p["violet"]}"/>'
    else:
        s+=f'<rect x="679" y="66" width="240" height="163" rx="13" fill="{p["panel"]}" stroke="{p["line"]}"/>'
        s+=f'<path d="M705 94H753M705 110H787" stroke="{p["muted"]}" stroke-width="4" stroke-linecap="round"/>'
        for x,hh in [(710,31),(739,47),(768,66)]:
            s+=f'<rect x="{x}" y="{198-hh}" width="16" height="{hh}" rx="3" fill="url(#spectrum)" opacity=".8"/>'
        s+='<circle cx="852" cy="155" r="30" stroke="url(#spectrum)" stroke-width="8" stroke-dasharray="128 61" transform="rotate(-90 852 155)"/>'
        s+=f'<path d="M919 146H974M957 139L974 146L957 153" stroke="{p["cyan"]}" stroke-width="2"/>'
        for y,ll in [(91,91),(137,65),(183,79)]:
            s+=f'<rect x="995" y="{y}" width="145" height="32" rx="7" fill="{p["panel"]}" stroke="{p["line"]}"/>'
            s+=f'<path d="M1006 {y+16}L1011 {y+21}L1019 {y+11}" stroke="{p["cyan"]}" stroke-width="2"/><path d="M1030 {y+16}H{1030+ll}" stroke="{p["muted"]}" stroke-width="3" stroke-linecap="round"/>'
        s+=f'<path d="M1070 229V251H799V240M791 248L799 240L807 248" stroke="{p["violet"]}" stroke-width="1.5" stroke-dasharray="4 5"/>'
    s+='</g>'
    (OUT/f'{kind}-{"mobile-" if mobile else ""}{theme}.svg').write_text(s+end(w,h,p),encoding='utf-8')

def footer(theme,mobile=False):
    p=PALETTES[theme]; w,h=(640,180) if mobile else (1200,116)
    s=start(w,h,p,'Keep building','Learn. Build. Ship. Improve. Repeat.')
    if mobile:
        s+='<path d="M33 70L69 106M69 70L33 106" stroke="url(#spectrum)" stroke-width="5"/>'
        s+=text(111,77,'LEARN → BUILD → SHIP',27,p['ink'],600,mono=True)
        s+=text(111,122,'IMPROVE → REPEAT',27,p['cyan'],600,mono=True)
    else:
        s+='<path d="M33 40L69 76M69 40L33 76" stroke="url(#spectrum)" stroke-width="5"/>'
        for x,word in [(114,'LEARN'),(322,'BUILD'),(527,'SHIP'),(706,'IMPROVE'),(964,'REPEAT')]:
            s+=text(x,69,word,27,p['ink'],600,spacing=2,mono=True)
        for x in [268,475,653,910]:
            s+=text(x,68,'→',26,p['cyan'],mono=True)
    (OUT/f'footer-{"mobile-" if mobile else ""}{theme}.svg').write_text(s+end(w,h,p),encoding='utf-8')

def achievement(theme,mobile=False):
    p=PALETTES[theme]; w,h=(640,210) if mobile else (1200,144)
    s=start(w,h,p,'GSSoC 2026 — Rank #13','Anmol Patel’s GSSoC 2026 achievement, as supplied in the original profile.')
    s+=f'<rect x="0" y="0" width="5" height="{h}" fill="url(#spectrum)"/>'
    s+=text(32 if mobile else 40,142 if mobile else 111,'#13',94 if mobile else 92,p['cyan'],700,spacing=-5)
    if mobile:
        s+=f'<path d="M244 42V168" stroke="{p["line"]}"/>'
        s+=text(280,99,'GSSoC',39,p['ink'],600)
        s+=text(280,144,'2026',29,p['muted'],mono=True,spacing=3)
    else:
        s+=f'<path d="M250 32V112" stroke="{p["line"]}"/>'
        s+=text(284,72,'GSSoC 2026',33,p['ink'],600)
        s+=text(284,108,'OPEN SOURCE · REAL CONTRIBUTIONS',19,p['muted'],mono=True,spacing=1)
        for n in range(9):
            x=976+n*20
            s+=f'<rect x="{x}" y="{84-n*5}" width="6" height="{20+n*5}" rx="3" fill="{p["cyan"] if n%2 else p["violet"]}" opacity="{.18+n*.07}"/>'
    (OUT/f'achievement-{"mobile-" if mobile else ""}{theme}.svg').write_text(s+end(w,h,p),encoding='utf-8')

if __name__ == '__main__':
    for theme in PALETTES:
        hero(theme)
        hero(theme,True)
        for kind in ['trading-agent','focustube','presentai']:
            card(theme,kind)
            card(theme,kind,True)
        footer(theme)
        footer(theme,True)
        achievement(theme)
        achievement(theme,True)
    print('Created 24 self-contained profile SVG assets.')
