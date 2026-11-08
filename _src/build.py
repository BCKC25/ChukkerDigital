#!/usr/bin/env python3
"""Build the Chukker Digital site.

Run from the repo root:  python3 _src/build.py

It reads the partials and page bodies in _src/, fills in the shared header,
footer, SEO tags and structured data, and writes finished HTML to the repo
root (index.html, plans/index.html, ...) plus sitemap.xml and robots.txt.
GitHub Pages serves those files as-is. No dependencies beyond Python 3.
"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

SITE_URL = "https://chukkerdigital.com"
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
VERSION = datetime.date.today().strftime("%Y%m%d")

PHONE_DISPLAY = "(803) 770-7220"
PHONE_E164 = "+18037707220"
EMAIL = "j.lovett@chukkerdigital.com"

# ---------------------------------------------------------------------------
# Business details used in structured data (JSON-LD) on every page.
# ---------------------------------------------------------------------------
BUSINESS = {
    "@type": "ProfessionalService",
    "@id": f"{SITE_URL}/#business",
    "name": "Chukker Digital",
    "legalName": "Chukker Digital LLC",
    "url": f"{SITE_URL}/",
    "logo": f"{SITE_URL}/assets/img/icon-512.png",
    "image": f"{SITE_URL}/assets/img/og-image.png",
    "description": "Website care, local SEO and Google and Meta ad management for owner-run small businesses in Aiken, South Carolina, on flat monthly plans.",
    "telephone": PHONE_E164,
    "email": EMAIL,
    "priceRange": "$300–$2,000+ per month",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Aiken",
        "addressRegion": "SC",
        "addressCountry": "US",
    },
    "areaServed": [
        {"@type": "City", "name": "Aiken, SC"},
        {"@type": "City", "name": "North Augusta, SC"},
        {"@type": "City", "name": "Augusta, GA"},
        {"@type": "AdministrativeArea", "name": "Aiken County, SC"},
    ],
    "founder": {"@type": "Person", "name": "Josh Lovett"},
    "knowsAbout": [
        "Website maintenance", "Web design", "Local SEO",
        "Google Business Profile", "Google Ads", "Meta ads",
    ],
    "makesOffer": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Website care and maintenance"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Local SEO"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Google and Meta ad management"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Website design and builds"}},
    ],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": f"{SITE_URL}/#website",
    "url": f"{SITE_URL}/",
    "name": "Chukker Digital",
    "publisher": {"@id": f"{SITE_URL}/#business"},
    "inLanguage": "en-US",
}

# ---------------------------------------------------------------------------
# Plans: one source for the plan cards and the Offer structured data.
# ---------------------------------------------------------------------------
PLANS = [
    {
        "tier": "Tier 1", "name": "Maintain & Protect", "min": 300, "max": 500, "plus": False,
        "fit": "Your website works and customers already find you. You just don't have time to keep it updated and secure.",
        "items": ["Site upkeep and security updates", "Up to 5 small text and photo changes a month",
                  "Monthly Google Analytics check-in", "Broken-site fixes the same day"],
        "common": "Established shops, contractors and services that run on referrals.",
    },
    {
        "tier": "Tier 2", "name": "Grow & Optimize", "min": 800, "max": 1200, "plus": False,
        "fit": "People search \"near me\" for what you do, and your competitors show up first on Google Maps.",
        "items": ["Everything in Tier 1", "Local SEO and keyword targeting",
                  "2 new content pieces a month", "Weekly Google Business Profile posts"],
        "common": "Salons, studios, restaurants and local retail.",
    },
    {
        "tier": "Tier 3", "name": "The Complete Engine", "min": 1500, "max": 2000, "plus": True, "feature": True,
        "fit": "You have open spots on the calendar and want paid ads to fill them, with clear numbers on what each dollar brings back.",
        "items": ["Everything in Tier 2", "Google and Meta ad setup and management",
                  "Monthly ROI report: leads and bookings", "Ad spend paid by you, straight to Google and Meta"],
        "common": "Appointment-based businesses: fitness, wellness, med spa, home services.",
    },
]

BUILDS = [
    ("Starter Template Site", 1500, "Squarespace or Wix template site, up to 5 pages, built for phones first, with basic search setup."),
    ("Standard Custom Design", 2500, "Custom design around your brand, up to 10 pages, with Google Analytics and Business Profile set up."),
    ("Custom-Coded Hand-Built Site", 4000, "Coded from scratch with booking built into the site and built for speed on every device."),
    ("Booking and payments add-on", 300, "Connect Square, Mindbody, Vagaro or Calendly so customers can book and pay from your site."),
]

# ---------------------------------------------------------------------------
# FAQs: each list renders as the page's FAQ and as FAQPage structured data.
# Answers are plain HTML (links allowed).
# ---------------------------------------------------------------------------
FAQ = {
    "home": [
        ("What does Chukker Digital do?",
         "Chukker Digital looks after the online side of owner-run businesses in Aiken, SC: website upkeep and changes, local SEO and Google Business Profile management, and Google and Meta ads. You pick one flat monthly plan and one local person handles it."),
        ("How much does it cost?",
         "Monthly plans are $300–$500 for website care, $800–$1,200 to add local SEO and Google Business Profile management, and $1,500–$2,000+ to add Google and Meta ads. Your exact rate is set in a written quote after a free 15-minute audit. <a href=\"/plans/\">See the plans</a>."),
        ("How much does a new website cost in Aiken?",
         "Website builds are a one-time project, separate from the monthly plans: a template site from $1,500, a custom design from $2,500, or a hand-coded site from $4,000. <a href=\"/website-builds/\">See website builds</a>."),
        ("Do I own my website and accounts?",
         "Yes. Your website, domain and every Google and Meta account stay in your business's name. Chukker Digital is given access to work on them, never ownership."),
        ("Do you mark up ad spend?",
         "No. Ad spend is billed straight to your card by Google or Meta, and hosting is paid directly to your host. That money never passes through Chukker Digital."),
    ],
    "plans": [
        ("Which plan is right for my business?",
         "If your site works and customers already find you, Maintain &amp; Protect keeps it that way. If competitors show up ahead of you on Google Maps, Grow &amp; Optimize adds local SEO and Google Business Profile work. If you have open spots to fill and want paid ads, The Complete Engine adds Google and Meta ads. The free audit will point to one."),
        ("Is there a contract?",
         "Plans start with a 3-month period, because SEO and ads need time to show results. Your signed agreement lists your plan, monthly rate and payment terms."),
        ("Is ad spend included in the price?",
         "No. The plan price covers the work. Ad spend is paid by you directly to Google or Meta, and we never change your ad budget without your written OK."),
        ("What if I need something my plan doesn't cover?",
         "You'll get a written quote before any work starts, and nothing is billed without your approval. If you need that kind of work every month, moving up a plan is usually the better deal."),
        ("Can I change plans later?",
         "Yes. You can upgrade anytime, and the new rate starts with your next billing month."),
    ],
    "website-builds": [
        ("Is a website build included in a monthly plan?",
         "No. Designing a new site or rebuilding an old one is a separate, one-time cost, quoted in writing before any work starts. A monthly plan can start the month after launch."),
        ("How is a website build paid for?",
         "50% to start and 50% at launch. The site, domain and hosting are in your name."),
        ("Can you connect my booking system?",
         "Yes. Square, Mindbody, Vagaro or Calendly can be connected so customers book and pay right from your site, starting at $300."),
        ("Which option do I need?",
         "A template site suits a business that needs something clean and simple. A custom design suits a business with services, pricing, a gallery and a team to show. A hand-coded site is for something a template can't do, like your own booking flow built into the site."),
    ],
    "how-it-works": [
        ("Can I just text you a change?",
         "Texts are easy to lose, so you'll get a friendly reply asking you to send it through the Request Form, where it's tracked and gets a due date."),
        ("What happens if my site goes down?",
         "Mark the request \"Something is broken\". Work starts within 4 hours and it's fixed the same day. Sites are also watched by uptime monitoring."),
        ("Do I have to share my passwords?",
         "No. You add Chukker Digital as a user through each platform's own invitation, on a 20-minute call. Please never send passwords by text or email."),
        ("How do I pay?",
         "An invoice is sent at the start of each month. Pay by bank transfer or card at no extra cost, within 7 days of the invoice."),
    ],
}

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
PAGES = [
    {
        "slug": "", "src": "index.html", "nav": None,
        "title": "Web Design, Local SEO & Google Ads in Aiken, SC | Chukker Digital",
        "og_title": "Chukker Digital: website, search and ads for Aiken businesses",
        "description": "One local person for your website, local SEO and Google and Meta ads, on one flat monthly rate. For owner-run businesses in Aiken, SC. Free 15-minute audit.",
        "faq": "home", "priority": "1.0",
    },
    {
        "slug": "plans", "src": "plans.html", "nav": "plans",
        "title": "Monthly Website, SEO & Ads Plans in Aiken, SC | Chukker Digital",
        "description": "Flat monthly plans for Aiken small businesses: website care from $300, local SEO from $800, and Google and Meta ad management from $1,500. No hourly billing.",
        "h1": "Plans and pricing", "crumb": "Plans", "period": "Scoreboard",
        "intro": "Three flat monthly plans, each built for a different stage. Find the description that fits your business, and that's your plan.",
        "faq": "plans", "priority": "0.9", "offers": "plans",
    },
    {
        "slug": "website-builds", "src": "website-builds.html", "nav": "website-builds",
        "title": "Website Design in Aiken, SC from $1,500 | Chukker Digital",
        "description": "New websites for Aiken businesses: template sites from $1,500, custom designs from $2,500, hand-coded from $4,000. Written quote first, and you own the site.",
        "h1": "A new website, built to bring in customers", "crumb": "Website builds", "period": "The build",
        "intro": "A one-time project, separate from the monthly plans. You get a written quote before any work starts, and you own the finished site.",
        "faq": "website-builds", "priority": "0.9", "offers": "builds",
    },
    {
        "slug": "how-it-works", "src": "how-it-works.html", "nav": "how-it-works",
        "title": "How It Works: Requests, Turnaround & Billing | Chukker Digital",
        "description": "One request form with a due date back. Same-day fixes when something breaks, most requests done in 3 business days, and every account stays in your name.",
        "h1": "How working together works", "crumb": "How it works", "period": "Rules of play",
        "intro": "Requests go through one simple form and are handled on a set schedule with published turnaround times. You always know where a request stands.",
        "faq": "how-it-works", "priority": "0.7",
    },
    {
        "slug": "work", "src": "work.html", "nav": "work",
        "title": "Our Work for Aiken Businesses | Chukker Digital",
        "description": "Websites, Google listings and ads Chukker Digital runs in Aiken: a beauty studio, plus the family yoga studio and kettle corn business where it started.",
        "h1": "Work for Aiken businesses", "crumb": "Work", "period": "Today's lineup",
        "intro": "Chukker Digital started with its own family businesses and now runs websites, Google listings and ads for Aiken businesses like these.",
        "priority": "0.6",
    },
    {
        "slug": "about", "src": "about.html", "nav": "about",
        "title": "About Chukker Digital, Aiken, SC",
        "description": "Chukker Digital is a one-person web and marketing business in Aiken, SC, run by Josh Lovett. Local, flat-rate and transparent, with every account in your name.",
        "h1": "One local person, not an agency", "crumb": "About", "period": "Player profile",
        "intro": "Chukker Digital is run by Josh Lovett in Aiken, South Carolina, for owner-run businesses that want agency-level work without the agency overhead.",
        "priority": "0.6",
    },
    {
        "slug": "free-audit", "src": "free-audit.html", "nav": "free-audit",
        "title": "Free 15-Minute Website Audit in Aiken, SC | Chukker Digital",
        "description": "Book a free 15-minute audit of your website speed, mobile view, Google Business Profile and search ranking, shown on your own screen. Aiken, SC. No obligation.",
        "h1": "Book your free 15-minute audit", "crumb": "Free audit", "period": "The throw-in",
        "intro": "We'll look at your site speed, mobile view, Google profile and search ranking together, on your own screen, and show you the top few fixes.",
        "priority": "0.8", "no_cta": True,
    },
    {
        "slug": "404", "src": "404.html", "nav": None, "out": "404.html",
        "title": "Page not found | Chukker Digital",
        "description": "This page doesn't exist. Find Chukker Digital's plans, website builds or book a free audit.",
        "robots": "noindex, follow", "sitemap": False,
    },
]


def read(path):
    return (SRC / path).read_text(encoding="utf-8")


def money(n):
    return f"${n:,}"


FEATURES = [
    # (row label, [tier 1, tier 2, tier 3]); True = included, False = not included, text = detail
    ("Site upkeep, security updates and backups", [True, True, True]),
    ("Text and photo changes", ["5 a month", "5 a month", "5 a month"]),
    ("Broken-site fixes the same day", [True, True, True]),
    ("Monthly check-in email", [True, True, True]),
    ("Local SEO and keyword targeting", [False, True, True]),
    ("New pages or blog posts", [False, "2 a month", "2 a month"]),
    ("Google Business Profile posts", [False, "Weekly", "Weekly"]),
    ("Google and Meta ad management", [False, False, True]),
    ("Monthly ROI report", [False, False, True]),
]

LINEUP = [
    # (trade, business, what Chukker Digital does, optional (url, link text))
    ("Beauty studio on Whiskey Road, Aiken", "Total Vibe Salon & Studios",
     "A multi-service studio with lashes, hair, nails, waxing, spray tan and more under one roof. "
     "Its custom-coded website sends each service to the right provider's booking: Square for lashes, "
     "waxing and nails, and direct booking with each stylist for hair and spray tan.",
     ("https://totalvibesalon.com/", "totalvibesalon.com")),
    ("My wife's yoga studio in Aiken", "Peak Mobility Yoga",
     "My wife's studio, and the first site Chukker Digital launched from scratch: Mindbody class sign-ups, "
     "Google Analytics, and Google Ads run through the Chukker Digital manager account.",
     ("https://www.peakmobilityyoga.com/", "peakmobilityyoga.com")),
    ("My own kettle corn business in Aiken", "Big Cheese Kettle Co.",
     "My own business, and where I test every tool and ad strategy before using it for clients. "
     "Small-batch kettle corn sold at markets and events, with orders ahead for booth pickup and local delivery.",
     ("https://bigcheesekettleco.com/", "bigcheesekettleco.com")),
]


def cell(value, feature):
    cls = ' class="feature"' if feature else ""
    if value is True:
        inner = '<span class="yes" role="img" aria-label="Included">&#9679;</span>'
    elif value is False:
        inner = '<span class="no" role="img" aria-label="Not included">&ndash;</span>'
    else:
        inner = html.escape(value)
    return f"<td{cls}>{inner}</td>"


def scoreboard():
    def price_range(p):
        return f'to {money(p["max"])}{"+" if p["plus"] else ""} a month'

    heads, prices = [], []
    for p in PLANS:
        cls = ' class="feature"' if p.get("feature") else ""
        heads.append(f'<th scope="col"{cls}><span class="tier">{p["tier"]}</span>'
                     f'<span class="team">{html.escape(p["name"])}</span></th>')
        prices.append(f'<td{cls}><span class="price">{money(p["min"])}<small>{price_range(p)}</small></span></td>')
    rows = []
    for label, values in FEATURES:
        cells = "".join(cell(v, p.get("feature")) for p, v in zip(PLANS, values))
        rows.append(f'<tr><th scope="row">{html.escape(label)}</th>{cells}</tr>')
    fits = "".join(f'<td>{html.escape(p["common"])}</td>' for p in PLANS)
    return (
        '<div class="board">\n'
        '  <div class="board-title"><h2 id="board-title">Scoreboard: three flat monthly plans</h2><p>No hourly billing</p></div>\n'
        '  <table>\n'
        '    <caption class="visually-hidden">Monthly plan comparison</caption>\n'
        f'    <thead><tr><td></td>{"".join(heads)}</tr></thead>\n'
        f'    <tbody><tr><th scope="row">Monthly rate</th>{"".join(prices)}</tr>\n'
        f'    {"".join(rows)}</tbody>\n'
        f'    <tfoot><tr><th scope="row">Common fits</th>{fits}</tr></tfoot>\n'
        '  </table>\n'
        '  <p class="board-note">Each plan includes everything in the one before it. Your exact rate is set in a '
        'written quote after the free audit. Ad spend and hosting are paid by you, straight to Google, Meta or your host.</p>\n'
        '</div>'
    )


def lineup():
    items = []
    for i, (trade, name, did, link) in enumerate(LINEUP, 1):
        link_html = f' <a href="{link[0]}" rel="noopener">{link[1]}</a>' if link else ""
        items.append(
            f'<li>\n  <p class="jersey" aria-label="Number {i}">{i}</p>\n'
            f'  <div><h3>{html.escape(name)}</h3><p class="trade">{html.escape(trade)}</p></div>\n'
            f'  <p class="did">{html.escape(did)}{link_html}</p>\n</li>')
    items.append(
        '<li class="open">\n  <p class="jersey" aria-hidden="true">+</p>\n'
        '  <div><h3>Your business</h3><p class="trade">Next up</p></div>\n'
        '  <p class="did">Start with a free 15-minute audit of your website, Google profile and search ranking. '
        '<a href="/free-audit/">Book the audit</a></p>\n</li>')
    return '<ol class="lineup">\n' + "\n".join(items) + "\n</ol>"


def faq_html(key):
    items = []
    for q, a in FAQ[key]:
        items.append(f'<details><summary>{html.escape(q)}</summary><div class="answer"><p>{a}</p></div></details>')
    return '<div class="faq">' + "".join(items) + "</div>"


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", html.unescape(s))


def page_hero(page):
    return f'''<section class="page-hero" aria-labelledby="page-title">
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{html.escape(page["crumb"])}</li></ol></nav>
    <div class="page-hero-grid">
      <p class="period">{html.escape(page["period"])}</p>
      <div>
        <h1 id="page-title">{html.escape(page["h1"])}</h1>
        <p class="lede">{html.escape(page["intro"])}</p>
      </div>
    </div>
  </div>
</section>'''


CTA = '''<section class="throwin" aria-labelledby="cta-title">
  <div class="wrap">
    <p class="period">The throw-in</p>
    <div>
      <h2 id="cta-title">Start with a free 15-minute audit</h2>
      <p>See where your site, Google profile and search ranking stand today, on your own screen.</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="/free-audit/">Book a free audit</a>
      <a class="btn btn-line" href="tel:''' + PHONE_E164 + '''">Call ''' + PHONE_DISPLAY + '''</a>
    </div>
  </div>
</section>'''


def page_url(page):
    if page.get("out") == "404.html":
        return f"{SITE_URL}/404.html"
    return f"{SITE_URL}/{page['slug'] + '/' if page['slug'] else ''}"


def jsonld(page):
    url = page_url(page)
    graph = [BUSINESS, WEBSITE]
    webpage = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "about": {"@id": f"{SITE_URL}/#business"},
        "inLanguage": "en-US",
    }
    graph.append(webpage)
    if page.get("crumb"):
        graph.append({
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url},
            ],
        })
        webpage["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
    if page.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                for q, a in FAQ[page["faq"]]
            ],
        })
    if page.get("offers") == "plans":
        graph.append({
            "@type": "OfferCatalog",
            "@id": f"{url}#plans",
            "name": "Chukker Digital monthly plans",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": p["name"],
                    "description": "; ".join(p["items"]),
                    "seller": {"@id": f"{SITE_URL}/#business"},
                    "priceSpecification": {
                        "@type": "UnitPriceSpecification",
                        "priceCurrency": "USD",
                        "minPrice": p["min"],
                        **({} if p["plus"] else {"maxPrice": p["max"]}),
                        "unitCode": "MON",
                        "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "MON"},
                    },
                }
                for p in PLANS
            ],
        })
    if page.get("offers") == "builds":
        graph.append({
            "@type": "OfferCatalog",
            "@id": f"{url}#builds",
            "name": "Chukker Digital website builds",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": name,
                    "description": desc,
                    "seller": {"@id": f"{SITE_URL}/#business"},
                    "priceSpecification": {"@type": "PriceSpecification", "priceCurrency": "USD", "minPrice": price},
                }
                for name, price, desc in BUILDS
            ],
        })
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"


def fill(template, values):
    def rep(m):
        key = m.group(1)
        return values.get(key, "")
    return re.sub(r"\{\{([a-zA-Z0-9_\-]+)\}\}", rep, template)


def build():
    head = read("partials/head.html")
    header = read("partials/header.html")
    footer = read("partials/footer.html")
    tracking = read("partials/tracking.html").strip()

    for page in PAGES:
        url = page_url(page)
        values = {
            "title": html.escape(page["title"]),
            "og_title": html.escape(page.get("og_title", page["title"])),
            "description": html.escape(page["description"]),
            "canonical": url,
            "robots": page.get("robots", "index, follow, max-image-preview:large"),
            "site_url": SITE_URL,
            "version": VERSION,
            "tracking": tracking,
            "jsonld": jsonld(page),
            "year": str(YEAR),
        }
        for slug in ["plans", "website-builds", "how-it-works", "work", "about", "free-audit"]:
            values[f"nav_{slug}"] = ' aria-current="page"' if page["nav"] == slug else ""
        body_values = {
            "scoreboard": scoreboard(),
            "lineup": lineup(),
            "faq": faq_html(page["faq"]) if page.get("faq") else "",
            "cta": "" if page.get("no_cta") else CTA,
            "page_hero": page_hero(page) if page.get("h1") else "",
        }
        body = fill(read("pages/" + page["src"]), body_values)
        doc = fill(head, values) + fill(header, values) + body + "\n" + fill(footer, values)

        out = ROOT / (page.get("out") or (f"{page['slug']}/index.html" if page["slug"] else "index.html"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))

    # sitemap.xml
    urls = []
    for page in PAGES:
        if page.get("sitemap") is False:
            continue
        urls.append(
            f"  <url><loc>{page_url(page)}</loc><lastmod>{TODAY}</lastmod>"
            f"<priority>{page.get('priority', '0.5')}</priority></url>"
        )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print("wrote sitemap.xml")

    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /_src/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("wrote robots.txt")


if __name__ == "__main__":
    build()
