---
name: bogo
description: Build or refresh the BOGO page at goodhealthoils.com/bogo for a new dōTERRA BOGO sale - pull the pairings, prices and PV, download elegant graphics that show every product in each pairing, link the eBook, ask Stephne for the dates, then build and publish. Use when Stephne types /bogo or says a new BOGO is coming.
---

# /bogo - set up the BOGO page

Stephne runs this a few times a year, usually from her phone. Keep replies short, warm and plain (no code talk).
Read `CLAUDE.md` first (golden rules: `?OwnerID=88739` on every doterra.com link, write the brand as dōTERRA, never invent
prices, PV, dates or terms).

## How the page works (already built - content only)
- One file per BOGO: `content/promos/bogo-YYYY-MM.yml` (`type: bogo`). The one with `show_on_home: true` is the current
  BOGO and is published at **/bogo/** (also kept as a preview/archive copy at `/promos/<slug>/`, not in search).
- Four dates, all `YYYY-MM-DD`, decided by the viewer's own date (no rebuild or reminders needed):
  | field | what happens |
  |---|---|
  | `show_from` | home-page BOGO picture appears; /bogo says **"BOGO's coming <weekday>!"** until the sale starts |
  | `start` | sale starts - the deals show on /bogo |
  | `end` | last sale day. The day after, /bogo says **"BOGO's have Ended"** |
  | `show_until` | last day the home-page picture shows (/bogo keeps saying "have Ended") |
- `detail.ebook` (title, text, url, image) is pinned to the top of /bogo in every state.
- Templates: `templates/bogo.html`, `templates/promo-body.html`; logic in `assets/js/site.js` and `build.py`. Don't edit
  them for a normal BOGO.

## Sources (in this order)
1. **Deals - doTERRA BOGO page**: https://www.doterra.com/US/en/bogo?OwnerID=88739 (new deals usually go up the Monday the
   sale starts; before that it still shows the last BOGO - check the dates on it). It has bot protection, so read it with
   Playwright (headless Chromium, desktop Chrome user agent), not curl. It lists the pairings, the bundle, the
   free-gift-with-PV offer and the limits.
2. **Deals - Stack Team App** (sign-in needed, Claude can't open it):
   https://usdoterradiamonds.teamapp.com/articles/9983840?_detail=v1 - ask Stephne for a screenshot of the deals if anything is
   missing or unclear (free gift with PV, limits, dates).
3. **Graphics - DMK** (doTERRA Digital Marketing Kit on Canto, public, preferred):
   https://doterra.canto.com/v/DigitalMarketingKit/landing?viewIndex=0. Use the helper:
   ```
   python3 .claude/skills/bogo/dmk.py folders                      # find the "- <Month> BOGOs -" folder id
   python3 .claude/skills/bogo/dmk.py list <FOLDER_ID> Post         # social posts (one per pairing + bundle)
   python3 .claude/skills/bogo/dmk.py list <FOLDER_ID> Banner       # wide banners for the hero
   python3 .claude/skills/bogo/dmk.py get <ASSET_ID> assets/img/promos/<slug>/<name>.webp 1000
   ```
   Pick simple, elegant graphics that show **every product in the pairing** (not a single bottle). In Nov 2026 the best
   were `<Pairing>-...-Promo-Social Media-US-English-Post.jpg` (square, BUY/GET labels) for cards and a
   `...-Promo-Social Media-US-English-Banner-0N.jpg` for the hero. The `...-Pricing-Post.jpg` versions print
   Retail/Wholesale/PV - read prices off those (download at 2000px and crop the text box) when the doTERRA page isn't up yet.
   Card images 1000px wide, hero 1400px, webp quality 86 (the helper does this).
4. **Graphics fallback - OneDrop** (paid, sign-in, being phased out): https://www.onedropdesigns.com/doterra/?pages=1&slug=&sortby=promotions
   Only if the DMK has nothing usable. Claude can't sign in - ask Stephne to download and send the images.
5. **eBook - Issuu**: https://issuu.com/doterra-living?ps=24 - find `..._bogo_-_<name>_ebook` (e.g.
   `https://issuu.com/doterra-living/docs/november_2026_bogo_-_pure_joy_ebook`). `curl` the page and grep for
   `doterra-living/docs/`. Cover image: the DMK "eBook & Educational Materials" album has the eBook PDF; download its
   preview (`previewURI` from `dmk.py`'s search JSON) or use the first page of a graphic.

Network: the cloud environment allows www.doterra.com, media.doterra.com, doterra.canto.com, d2hqlhbe1d8j2s.cloudfront.net,
d3opzdukpbxlns.cloudfront.net and issuu.com. If something new is blocked, tell her which site and ask before adding it.

## Steps
1. Find the deals (sources 1-2) and the DMK folder (source 3). Note the BOGO name (e.g. "Pure Joy"), sale dates, each
   pairing (buy item, free item(s), wholesale price, PV), the bundle (price, PV, savings), any free gift with PV and limits.
2. Copy the latest `content/promos/bogo-*.yml` to `content/promos/bogo-YYYY-MM.yml` (sale month) and set the old file to
   `show_on_home: false` (keep it as an archive). Update slug, title, subtitle, intro (her voice: warm, upbeat, simple),
   `ebook`, and `items`:
   ```yaml
   - title: Buy Citrus Bloom 15 mL
     subtitle: Get Citrus Bliss 15 mL FREE
     price: "Wholesale $28.50 (28.50 PV)"
     image: assets/img/promos/bogo-2026-11/citrus-bloom-citrus-bliss.webp
     url: https://www.doterra.com/US/en/bogo?OwnerID=88739
   ```
   Bundle first. Add a free-gift-with-PV card or intro line only when a source confirms it. Leave out anything unknown and
   tell her.
3. Download the graphics into `assets/img/promos/<slug>/` (`hero.webp`, `bundle.webp`, `<buy>-<free>.webp`, `ebook.webp`).
4. **Ask Stephne for the dates** (AskUserQuestion, one question each, suggest sensible defaults from the sale dates):
   - When should the page show up on the site? (`show_from` - e.g. a few days before; it says "BOGO's coming <day>!")
   - What is the last day of the sale? (`end` - default the official last day; `start` comes from the sources)
   - When should it come off the home page? (`show_until` - e.g. a week after the sale; /bogo keeps the eBook and
     "BOGO's have Ended")
5. `python3 build.py` - no WARNING lines. Check all four states with Playwright by faking the date
   (`context.clock.setFixedTime`, timezone America/Chicago): before start, during, after end, after show_until. Look at the
   phone (390px) and desktop screenshots.
6. Commit and push to `main` (see CLAUDE.md). Tell her it's live in about a minute at goodhealthoils.com/bogo, list the
   pairings, the dates, and anything you couldn't confirm.
