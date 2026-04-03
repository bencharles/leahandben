#!/usr/bin/env python3
"""
Build script for Leah & Ben wedding site.

Assembles page templates into the base template, then encrypts
index-unprotected.html into the password-protected index.html gate page.

Usage:
    python build.py
"""

import os, re, base64
from pathlib import Path

# ── Paths ──
ROOT = Path(__file__).parent
TEMPLATES = ROOT / 'templates'
BASE_TPL = (TEMPLATES / 'base.html').read_text()

# ── Encryption config ──
PASSWORD = b'leahben26'
ITER = 600000


def parse_template(name):
    """Parse a page template into its sections."""
    text = (TEMPLATES / name).read_text()

    # Extract metadata
    title = re.search(r'\{\{TITLE:\s*(.+?)\}\}', text).group(1).strip()
    nav_active = re.search(r'\{\{NAV_ACTIVE:\s*(.+?)\}\}', text).group(1).strip()

    # Optional nav class (e.g. "scrolled" for pages without a hero)
    nav_cls_match = re.search(r'\{\{NAV_CLASS:\s*(.+?)\}\}', text)
    nav_class = nav_cls_match.group(1).strip() if nav_cls_match else ''

    # Extract sections
    styles = re.search(r'\{\{STYLES\}\}\n(.*?)\n\{\{/STYLES\}\}', text, re.DOTALL)
    body = re.search(r'\{\{BODY\}\}\n(.*?)\n\{\{/BODY\}\}', text, re.DOTALL)
    scripts = re.search(r'\{\{SCRIPTS\}\}\n(.*?)\n\{\{/SCRIPTS\}\}', text, re.DOTALL)

    return {
        'title': title,
        'nav_active': nav_active,
        'nav_class': nav_class,
        'styles': styles.group(1) if styles else '',
        'body': body.group(1) if body else '',
        'scripts': scripts.group(1) if scripts else '',
    }


def assemble(page_name, auth_check=''):
    """Assemble a page template into the base template."""
    page = parse_template(page_name)

    html = BASE_TPL
    html = html.replace('{{TITLE}}', page['title'].replace('&', '&amp;'))
    html = html.replace('{{PAGE_STYLES}}', page['styles'])
    html = html.replace('{{PAGE_BODY}}', page['body'])
    html = html.replace('{{PAGE_SCRIPTS}}', page['scripts'])
    html = html.replace('{{AUTH_CHECK}}', auth_check)

    # Nav class (e.g. scrolled for non-hero pages)
    html = html.replace('{{NAV_EXTRA_CLS}}', f' class="{page["nav_class"]}"' if page['nav_class'] else '')

    # Nav active states
    html = html.replace('{{NAV_WELCOME_CLS}}', ' active' if page['nav_active'] == 'welcome' else '')
    html = html.replace('{{NAV_TRAVEL_CLS}}', ' active' if page['nav_active'] == 'travel' else '')
    html = html.replace('{{NAV_RSVP_CLS}}', ' active' if page['nav_active'] == 'rsvp' else '')

    return html


def encrypt_page(plaintext_html):
    """Encrypt HTML with AES-GCM and return the gate page HTML."""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    plaintext = plaintext_html.encode('utf-8')
    salt = os.urandom(16)
    iv = os.urandom(12)

    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(PASSWORD)
    ct = AESGCM(key).encrypt(iv, plaintext, None)

    S = base64.b64encode(salt).decode()
    I = base64.b64encode(iv).decode()
    C = base64.b64encode(ct).decode()

    # Build gate page — uses {{ }} for f-string escaping of JS braces
    return f'''<!DOCTYPE html>
<html lang="en" style="background:#4A5320">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Leah &amp; Ben</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Jost:wght@200;300;400&display=swap" rel="stylesheet">
  <link rel="preload" href="style.css" as="style">
  <script>if(localStorage.getItem('lb_pw'))document.documentElement.classList.add('cached');</script>
  <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--amber:#C8985A;--forest:#4A5320;--cream:#F6EFE0}}
    body{{font-family:'Jost',sans-serif;background:var(--forest);min-height:100svh;display:flex;align-items:center;justify-content:center;-webkit-font-smoothing:antialiased}}
    html.cached .gate{{display:none}}
    .gate{{text-align:center;padding:clamp(40px,8vw,80px) clamp(28px,6vw,60px);max-width:500px;width:100%;transition:opacity 0.4s ease}}
    .gate.fade-out{{opacity:0;pointer-events:none}}
    .gate-names{{font-family:'Cormorant Garamond',serif;font-size:clamp(2.4rem,7vw,4rem);font-weight:300;color:#fff;letter-spacing:0.06em;line-height:1.05;white-space:nowrap}}
    .gate-amp{{color:var(--amber);font-style:italic}}
    .gate-rule{{width:44px;height:1px;background:var(--amber);margin:20px auto;opacity:0.6}}
    .gate-date{{font-family:'Cinzel',serif;font-size:clamp(0.62rem,1.4vw,0.78rem);letter-spacing:0.18em;color:rgba(255,255,255,0.55);margin-bottom:40px;white-space:nowrap}}
    .gate-label{{font-size:0.72rem;letter-spacing:0.18em;color:rgba(255,255,255,0.45);margin-bottom:16px;text-transform:uppercase}}
    .gate-input-wrap{{position:relative;margin-bottom:14px}}
    .gate-input{{width:100%;padding:14px 18px;background:rgba(255,255,255,0.07);border:1px solid rgba(200,152,90,0.35);border-radius:8px;color:#fff;font-family:'Jost',sans-serif;font-size:1rem;font-weight:300;letter-spacing:0.08em;text-align:center;outline:none;transition:border-color 0.2s,background 0.2s;-webkit-appearance:none}}
    .gate-input::placeholder{{color:rgba(255,255,255,0.25)}}
    .gate-input:focus{{border-color:var(--amber);background:rgba(255,255,255,0.11)}}
    .gate-input.error{{animation:shake 0.4s ease;border-color:#e07070}}
    @keyframes shake{{0%,100%{{transform:translateX(0)}}20%{{transform:translateX(-6px)}}40%{{transform:translateX(6px)}}60%{{transform:translateX(-4px)}}80%{{transform:translateX(4px)}}}}
    .gate-btn{{width:100%;padding:14px;background:var(--amber);border:none;border-radius:8px;color:var(--forest);font-family:'Cinzel',serif;font-size:0.78rem;letter-spacing:0.22em;cursor:pointer;transition:opacity 0.2s,transform 0.15s;font-weight:500}}
    .gate-btn:hover{{opacity:0.9;transform:translateY(-1px)}}
    .gate-btn:disabled{{opacity:0.5;cursor:default;transform:none}}
    .gate-error{{margin-top:14px;font-size:0.75rem;color:rgba(255,120,120,0.85);letter-spacing:0.05em;min-height:20px}}
  </style>
</head>
<body>
  <div class="gate" id="gate">
    <div class="gate-names">Leah <span class="gate-amp">&amp;</span> Ben</div>
    <div class="gate-rule"></div>
    <div class="gate-date">August 15, 2026 &nbsp;&middot;&nbsp; Montclair, New Jersey</div>
    <div class="gate-label">Enter password to continue</div>
    <div class="gate-input-wrap">
      <input class="gate-input" id="pw" type="password" placeholder="Password" autocomplete="current-password" autofocus/>
    </div>
    <button class="gate-btn" id="btn" onclick="unlock()">Enter</button>
    <div class="gate-error" id="err"></div>
  </div>

  <script>
    const SALT = '{S}';
    const IV   = '{I}';
    const CT   = '{C}';
    const ITER = {ITER};

    function b64ToBytes(b64){{const bin=atob(b64);return Uint8Array.from(bin,c=>c.charCodeAt(0))}}

    async function tryDecrypt(pw){{
      const km=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
      const key=await crypto.subtle.deriveKey({{name:'PBKDF2',salt:b64ToBytes(SALT),iterations:ITER,hash:'SHA-256'}},km,{{name:'AES-GCM',length:256}},false,['decrypt']);
      const dec=await crypto.subtle.decrypt({{name:'AES-GCM',iv:b64ToBytes(IV)}},key,b64ToBytes(CT));
      return new TextDecoder().decode(dec);
    }}

    function swapToSite(html, animate){{
      sessionStorage.setItem('lb_unlocked','1');
      sessionStorage.setItem('lb_from_gate','1');
      function doSwap(){{
        const parser=new DOMParser();
        const newDoc=parser.parseFromString(html,'text/html');
        document.documentElement.style.background='#4A5320';
        document.head.innerHTML=newDoc.head.innerHTML;
        document.body.innerHTML=newDoc.body.innerHTML;
        Array.from(document.body.querySelectorAll('script')).forEach(function(el){{
          const s=document.createElement('script');
          Array.from(el.attributes).forEach(function(a){{s.setAttribute(a.name,a.value)}});
          s.textContent=el.textContent;
          el.parentNode.replaceChild(s,el);
        }});
      }}
      if(animate){{
        document.getElementById('gate').classList.add('fade-out');
        setTimeout(doSwap,400);
      }}else{{
        doSwap();
      }}
    }}

    // Auto-unlock from cached password (gate hidden via html.cached CSS)
    (async function(){{
      const cached=localStorage.getItem('lb_pw');
      if(cached){{
        try{{
          const html=await tryDecrypt(cached);
          swapToSite(html,false);
          return;
        }}catch(e){{
          localStorage.removeItem('lb_pw');
          document.documentElement.classList.remove('cached');
        }}
      }}
    }})();

    async function unlock(){{
      const pw=document.getElementById('pw').value;
      if(!pw)return;
      const btn=document.getElementById('btn'),err=document.getElementById('err'),input=document.getElementById('pw');
      btn.disabled=true;err.textContent='';
      try{{
        const html=await tryDecrypt(pw);
        localStorage.setItem('lb_pw',pw);
        swapToSite(html,true);
      }}catch(e){{
        input.classList.add('error');
        setTimeout(()=>input.classList.remove('error'),500);
        err.textContent='Incorrect password. Please try again.';
        btn.disabled=false;input.value='';input.focus();
      }}
    }}
    document.addEventListener('keydown',e=>{{if(e.key==='Enter')unlock()}});
  </script>
</body>
</html>'''


def main():
    # 1. Assemble index (no auth check — gate handles auth)
    index_html = assemble('index.html')
    index_out = ROOT / 'index-unprotected.html'
    index_out.write_text(index_html)
    print(f'  index-unprotected.html  ({len(index_html)/1024:.1f} KB)')

    # 2. Assemble RSVP (with auth check)
    auth = '  <script>if(!sessionStorage.getItem("lb_unlocked")&&!localStorage.getItem("lb_pw"))window.location.replace("index.html");</script>\n'
    rsvp_html = assemble('rsvp.html', auth_check=auth)
    rsvp_out = ROOT / 'rsvp.html'
    rsvp_out.write_text(rsvp_html)
    print(f'  rsvp.html               ({len(rsvp_html)/1024:.1f} KB)')

    # 3. Assemble Travel (with auth check)
    travel_html = assemble('travel.html', auth_check=auth)
    travel_out = ROOT / 'travel.html'
    travel_out.write_text(travel_html)
    print(f'  travel.html             ({len(travel_html)/1024:.1f} KB)')

    # 4. Encrypt index into gate page
    gate_html = encrypt_page(index_html)
    gate_out = ROOT / 'index.html'
    gate_out.write_text(gate_html)
    print(f'  index.html (gate)       ({len(gate_html)/1024:.1f} KB)')

    print('\nBuild complete!')


if __name__ == '__main__':
    main()
