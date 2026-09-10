from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
PALETTES = {
    'dark': dict(bg='#0D1117', panel='#111923', ink='#F0F6FC', muted='#9DAEC2', line='#293747', cyan='#67E8F9', violet='#B5A2FF', grid='#263444'),
    'light': dict(bg='#F6F8FC', panel='#EDF2F9', ink='#152337', muted='#52657D', line='#CDDAE8', cyan='#087E99', violet='#7451C8', grid='#D5DFEC'),
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
    p=PALETTES[theme]; w,h=(640,520) if mobile else (1200,400)
    s=start(w,h,p,'Anmol Patel | Xenon','AI, full-stack, and open source. Original orbital artwork with a luminous X at its center.')
    if mobile:
        s+=text(36,43,'XENON010101',20,p['muted'],spacing=1,mono=True)
        s+=text(32,111,'Anmol Patel',67,p['ink'],700,spacing=-3)
        s+=text(36,154,'AI  /  FULL-STACK  /  OPEN SOURCE',21,p['cyan'],600,spacing=.6)
        s+=orbit(p,320,348,.68)
    else:
        s+=f'<rect x="0" y="0" width="6" height="400" fill="url(#spectrum)"/>'
        s+=text(48,56,'XENON010101',19,p['cyan'],600,spacing=2,mono=True)
        s+=text(42,176,'Anmol',103,p['ink'],700,spacing=-5)
        s+=text(42,281,'Patel',103,p['ink'],700,spacing=-5)
        s+=text(48,344,'AI  /  FULL-STACK  /  OPEN SOURCE',21,p['cyan'],600,spacing=.7)
        s+=orbit(p,925,200,.80)
    (OUT/f'hero-{"mobile-" if mobile else ""}{theme}.svg').write_text(s+end(w,h,p),encoding='utf-8')


if __name__ == '__main__':
    for theme in PALETTES:
        hero(theme)
        hero(theme, True)
    print('Created four profile hero SVG assets.')
