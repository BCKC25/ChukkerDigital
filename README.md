# Chukker Digital website

The marketing site for Chukker Digital LLC, Aiken, SC. Plain static HTML and CSS, built to load fast and read cleanly for Google, served by GitHub Pages.

## How it's organized

| Path | What it is |
| --- | --- |
| `_src/pages/` | The body of each page. Edit copy here. |
| `_src/partials/` | Shared head, header, footer, and `tracking.html` for Google and Meta tags. |
| `_src/build.py` | Stitches pages together and writes the SEO tags, structured data, `sitemap.xml` and `robots.txt`. Plan prices, FAQs, page titles and descriptions live here. |
| `index.html`, `plans/`, `website-builds/` ... | **Generated.** Don't edit these by hand; rebuild instead. |
| `assets/` | Stylesheet, self-hosted fonts and images. |

## Making a change

1. Edit a file in `_src/`.
2. Run `python3 _src/build.py` from the repo root (Python 3, no installs needed).
3. Commit and push. GitHub Pages republishes in a minute or two.

To preview locally: `python3 -m http.server 8000`, then open http://localhost:8000.

## Adding Google and Meta tags

Everything goes in `_src/partials/tracking.html`, which is added to the `<head>` of every page. The file has commented slots for:

- Google Search Console verification
- Meta domain verification
- Google Analytics 4
- Meta Pixel

Paste each snippet, uncomment it, rebuild, push.

After Search Console is verified, submit `https://chukkerdigital.com/sitemap.xml` under **Sitemaps**.

## Publishing with GitHub Pages

1. Repo **Settings > Pages**: Source = *Deploy from a branch*, Branch = `main`, folder `/ (root)`.
2. Under **Custom domain**, enter `chukkerdigital.com` and save. (This creates the `CNAME` file.)
3. In Squarespace Domains, DNS settings for chukkerdigital.com, add:
   - `A` records for `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www`: `bckc25.github.io`
   - Leave the Google Workspace `MX` and `TXT` records alone, or email stops working.
4. Once the domain shows as verified in Pages, tick **Enforce HTTPS**.

Check GitHub's current Pages docs for the IP addresses before entering them; they rarely change but GitHub is the source of truth.

## SEO built in

- Unique title, meta description and canonical URL on every page
- Open Graph and Twitter card tags with a 1200×630 share image
- JSON-LD structured data: `ProfessionalService` (business, phone, service area), `WebSite`, `WebPage`, `BreadcrumbList`, `FAQPage`, and `OfferCatalog` for plan and build pricing
- `sitemap.xml` and `robots.txt`, regenerated on every build
- One `h1` per page, semantic landmarks, descriptive link text
- Self-hosted, subset fonts (about 75 KB total) and no framework JavaScript

## Fonts

Cormorant Garamond, Archivo and Big Shoulders are licensed under the SIL Open Font License 1.1; see `LICENSE-fonts.txt`.
