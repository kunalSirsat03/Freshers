from pathlib import Path
p = Path(r"d:\Freshers\templates\fresher_cinematic.html")
t = p.read_text(encoding="utf-8")
old_css = """    .hero{position:relative;min-height:740px;height:100svh;max-height:1040px;display:flex;align-items:flex-end;overflow:hidden;background:linear-gradient(180deg,#f6f0ee 0%,#f4efee 100%)}.hero-media,.hero-shade,.hero-texture{position:absolute;inset:0}.hero-media{inset:auto 60px 60px auto;width:min(42vw,560px);height:min(72vh,620px);border-radius:30px;overflow:hidden;box-shadow:0 26px 60px rgba(21,18,28,.18);border:1px solid rgba(255,255,255,.55);background:#ddd}.hero-media img{width:100%;height:100%;object-fit:cover;object-position:center;animation:hero-drift 24s ease-in-out infinite alternate}.hero-shade{background:linear-gradient(90deg,rgba(246,240,238,.9) 0%,rgba(246,240,238,.78) 48%,rgba(246,240,238,.2) 100%);display:block}.hero-shade:after{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 70% 34%,rgba(228,53,94,.12),transparent 34%)}.hero-texture{opacity:.12;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(255,255,255,.38) 4px,transparent 5px);mix-blend-mode:soft-light}.hero-content{position:relative;z-index:1;padding-top:130px;padding-bottom:74px}.hero-kicker,.eyebrow{display:flex;align-items:center;gap:12px;font-size:10px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--ink)}.hero-kicker{padding:10px 18px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.35);display:inline-flex}.hero-kicker:before{content:'';display:block;width:34px;height:2px;background:var(--red)}.hero-title{max-width:940px;margin:22px 0 20px;font:900 112px/.78 var(--display);text-transform:uppercase;letter-spacing:0;color:var(--ink)}.hero-title span{display:block;color:var(--red)}.hero-bottom{display:grid;grid-template-columns:minmax(220px,1fr) auto;gap:40px;align-items:end;max-width:1000px}.hero-description{max-width:470px;margin:0 0 22px;color:var(--muted);font-size:15px}.hero-meta{display:flex;flex-wrap:wrap;gap:0;margin-top:28px;border-top:1px solid var(--line);max-width:840px}.meta-item{flex:1 1 170px;border:1px solid var(--line);padding:18px 18px 12px;border-top:0;border-left:0;background:rgba(255,255,255,.26)}.meta-item:nth-child(3n+1){border-left:1px solid var(--line)}.meta-item small{display:block;font-size:10px;letter-spacing:1.8px;text-transform:uppercase;color:var(--muted)}.meta-item strong{display:block;margin-top:8px;font:700 26px/1.1 var(--display);letter-spacing:-.03em;color:var(--ink)}.hero-actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:22px}.countdown{display:flex;align-items:flex-end;gap:14px;padding-top:18px}.countdown-unit{min-width:86px;padding:12px 10px 10px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.26);text-align:center}.countdown-unit b{display:block;font:800 38px/1 var(--display);letter-spacing:-.03em;color:var(--red)}.countdown-unit small{display:block;margin-top:4px;font-size:9px;letter-spacing:1.7px;text-transform:uppercase;color:var(--muted)}.hero-index{position:absolute;right:calc((100% - var(--content))/2 + 24px);bottom:26px;font:900 200px/.74 var(--display);letter-spacing:-.05em;color:rgba(23,27,34,.06);pointer-events:none}"""
new_css = """    .hero{position:relative;min-height:760px;height:100svh;max-height:1040px;display:flex;align-items:flex-end;overflow:hidden;background:linear-gradient(180deg,#f5efee 0%,#f3efee 100%)}.hero-media,.hero-shade,.hero-texture{position:absolute;inset:0}.hero-media{display:none}.hero-shade{background:linear-gradient(90deg,rgba(245,239,238,.96) 0%,rgba(245,239,238,.9) 42%,rgba(245,239,238,.18) 100%)}.hero-shade:after{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 70% 34%,rgba(228,53,94,.10),transparent 32%)}.hero-texture{opacity:.13;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(255,255,255,.38) 4px,transparent 5px);mix-blend-mode:soft-light}.hero-inner{position:relative;z-index:1;display:grid;grid-template-columns:1.1fr .9fr;align-items:center;gap:56px;padding-top:150px;padding-bottom:70px}.hero-copy{display:flex;flex-direction:column;align-items:flex-start}.hero-kicker,.eyebrow{display:flex;align-items:center;gap:12px;font-size:10px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--ink)}.hero-kicker{padding:10px 18px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.35);display:inline-flex;margin-bottom:14px}.hero-kicker:before{content:'';display:block;width:34px;height:2px;background:var(--red)}.hero-title{margin:0;font:900 140px/.72 var(--display);text-transform:uppercase;letter-spacing:-2px;color:var(--red)}.hero-title small{display:block;font-size:28px;letter-spacing:8px;color:var(--ink);font-weight:800;line-height:1}.hero-subtitle{margin:18px 0 0;color:var(--muted);font-size:18px;line-height:1.6;max-width:420px}.hero-meta{display:flex;flex-wrap:wrap;gap:14px;margin-top:26px}.meta-card{min-width:84px;padding:10px 12px 8px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.26);text-align:center}.meta-card strong{display:block;font:800 38px/1 var(--display);color:var(--red)}.meta-card span{display:block;margin-top:5px;font-size:10px;letter-spacing:1.8px;text-transform:uppercase;color:var(--muted)}.ticket-panel{display:flex;align-items:center;gap:10px;margin-top:22px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.34);max-width:320px}.ticket-panel .ticket-price{font:800 28px/1 var(--display);color:var(--red)}.ticket-panel small{font-size:13px;color:var(--muted)}.hero-actions{display:flex;flex-wrap:wrap;gap:14px;margin-top:26px}.hero-visual{display:flex;justify-content:center;align-items:center;position:relative}.hero-poster-wrap{position:relative;padding:18px 18px 12px;display:flex;justify-content:center}.hero-poster{position:relative;width:min(100%,430px);min-height:500px;border-radius:22px;overflow:hidden;border:1px solid rgba(255,255,255,.22);box-shadow:0 36px 60px rgba(30,20,20,.12);background:linear-gradient(180deg,#1d101c 0%,#07090f 100%)}.hero-poster-badge{position:absolute;right:24px;top:18px;z-index:2;padding:8px 16px;border-radius:999px;background:rgba(251,249,249,.88);color:var(--ink);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,.08)}.hero-poster-image{position:absolute;inset:0;background:linear-gradient(180deg,rgba(22,18,35,.04),rgba(9,8,17,.42)),url('https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1200&q=80') center/cover no-repeat;filter:grayscale(.2) saturate(1.15) contrast(1.1)}.hero-poster::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 18%,rgba(255,95,146,.52),rgba(255,95,146,0) 24%),linear-gradient(135deg,rgba(34,206,255,.18),rgba(255,196,87,.08) 32%,rgba(0,0,0,.06) 70%,rgba(0,0,0,.52));z-index:1}.hero-poster-content{position:absolute;left:0;right:0;bottom:0;padding:24px 22px 18px;z-index:2;background:linear-gradient(180deg,rgba(10,11,16,0),rgba(5,7,13,.82) 53%,rgba(5,7,13,.96));color:white}.hero-poster-content h3{margin:0;font:800 34px/1.05 var(--display);text-transform:none;letter-spacing:-1px}.hero-poster-content p{margin:8px 0 0;color:rgba(255,255,255,.78);font-size:13px;letter-spacing:.2px}.hero-content{display:none}.hero-index{display:none}.hero-bottom{display:none}.countdown{display:none}.meta-item{display:none}"""
if old_css not in t:
    raise SystemExit('old_css not found')
t = t.replace(old_css, new_css, 1)
start = t.index('  <section class="hero" id="home">')
end = t.index('  <section class="section section-red" id="about">', start)
replacement = '''  <section class="hero" id="home">
    <div class="hero-media" aria-hidden="true">{% if event.poster_image %}<img src="{{ event.poster_image.url }}" alt="">{% elif event.hero_image %}<img src="{{ event.hero_image.url }}" alt="">{% elif gallery %}<img src="{{ gallery.0.display_url }}" alt="">{% endif %}</div>
    <div class="hero-shade"></div>
    <div class="hero-texture"></div>
    <div class="container hero-inner">
      <div class="hero-copy" data-reveal>
        <div class="hero-kicker">{{ event.organizer_name|default:"Department of Engineering" }}</div>
        <h1 class="hero-title">{{ event.title|default:"Unofficial" }}<small>FRESHERS</small></h1>
        <p class="hero-subtitle">A party everyone remembers.</p>

        <div class="hero-meta" aria-label="Event information">
          <div class="meta-card"><strong>13</strong><span>Days</span></div>
          <div class="meta-card"><strong>19</strong><span>Hours</span></div>
          <div class="meta-card"><strong>15</strong><span>Minutes</span></div>
          <div class="meta-card"><strong>39</strong><span>Seconds</span></div>
        </div>

        <div class="ticket-panel" aria-label="Ticket detail">
          <span class="ticket-price">₹{{ event.ticket_price }}</span>
          <small>Entry pass · buffet included</small>
        </div>

        <div class="hero-actions">
          {% if event.registration_url %}
            <a class="cta" href="{{ event.registration_url }}" target="_blank" rel="noopener">Register now <span class="arrow" aria-hidden="true">&rarr;</span></a>
          {% endif %}
          <a class="cta cta-outline" href="#about">Explore the night</a>
        </div>
      </div>

      <div class="hero-visual" data-reveal>
        <div class="hero-poster-wrap">
          <div class="hero-poster">
            <div class="hero-poster-badge">One night only</div>
            <div class="hero-poster-image" aria-hidden="true"></div>
            <div class="hero-poster-content">
              <h3>Make it a night.</h3>
              <p>Music · Dinner · New memories</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
'''
t = t[:start] + replacement + t[end:]
p.write_text(t, encoding='utf-8')
print('updated')
