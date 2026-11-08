# Good Health Oils website - instructions for Claude

This repo is the website for Good Health Oils, LLC (Stephne Hilgendorf, dōTERRA Diamond Wellness Advocate).
Stephne updates it by sending Claude short prompts, often from her phone. Make the change, run `python3 build.py`
to check it builds with no WARNING lines, then commit to `main` and push. GitHub Actions publishes in about a minute.

## Golden rules
- Every doterra.com link ends with `?OwnerID=88739` (her referral ID). link.doterra.com short links are already hers.
- Promotions are content only - edit YAML in `content/`, not the templates, unless she asks for a design change.
- Never invent prices, PV, dates or terms. Use doterra.com/US/en/promotions, the doTERRA Digital Marketing Kit, or OneDrop.
  If something is unknown, leave it out and tell her.
- Images go in `assets/img/...` as .webp (max ~1400px wide, quality ~86). Keep file names lowercase-with-dashes.
- Pictures open their link in a new tab (the templates handle this when an item has a `url`).
- Keep her voice: warm, upbeat, simple sentences.

## Where things live
| What | File |
|---|---|
| Name, contact links, nav menu | `content/site.yml` |
| Home tiles + always-on cards (Yearly Renewal, Refer a Friend) | `content/home.yml` |
| Promotions (one file each) | `content/promos/*.yml` |
| Newsletter page | `content/newsletter.yml` |
| Shop products | `content/shop.yml` |
| Learn videos | `content/learn.yml` |
| About / How To Use / 90 Day Reset | `content/about.yml`, `content/how-to-use.yml`, `content/90-day-reset.yml` |
| Colors and fonts | `assets/css/site.css` (tokens at the top) |

## The three kinds of promotion
Each file in `content/promos/` has `type:` and `show_on_home:`.
1. `monthly` - Product of the Month and regular offers. Fields: `month`, `banner`, `intro`, `items`, `footnote`, optional `banner_options`.
   Only ONE monthly file should have `show_on_home: true`. Each month: copy last month's file to `YYYY-MM-monthly.yml`,
   update it, and set the old one to `show_on_home: false` (keep it as an archive).
2. `seasonal` - holiday or seasonal collections. Shows on the home page as one big picture that opens its own detail
   page (`/promos/<slug>/`) in a new tab. Fields: `home_card`, `detail` (title, subtitle, hero_image, intro, links, items).
3. `bogo` - BOGO week. Same shape as seasonal. Use `start`/`end` dates (YYYY-MM-DD): the home page shows it only between those dates.
Turn a section on or off with `show_on_home: true|false`. Optional `start`/`end` also auto-hide by date.
Item fields: `title`, `subtitle`, `image`, `url`, `text` (longer description), `caption`, `price`, `status` (red ribbon, e.g. "SOLD OUT"), `availability`.

## Quick prompts and what to do
- "Mark Winterberry sold out" -> add `status: SOLD OUT` to that item in the active holiday file.
- "Turn on BOGO" / "Hide the holiday section" -> flip `show_on_home`.
- "Change the Product of the Month to X" -> edit the first item in the active monthly file.
- "Use banner option B" -> copy that option's image to the monthly `banner.image`.
- "Add a product to the shop" -> add to the right section in `content/shop.yml`; ask for the price/link if not given.

## Monthly update (first of the month)
Follow the `monthly-doterra-promo-update` skill: banners and product graphics come from OneDrop (onedropdesigns.com, signed in
in her stephne@goodhealthoils.com Chrome profile); offer 3 banner style options, favoring holiday or seasonal themes when
they exist (she likes upscale casual elegant, but mix it up). Put the options in `banner_options` so they show at
`/promos/<slug>/banner-options/`. Fall back to the doTERRA Digital Marketing Kit only if she doesn't like any OneDrop option.

## Known gaps
- 90 Day Reset: Month 2 and Month 3 "Order" have no link yet; Month 3 Checklist and About use the same document.
