from core.schema import PortfolioProfile


THEMES = {
    # ---------- DARK 1: gradient hero + side facts card (inspired by dark analytics-style portfolios) ----------
    "aurora": {
        "label": "Aurora",
        "mode": "dark",
        "google_fonts": "family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600",
        "font_disp": "'Space Grotesk','Inter',sans-serif",
        "font_body": "'Inter',sans-serif",
        "bg": "#0B0E1A", "surface": "#121628", "surface2": "#171C33",
        "ink": "#F3F2FF", "ink_soft": "#B4B1DA", "ink_faint": "#6E6B96",
        "line": "#242A48",
        "accent": "#8B7CF6", "accent2": "#34D8B0",
        "radius": "16px",
        "split_hero": True, "numbered": False, "gradient_text": True, "avatar": False,
    },
    # ---------- DARK 2: monospace, numbered sections, lime accent (inspired by brutalist dev portfolios) ----------
    "terminal": {
        "label": "Terminal",
        "mode": "dark",
        "google_fonts": "family=JetBrains+Mono:wght@400;500;700",
        "font_disp": "'JetBrains Mono',monospace",
        "font_body": "'JetBrains Mono',monospace",
        "bg": "#0A0A0A", "surface": "#121212", "surface2": "#171717",
        "ink": "#F2F2F0", "ink_soft": "#9A9A96", "ink_faint": "#5C5C58",
        "line": "#2A2A28",
        "accent": "#D6FF3F", "accent2": "#7DFFE0",
        "radius": "6px",
        "split_hero": False, "numbered": True, "gradient_text": False, "avatar": False,
    },
    # ---------- LIGHT 1: warm, editorial, coral accent (inspired by warm creative portfolios) ----------
    "sunset": {
        "label": "Sunset",
        "mode": "light",
        "google_fonts": "family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600",
        "font_disp": "'Poppins','Inter',sans-serif",
        "font_body": "'Inter',sans-serif",
        "bg": "#FBF3EE", "surface": "#FFFFFF", "surface2": "#FFF7F2",
        "ink": "#2B2320", "ink_soft": "#7A6E67", "ink_faint": "#B5A89F",
        "line": "#F0DED2",
        "accent": "#E1573C", "accent2": "#F2A65A",
        "radius": "18px",
        "split_hero": False, "numbered": False, "gradient_text": False, "avatar": True,
    },
    # ---------- LIGHT 2: muted, graphite, minimal serif (inspired by studio/agency portfolios) ----------
    "studio": {
        "label": "Studio",
        "mode": "light",
        "google_fonts": "family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600",
        "font_disp": "'Fraunces','Inter',serif",
        "font_body": "'Inter',sans-serif",
        "bg": "#F3F2EF", "surface": "#FFFFFF", "surface2": "#FAFAF8",
        "ink": "#201F1C", "ink_soft": "#69675F", "ink_faint": "#A6A399",
        "line": "#E4E1DA",
        "accent": "#9C6B3F", "accent2": "#5F6B5A",
        "radius": "4px",
        "split_hero": False, "numbered": False, "gradient_text": False, "avatar": True,
    },
}


def _initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def render_portfolio_html(profile: PortfolioProfile, theme: str = "aurora") -> str:
    """
    Accepts a profile and compiles a complete, responsive portfolio website.
    Supports 4 visually distinct themes: 'aurora' and 'terminal' (dark),
    'sunset' and 'studio' (light).
    """
    t = THEMES.get(theme, THEMES["aurora"])
    on_accent = "#0A0A0A" if t["mode"] == "dark" else "#FFFFFF"

    def esc(s):
        return s if s else ""

    # ---- Skill badges ----
    skills_html = "".join(f'<span class="badge">{s}</span>' for s in profile.skills)

    # ---- Projects ----
    accent_cycle = [t["accent"], t["accent2"]]
    project_blocks = ""
    for i, proj in enumerate(profile.projects):
        stripe = accent_cycle[i % 2]
        tech_badges = "".join(f'<span class="badge sm">{tech}</span>' for tech in proj.tech_stack)
        github_link = (
            f'<a href="{proj.github_url}" target="_blank" class="proj-link">'
            f'<span>Source</span><span class="arrow">&rarr;</span></a>'
            if proj.github_url else ""
        )
        label = f'<span class="proj-num">{i + 1:02d}</span>' if t["numbered"] else ""
        project_blocks += f"""
        <div class="card proj-card reveal" style="--stripe:{stripe};transition-delay:{(i % 4) * 60}ms">
            <div class="proj-head">{label}<h3>{proj.title}</h3></div>
            <p class="proj-desc">{proj.description}</p>
            <div class="proj-foot">
                <div class="badge-row">{tech_badges}</div>
                {github_link}
            </div>
        </div>
        """

    # ---- Experience timeline ----
    experience_blocks = ""
    for exp in profile.experience:
        highlights = "".join(f"<li>{h}</li>" for h in exp.highlights)
        experience_blocks += f"""
        <div class="timeline-item reveal">
            <div class="timeline-row">
                <h3>{exp.position}</h3>
                <span class="meta">{exp.duration}</span>
            </div>
            <p class="sub">{exp.company} &middot; {exp.location}</p>
            <ul class="highlights">{highlights}</ul>
        </div>
        """

    # ---- Education timeline ----
    education_blocks = ""
    for edu in profile.education:
        details = f'<p class="edu-detail">{edu.details}</p>' if edu.details else ""
        education_blocks += f"""
        <div class="timeline-item reveal">
            <div class="timeline-row">
                <h3>{edu.degree}</h3>
                <span class="meta">{edu.duration}</span>
            </div>
            <p class="sub">{edu.institution}</p>
            {details}
        </div>
        """

    # ---- Certifications (only rendered when present on the resume) ----
    certification_blocks = ""
    for cert in profile.certifications:
        date_html = f'<span class="meta">{cert.date}</span>' if cert.date else ""
        certification_blocks += f"""
        <div class="timeline-item reveal">
            <div class="timeline-row">
                <h3>{cert.name}</h3>
                {date_html}
            </div>
            <p class="sub">{cert.issuer}</p>
        </div>
        """

    # ---- Volunteer work (only rendered when present on the resume) ----
    volunteer_blocks = ""
    for vol in profile.volunteer_work:
        desc_html = f'<p class="edu-detail">{vol.description}</p>' if vol.description else ""
        volunteer_blocks += f"""
        <div class="timeline-item reveal">
            <div class="timeline-row">
                <h3>{vol.role}</h3>
                <span class="meta">{vol.duration}</span>
            </div>
            <p class="sub">{vol.organization}</p>
            {desc_html}
        </div>
        """

    linkedin_html = f'<a href="{profile.linkedin}" target="_blank" class="link">LinkedIn</a>' if profile.linkedin else ""
    github_html = f'<a href="{profile.github}" target="_blank" class="link">GitHub</a>' if profile.github else ""

    # ---- Section eyebrow helper (numbered vs plain) ----
    def eyebrow(idx, text):
        if t["numbered"]:
            return f'<div class="eyebrow"><span class="idx">{idx:02d}</span> &mdash; {text.upper()}</div>'
        return f'<div class="eyebrow"><span class="eyebrow-dot"></span>{text.upper()}</div>'

    # ---- Hero ----
    name_html = (
        f'<span class="grad">{profile.name}</span>' if t["gradient_text"] else profile.name
    )
    avatar_html = (
        f'<div class="avatar">{_initials(profile.name)}</div>' if t["avatar"] else ""
    )

    if t["split_hero"]:
        top_skills = " &middot; ".join(profile.skills[:3]) if profile.skills else ""
        first_edu = profile.education[0] if profile.education else None
        hero_html = f"""
        <section class="hero split reveal">
            <div class="hero-glow"></div>
            <div class="hero-main">
                {eyebrow(0, "Portfolio")}
                <h1>{name_html}</h1>
                <p class="headline">{profile.headline}</p>
                <p class="bio">{profile.bio}</p>
                <div class="cta-row">
                    <a href="mailto:{profile.email}" class="btn-primary">Contact me</a>
                    {linkedin_html}
                    {github_html}
                </div>
            </div>
            <div class="facts-card">
                {f'<div class="fact"><span class="fact-label">Degree</span><span class="fact-value">{first_edu.degree}</span></div>' if first_edu else ""}
                {f'<div class="fact"><span class="fact-label">Institution</span><span class="fact-value">{first_edu.institution}</span></div>' if first_edu else ""}
                <div class="fact"><span class="fact-label">Projects</span><span class="fact-value">{len(profile.projects)}</span></div>
                <div class="fact"><span class="fact-label">Focus</span><span class="fact-value">{top_skills}</span></div>
            </div>
        </section>
        """
    else:
        hero_html = f"""
        <section class="hero reveal">
            <div class="hero-glow"></div>
            {avatar_html}
            {eyebrow(0, "Portfolio")}
            <h1>{name_html}</h1>
            <p class="headline">{profile.headline}</p>
            <p class="bio">{profile.bio}</p>
            <div class="cta-row">
                <a href="mailto:{profile.email}" class="btn-primary">Contact me</a>
                {linkedin_html}
                {github_html}
            </div>
        </section>
        """

    education_section = f"""
    <section class="block reveal">
        {eyebrow(4, "Education")}
        <h2>Education</h2>
        <div class="timeline">{education_blocks}</div>
    </section>
    """ if profile.education else ""

    certifications_section = f"""
    <section class="block reveal">
        {eyebrow(5, "Certifications")}
        <h2>Certifications</h2>
        <div class="timeline">{certification_blocks}</div>
    </section>
    """ if profile.certifications else ""

    volunteer_section = f"""
    <section class="block reveal">
        {eyebrow(6, "Volunteer work")}
        <h2>Volunteer work</h2>
        <div class="timeline">{volunteer_blocks}</div>
    </section>
    """ if profile.volunteer_work else ""

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{profile.name} | Portfolio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?{t['google_fonts']}&display=swap" rel="stylesheet">
<style>
  :root{{
    --bg:{t['bg']}; --surface:{t['surface']}; --surface2:{t['surface2']};
    --ink:{t['ink']}; --ink-soft:{t['ink_soft']}; --ink-faint:{t['ink_faint']};
    --line:{t['line']}; --accent:{t['accent']}; --accent2:{t['accent2']};
    --radius:{t['radius']};
    --font-disp:{t['font_disp']}; --font-body:{t['font_body']};
    --on-accent:{on_accent};
    --glow: color-mix(in srgb, var(--accent) 32%, transparent);
    --glow-soft: color-mix(in srgb, var(--accent) 14%, transparent);
    --tint: color-mix(in srgb, var(--accent) 10%, var(--surface));
    --ease: cubic-bezier(.16,.84,.44,1);
  }}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);line-height:1.6;overflow-x:hidden;
    background-image:radial-gradient(color-mix(in srgb, var(--line) 70%, transparent) 1px, transparent 1px);
    background-size:28px 28px;}}
  ::selection{{background:var(--accent);color:var(--on-accent)}}
  h1,h2,h3{{font-family:var(--font-disp);letter-spacing:-.02em;margin:0}}
  a{{color:inherit}}
  .wrap{{max-width:880px;margin:0 auto;padding:0 24px;position:relative}}

  .reveal{{opacity:0;transform:translateY(18px);transition:opacity .7s var(--ease),transform .7s var(--ease)}}
  .reveal.in-view{{opacity:1;transform:none}}

  #exportHUD{{position:sticky;top:0;z-index:50;background:color-mix(in srgb, var(--surface2) 88%, transparent);
    backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
    border-bottom:1px solid var(--line);
    display:flex;align-items:center;justify-content:space-between;padding:12px 24px;font-family:var(--font-body)}}
  #exportHUD .status{{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--ink-soft)}}
  #exportHUD .dot{{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px var(--glow-soft);
    animation:pulse 2.2s ease-in-out infinite}}
  @keyframes pulse{{0%,100%{{box-shadow:0 0 0 3px var(--glow-soft)}}50%{{box-shadow:0 0 0 6px var(--glow-soft)}}}}
  #exportHUD button{{font-size:12px;font-weight:600;border:1px solid var(--line);background:var(--surface);
    color:var(--ink);padding:8px 14px;border-radius:8px;cursor:pointer;margin-left:8px;font-family:var(--font-body);
    transition:transform .2s var(--ease),border-color .2s,background .2s}}
  #exportHUD button:hover{{transform:translateY(-1px);border-color:var(--accent)}}
  #exportHUD button.primary{{background:var(--accent);color:var(--on-accent);border:none;
    box-shadow:0 4px 14px -4px var(--glow)}}
  #exportHUD button.primary:hover{{box-shadow:0 6px 20px -4px var(--glow);filter:brightness(1.05)}}

  .eyebrow{{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;letter-spacing:.1em;
    text-transform:uppercase;color:var(--accent);margin-bottom:14px}}
  .eyebrow .idx{{color:var(--ink-faint);margin-right:2px}}
  .eyebrow-dot{{width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px var(--glow-soft);
    flex:none}}

  .hero{{padding:72px 0 44px;position:relative;overflow:hidden}}
  .hero-glow{{position:absolute;top:-140px;right:-120px;width:420px;height:420px;border-radius:50%;
    background:radial-gradient(circle, var(--accent) 0%, transparent 70%);opacity:.18;filter:blur(50px);
    pointer-events:none;z-index:0}}
  .hero > *:not(.hero-glow){{position:relative;z-index:1}}
  .hero h1{{font-size:clamp(32px,5vw,44px);font-weight:700;margin-bottom:10px}}
  .hero .grad{{background:linear-gradient(100deg,var(--accent),var(--accent2));-webkit-background-clip:text;
    background-clip:text;color:transparent;background-size:200% auto;animation:sheen 6s ease-in-out infinite}}
  @keyframes sheen{{0%,100%{{background-position:0% 50%}}50%{{background-position:100% 50%}}}}
  .headline{{font-size:18px;color:var(--ink-soft);font-weight:500;margin:0 0 16px}}
  .bio{{font-size:15px;color:var(--ink-soft);max-width:560px;margin:0 0 24px}}
  .cta-row{{display:flex;gap:18px;align-items:center;flex-wrap:wrap}}
  .btn-primary{{background:var(--accent);color:var(--on-accent);font-weight:600;
    padding:12px 22px;border-radius:calc(var(--radius) - 4px);text-decoration:none;font-size:14px;
    display:inline-flex;align-items:center;box-shadow:0 4px 14px -4px var(--glow);
    transition:transform .25s var(--ease),box-shadow .25s var(--ease),filter .25s}}
  .btn-primary:hover{{transform:translateY(-3px);box-shadow:0 10px 24px -6px var(--glow);filter:brightness(1.05)}}
  .link{{font-size:14px;font-weight:500;color:var(--ink-soft);text-decoration:none;position:relative;padding-bottom:2px}}
  .link::after{{content:'';position:absolute;left:0;bottom:0;width:0;height:1px;background:var(--accent);
    transition:width .25s var(--ease)}}
  .link:hover{{color:var(--accent)}}
  .link:hover::after{{width:100%}}
  .avatar{{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));
    color:var(--on-accent);display:flex;align-items:center;justify-content:center;font-family:var(--font-disp);
    font-weight:600;font-size:18px;margin-bottom:18px;box-shadow:0 6px 20px -6px var(--glow);
    transition:transform .3s var(--ease)}}
  .avatar:hover{{transform:rotate(-6deg) scale(1.05)}}

  .hero.split{{display:grid;grid-template-columns:1.5fr 1fr;gap:32px;align-items:start}}
  @media(max-width:720px){{.hero.split{{grid-template-columns:1fr}}}}
  .facts-card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;
    margin-top:10px;transition:border-color .3s var(--ease),box-shadow .3s var(--ease),transform .3s var(--ease)}}
  .facts-card:hover{{border-color:var(--accent);box-shadow:0 14px 30px -12px var(--glow);transform:translateY(-3px)}}
  .fact{{display:flex;flex-direction:column;gap:2px;padding:12px 6px;border-bottom:1px solid var(--line);
    border-radius:8px;margin:0 -6px;transition:background .25s var(--ease),padding-left .25s var(--ease)}}
  .fact:hover{{background:var(--tint);padding-left:12px}}
  .fact:last-child{{border-bottom:none;padding-bottom:0}}
  .fact-label{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-faint)}}
  .fact-value{{font-size:14px;font-weight:600}}

  .block{{padding:40px 0}}
  .block h2{{font-size:clamp(22px,3vw,26px);font-weight:700;margin-bottom:18px}}

  .badge-row{{display:flex;flex-wrap:wrap;gap:8px}}
  .badge{{font-size:12px;font-weight:500;padding:6px 13px;border-radius:100px;background:var(--surface2);
    border:1px solid var(--line);color:var(--ink-soft);transition:transform .2s var(--ease),background .2s,
    border-color .2s,color .2s;cursor:default}}
  .badge:hover{{transform:translateY(-2px);background:var(--tint);border-color:var(--accent);color:var(--ink)}}
  .badge.sm{{padding:3px 9px;font-size:11px}}

  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
  @media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
  .card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;
    position:relative;overflow:hidden;
    transition:transform .35s var(--ease),border-color .35s var(--ease),box-shadow .35s var(--ease)}}
  .card::before{{content:'';position:absolute;inset:0;border-radius:inherit;padding:1px;
    background:linear-gradient(135deg,var(--accent),transparent 60%);opacity:0;transition:opacity .35s var(--ease);
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none}}
  .card:hover{{transform:translateY(-6px);border-color:var(--accent);box-shadow:0 20px 40px -20px var(--glow)}}
  .card:hover::before{{opacity:1}}
  .proj-card{{border-top:3px solid var(--stripe);display:flex;flex-direction:column;justify-content:space-between}}
  .proj-head{{display:flex;align-items:baseline;gap:10px;margin-bottom:8px}}
  .proj-num{{font-size:12px;color:var(--ink-faint);font-weight:600}}
  .proj-head h3{{font-size:17px;font-weight:600}}
  .proj-desc{{font-size:13.5px;color:var(--ink-soft);margin-bottom:16px}}
  .proj-foot{{display:flex;flex-direction:column;gap:10px}}
  .proj-link{{font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;display:inline-flex;
    align-items:center;gap:5px}}
  .proj-link .arrow{{display:inline-block;transition:transform .25s var(--ease)}}
  .proj-link:hover .arrow{{transform:translateX(4px)}}

  .timeline{{display:flex;flex-direction:column;gap:8px}}
  .timeline-item{{position:relative;border-left:2px solid var(--line);padding:14px 16px 14px 22px;
    border-radius:0 10px 10px 0;transition:border-color .3s var(--ease),background .3s var(--ease)}}
  .timeline-item::before{{content:'';position:absolute;left:-7px;top:18px;width:12px;height:12px;border-radius:50%;
    background:var(--bg);border:2px solid var(--ink-faint);transition:border-color .3s var(--ease),
    background .3s var(--ease),box-shadow .3s var(--ease)}}
  .timeline-item:hover{{border-left-color:var(--accent);background:var(--tint)}}
  .timeline-item:hover::before{{border-color:var(--accent);background:var(--accent);box-shadow:0 0 0 4px var(--glow-soft)}}
  .timeline-row{{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}}
  .timeline-row h3{{font-size:17px;font-weight:600}}
  .meta{{font-size:12px;color:var(--ink-faint);font-weight:500;white-space:nowrap}}
  .sub{{font-size:13.5px;color:var(--ink-soft);margin:4px 0 10px}}
  .highlights{{margin:0;padding-left:18px;font-size:13.5px;color:var(--ink-soft)}}
  .highlights li{{margin-bottom:5px}}
  .edu-detail{{font-size:12.5px;color:var(--ink-faint);font-style:italic;margin:4px 0 0}}

  footer{{padding:44px 0 60px;font-size:12px;color:var(--ink-faint);border-top:1px solid var(--line);margin-top:20px;
    text-align:center}}
</style>
</head>
<body>

<div id="exportHUD">
    <div class="status"><span class="dot"></span>Live preview &middot; {t['label']} theme</div>
    <div>
        <button onclick="window.print()">Print PDF</button>
        <button class="primary" onclick="exportSourceFile()">Download site</button>
    </div>
</div>

<div class="wrap">
    {hero_html}

    <section class="block reveal">
        {eyebrow(1, "Skills")}
        <h2>Technical skills</h2>
        <div class="badge-row">{skills_html}</div>
    </section>

    <section class="block reveal">
        {eyebrow(2, "Selected work")}
        <h2>Projects</h2>
        <div class="grid">{project_blocks}</div>
    </section>

    <section class="block reveal">
        {eyebrow(3, "Experience")}
        <h2>Where I've worked</h2>
        <div class="timeline">{experience_blocks}</div>
    </section>

    {education_section}

    {certifications_section}

    {volunteer_section}

    <footer>Generated portfolio &middot; {profile.name}</footer>
</div>

<script>
    function exportSourceFile() {{
        const hud = document.getElementById("exportHUD");
        if (hud) hud.remove();
        const rawHtml = document.documentElement.outerHTML;
        const blob = new Blob([rawHtml], {{ type: "text/html" }});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "index.html";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        document.body.insertBefore(hud, document.body.firstChild);
    }}

    (function() {{
        const items = document.querySelectorAll(".reveal");
        if (!("IntersectionObserver" in window) || !items.length) {{
            items.forEach(el => el.classList.add("in-view"));
            return;
        }}
        const io = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add("in-view");
                    io.unobserve(entry.target);
                }}
            }});
        }}, {{ threshold: 0.12, rootMargin: "0px 0px -40px 0px" }});
        items.forEach(el => io.observe(el));
    }})();
</script>
</body>
</html>
"""
    return html_template