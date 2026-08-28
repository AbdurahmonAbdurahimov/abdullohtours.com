# abdullohtours.com — Build Specification

You are building a production website for **Abdulloh Tours**, a private tour operator in Uzbekistan. Read this whole document before writing code. Ask me before making architectural decisions that contradict anything here.

---

## 1. Business model (read carefully — this shapes everything)

Abdulloh Tours is a **private tour organizer**, not an OTA and not a travel agency selling flights.

- We do **NOT** sell airline tickets. Never build anything flight-related.
- We drive tourists around Uzbekistan in our own vehicles with an English-speaking driver.
- Pricing is **per private group (per vehicle)**, not per person. Entrance tickets, guide, and meals are per-person extras.
- **There is no online payment.** A booking is a *request*. The tourist submits a form, we get a Telegram notification, we reply on WhatsApp and agree on the final price. Design the whole funnel around this.
- Target audience: foreign tourists (Europe, US, Russia) searching Google before/during their trip to Uzbekistan.

**Booking status pipeline:**
`NEW → CONTACTED → QUOTED → CONFIRMED → COMPLETED` (plus `CANCELLED`)

**Response time is the key business metric.** If we don't reply within an hour, the tourist books with GetYourGuide instead. Build for that.

---

## 2. Tech stack (fixed — do not substitute)

```
Python 3.12 + Django 5.x
PostgreSQL 16
Gunicorn + Caddy (automatic HTTPS)
Tailwind CSS via standalone CLI (NOT the CDN script)
Alpine.js for interactivity, HTMX for partial updates
django-unfold (admin theme)
django-modeltranslation (i18n for model content)
Docker Compose for deployment
cron for background jobs
```

**Explicitly NOT used:**
- No Celery, no Redis. Background work runs via Django management commands called from cron.
- No React / Next.js / any SPA. Server-rendered Django templates only — this is an SEO-first project.
- No Cloudflare. Caddy handles TLS; we serve our own static/media.
- No `cdn.tailwindcss.com`. Build CSS with the Tailwind CLI.
- No `localStorage` / `sessionStorage` anywhere.

### Deployment target

Single Hostinger VPS: Ubuntu 24.04, 2 vCPU / 4 GB RAM, European datacentre
(Vilnius or Amsterdam — the audience is mostly European).

Domain: **abdullohtours.com**

- Canonical host is `https://abdullohtours.com` (no `www`).
- Caddy 301-redirects `www.abdullohtours.com` to the canonical host.
- Every canonical tag, sitemap entry, and JSON-LD URL uses the canonical host.

Compose services: `web` (Gunicorn, 3 workers), `db` (postgres:16-alpine),
`caddy` (reverse proxy + automatic TLS).

Constraints for this box:

- The `db` service must NOT publish any port to the host — internal Docker
  network only. Docker bypasses `ufw`, so a published Postgres port would be
  reachable from the internet regardless of firewall rules.
- Only Caddy publishes ports (80, 443).
- Postgres tuning: `shared_buffers=256MB`, `max_connections=50`. The defaults
  assume a much larger machine.
- Memory limits in compose so one runaway process cannot take down the box:
  `web` 1g, `db` 768m.
- Postgres data and user-uploaded media live in named volumes, not bind mounts
  into the project directory.
- Provide `deploy.sh`: pull, build, migrate, collectstatic, restart.
- `backup_db` cron writes a `pg_dump`, keeps 14 days locally, and sends the
  dump to the Telegram admin chat as a document so backups live off-server too.

---

## 3. Design system

The brand is **Gold & Navy** — dark navy backgrounds, gold accents, warm cream for light sections. Derived from the company's existing printed flyers.

### Colour tokens (this is the complete list — do not add Material Design tokens)

```js
colors: {
  navy:        "#071A2A",  // primary dark background
  "navy-soft":  "#0A1D2D",  // cards, elevated surfaces on dark
  gold:        "#C9A66B",  // primary accent, borders, labels
  "gold-bright": "#D9A02E", // CTAs, hover states
  cream:       "#FFF8F1",  // light section background
  "cream-soft": "#FCF2E4",  // subtle light surface
  ink:         "#1F1B13",  // body text on light
  muted:       "#43474C",  // secondary text on light
  line:        "#C4C6CC",  // borders on light
}
```

Semantic states: use Tailwind's built-in `red-600` / `green-600` / `amber-500` for error/success/warning. Don't invent tokens for them.

### Typography

```
Headings: Playfair Display  (400, 700)
Body:     Inter             (400, 500, 600)
```

**Both fonts MUST support Cyrillic** — the site will have a Russian version. Do not use Libre Caslon Text or Geist (no Cyrillic coverage). Self-host both fonts as WOFF2 with `font-display: swap`; do not hotlink Google Fonts.

Type scale (responsive, single element — never duplicate an element for mobile/desktop):

```
display: text-[32px] md:text-[52px]   leading-tight
h1:      text-[28px] md:text-[44px]
h2:      text-[24px] md:text-[32px]
h3:      text-[20px] md:text-[24px]
body:    text-[16px]  leading-relaxed
small:   text-[14px]
label:   text-[13px]  tracking-[0.08em] uppercase font-semibold
```

### Spacing & shape

```
spacing: xs 4, sm 12, base 8, md 24, lg 48, xl 80
container max-width: 1280px
radius: default 4px, lg 8px, xl 12px, full 9999px
```

Aesthetic: restrained and editorial. Thin gold hairline borders, generous whitespace, large photography. Avoid heavy drop shadows and gradients.

### Reference mockups

Static HTML mockups from the design phase live in `design/`. Use them as the
visual reference for layout, component structure, and section ordering when
building templates.

Take from them: page composition, grid ratios, card anatomy, hero treatment,
spacing rhythm, and the stepper pattern in the tour builder.

Do **not** copy them verbatim. They contain known defects that must not reach
production:

- `cdn.tailwindcss.com` script tag — use the Tailwind CLI build instead
- Duplicated `<h1>`/`<h2>` pairs hidden with `hidden md:block` — use one element
  with responsive sizing
- Auto-generated Material Design colour tokens — use only the palette above
- `data-alt` attributes instead of real `alt` — write real alt text
- Fixed `h-[819px]` hero heights — use `min-h-[80dvh]`
- Placeholder body copy paraphrased from Wikipedia — replace with
  `TODO: content needed`
- `googleusercontent.com` image URLs — temporary, replace with local media
- Per-person pricing in the tour builder — this business prices per vehicle

`design/` is reference material: keep it in the repo, but outside
`STATICFILES_DIRS` so it never ships to production.

---

## 4. Data models

Create these Django apps: `core`, `catalog`, `bookings`, `blog`, `notifications`.

### core

```python
SiteSettings          # singleton, editable in admin
  phone, whatsapp_number, telegram_username, instagram_username,
  email, office_address, working_hours, response_time_promise,
  default_og_image

SEOMixin              # abstract: meta_title, meta_description,
                      # focus_keyword, og_image, noindex
```

**Seed SiteSettings with these real values:**

```
phone               = "+998953336000"
whatsapp_number     = "998953336000"
telegram_username   = "abdulloh_talibdjanov"
instagram_username  = "abdulloh_tours"
```

Never hardcode contact details in templates — always read from `SiteSettings` via a context processor.

### catalog

```python
Destination      slug, name, region, hero_image, intro, body,
                 min_recommended_days, is_active, order, SEOMixin

Attraction       destination FK, name, images, description,
                 entry_fee_usd, typical_duration_min, is_bookable=False

VehicleClass     name, min_pax, max_pax, daily_rate_usd, image, order

Activity         destination FK, title, slug, price_type, base_price_usd,
                 duration_hours, images, short_desc, full_desc,
                 included, not_included, is_active, SEOMixin
                 # price_type ∈ {PER_VEHICLE, PER_PERSON, PER_DAY}

AddOn            name, description, price_usd, unit, is_active
                 # unit ∈ {PER_PERSON, PER_DAY, PER_GROUP, PER_NIGHT}
                 # e.g. guide $50/day, hotel ~$60/night, airport VIP $80

Package          slug, title, tier, total_days, summary, body,
                 hero_image, gallery, base_vehicle_class,
                 is_featured, is_active, SEOMixin
                 # tier ∈ {ECONOMY, STANDARD, PREMIUM}

PackageDay       package FK, day_number, title, description

PackageItem      package_day FK, activity FK (nullable),
                 addon FK (nullable), is_optional, custom_label

SeasonalRate     activity FK (nullable, null = applies globally),
                 date_from, date_to, multiplier, label

Vehicle          name, vehicle_class FK, plate, is_partner,
                 is_active, daily_cost_usd

Driver           name, phone, languages, is_active

BlackoutDate     date, vehicle FK (nullable = all), reason
```

### bookings

```python
BookingRequest   ref_code (e.g. "AB-8291"), source_type,
                 package FK (nullable), custom_payload (JSONField),
                 start_date, end_date, adults, children,
                 vehicle_class FK, full_name, email, phone,
                 whatsapp, country, message, preferred_language,
                 status, estimated_total_usd, quoted_total_usd,
                 admin_notes, created_at, first_response_at,
                 utm_source, utm_medium, utm_campaign

BookingItem      request FK, item_type, label,
                 unit_price_usd, quantity, subtotal_usd
                 # frozen price snapshot at time of request

BuilderSession   session_key, payload (JSONField), last_step,
                 estimated_total_usd, is_converted, created_at
                 # abandoned-builder recovery
```

**Critical rule:** `BookingItem` stores a *copy* of the price. If an admin changes an `Activity` price tomorrow, existing requests must not change.

### blog

```python
BlogPost         slug, title, excerpt, body (rich text),
                 cover_image, author, category, related_destinations M2M,
                 related_packages M2M, published_at, status, SEOMixin
                 # status ∈ {DRAFT, REVIEW, PUBLISHED}
```

### notifications

```python
Notification     kind, payload (JSON), status, attempts,
                 last_error, created_at, sent_at
                 # status ∈ {PENDING, SENT, FAILED}

TelegramAdmin    chat_id, name, is_active, receives_bookings,
                 receives_reminders
```

---

## 5. Pricing engine

This is the hardest part. Put it in `catalog/pricing.py` as pure functions with full unit tests.

**Rules:**

1. Vehicle class is chosen **automatically** from total pax. The user may only upgrade, never pick a vehicle too small for their group.
2. If pax exceeds the largest vehicle capacity, add a second vehicle and multiply transport cost accordingly.
3. Transport cost = `vehicle_class.daily_rate_usd × number_of_days × vehicle_count`.
4. `PER_VEHICLE` activities: flat price per group.
5. `PER_PERSON` activities and add-ons: `price × pax`.
6. `PER_DAY` add-ons (e.g. guide): `price × days`.
7. `PER_NIGHT` add-ons (hotel): `price × pax × nights`.
8. Apply `SeasonalRate.multiplier` when the start date falls in the range.
9. Children under 12 count as 0.5 for per-person entrance fees but full for vehicle capacity. Make this a named constant, not a magic number.

**Return a structured breakdown**, not just a total:

```python
{
  "line_items": [{"label", "unit_price", "qty", "subtotal", "type"}],
  "vehicle_class": ...,
  "vehicle_count": ...,
  "subtotal_usd": ...,
  "total_usd": ...,
  "per_person_usd": ...,   # display only
}
```

**All pricing is computed server-side.** The Alpine.js builder POSTs the current selection to `/api/quote/` and renders whatever the server returns. Never compute a price in JavaScript.

Display totals as **"Estimated total"** everywhere — never "final price". This is a quote, not a sale.

---

## 6. Pages & URL structure

Language prefix on every URL. `en` is default and `x-default`.

```
/<lang>/                                    Home
/<lang>/destinations/                        Destination index
/<lang>/destinations/<slug>/                 Destination detail
/<lang>/tours/                               Package index
/<lang>/tours/<slug>/                        Package detail   ← highest-value SEO page
/<lang>/build/                               Tour Builder
/<lang>/build/quote/                         POST endpoint (HTMX)
/<lang>/request/                             Booking request form
/<lang>/request/<ref_code>/thanks/           Confirmation
/<lang>/about/                               About / Meet Abdulloh
/<lang>/reviews/
/<lang>/faq/
/<lang>/blog/  ·  /<lang>/blog/<slug>/
/<lang>/contact/
/sitemap.xml  ·  /robots.txt
/tg/webhook/<secret>/                        Telegram webhook
```

Localised slugs per language where it matters (`/de/touren/...`).

### Tour Builder flow (5 steps, Alpine.js + HTMX)

```
1. Dates (real date picker) + number of travellers
2. Destinations (multi-select cards)
3. Activities per selected destination
4. Add-ons (guide, hotel, airport meet, entrance tickets)
5. Contact details → submit
```

Vehicle class is derived at step 1 and shown in the sticky summary sidebar — it is not a separate step. The summary shows a live estimated total on every change.

Persist a `BuilderSession` row on each step change so abandoned builders are visible in admin.

### Booking request form — keep it short

Only: name, email, WhatsApp/phone, country, optional message. Every extra field costs conversion. Spam protection = honeypot field + `django-ratelimit` (5 requests/hour per IP). No visible CAPTCHA.

---

## 7. SEO requirements (non-negotiable)

- **Exactly one `<h1>` per page**, in the DOM. Never render two headings and hide one with `hidden md:block` — use responsive font sizes on a single element.
- Every `<img>` needs a real, descriptive `alt`.
- JSON-LD on every relevant page: `TravelAgency` (site-wide, including `telephone` and `sameAs` for Instagram/Telegram), `TouristTrip` (packages), `TouristAttraction` (attractions), `Product` + `Offer` (with `priceCurrency: USD` and `lowPrice`), `FAQPage`, `BreadcrumbList`, `Article` (blog).
- `hreflang` tags for all active languages plus `x-default`. **A language variant must only emit hreflang when its translation is actually complete** — add a `translation_complete` flag per language on translated models and fall back to English otherwise. Never publish machine-translated stubs.
- Canonical URL on every page.
- `django.contrib.sitemaps` with separate sections per content type and per language.
- Images: convert uploads to WebP on save, generate responsive `srcset`, `loading="lazy"` below the fold, explicit `width`/`height` to avoid layout shift.
- Target Lighthouse ≥ 95 on mobile for Performance, Accessibility, Best Practices, SEO.

**Content warning:** do not write placeholder copy scraped or paraphrased from Wikipedia or other sites. Where real content is missing, insert a clearly marked `TODO: content needed` block. Duplicate content will prevent this site from ranking.

---

## 8. Telegram bot

Implement as a plain Django webhook view at `/tg/webhook/<secret>/` using `python-telegram-bot` in webhook mode — no separate process, no polling.

**On a new booking request**, send to every active `TelegramAdmin` with `receives_bookings=True`:

```
🆕 NEW REQUEST  #AB-8291

👤 Elena Rostova · 🇬🇧 UK
📅 12–19 Oct 2025 · 2 adults
🚗 Sedan (1–3 pax)
🗺 Samarkand, Bukhara
💰 Estimated: $1,250

📱 +44 7700 900077
✉️ elena.r@example.com

⚠️ 12 Oct: 2/2 vehicles booked
```

With inline buttons: `✅ Confirm` · `💬 Contacted` · `❌ Reject` · `🔗 Open in admin`. Pressing a button updates `BookingRequest.status` and edits the message in place.

**Commands:** `/today`, `/pending`, `/week`, `/stats`.

**Auth:** only chat IDs present in `TelegramAdmin` are served. Everything else is ignored silently.

**Delivery:** every message is written as a `Notification` row first, then sent. Failures stay `PENDING` and are retried by cron. A notification must never be lost because the Telegram API was briefly down.

---

## 9. Cron jobs (Django management commands)

```
* * * * *   python manage.py send_pending_notifications
*/15 * * * * python manage.py check_unanswered_requests   # >60 min with no first_response_at → ping Telegram
0 3 * * *   python manage.py update_exchange_rates        # USD → EUR/GBP/UZS, cached in DB
0 4 * * *   python manage.py backup_db                    # pg_dump, keep 14 days
```

---

## 10. Availability logic (soft, not hard)

We do not block dates. This is a request-based business and the fleet grows over time.

- Count `CONFIRMED` requests overlapping a date against the count of active vehicles.
- If at or over capacity, show a `Limited availability for these dates` badge on the site — this is useful urgency, not a blocker.
- Include the same warning in the Telegram notification so the admin sees the conflict immediately.
- `BlackoutDate` rows let the admin mark genuinely unavailable days.

---

## 11. Admin panel

Use `django-unfold`. Do **not** hand-build an admin UI.

- Sidebar groups: Bookings · Catalog · Content · Fleet · Settings
- Custom dashboard: today's requests, pending count, confirmed this month, estimated revenue, recent requests table, abandoned builders
- `BookingRequest` list: filter by status/date/source, colour-coded status badges, one-click WhatsApp link, inline `BookingItem` breakdown
- Content models show a per-language translation status column so gaps are visible
- Bulk actions on `BookingRequest`: mark contacted, mark confirmed, export CSV

---

## 12. Internationalisation

Languages: `en` (default), `ru`, `de`, `fr`, `es`.

- UI strings via Django's `gettext` / `.po` files.
- Model content via `django-modeltranslation`.
- Launch reality: EN and RU get full content including blog; DE/FR/ES get tour and destination pages only. The code must support all five from day one, but only emit hreflang for genuinely translated pages.
- Prices are stored in USD. Display USD by default, with EUR/GBP shown as an informational conversion using a daily cached rate.

---

## 13. Phase 1 scope (build this first)

Ship a live, indexable site before adding the builder. Google needs time to trust a new domain, so the clock should start early.

**In scope for Phase 1:**
- Project skeleton, Docker Compose, Caddy, settings split (base/dev/prod)
- Design system: `tailwind.config.js`, self-hosted fonts, `base.html`, header, footer, floating WhatsApp button, language switcher
- All models + migrations + admin
- Home, Destination index/detail, Package index/detail, About, Contact, FAQ
- Booking request form + confirmation page
- Telegram notifications + bot commands
- SEO layer: sitemaps, robots.txt, JSON-LD, hreflang, canonical
- English only in the UI (but i18n plumbing in place)
- Seed data: 5 destinations (Tashkent, Samarkand, Bukhara, Khiva, Amirsoy/Chimgan), 3 vehicle classes, 3 packages, ~15 activities

**Phase 2:** Tour Builder, Russian translation, reviews.
**Phase 3:** blog, remaining languages, programmatic SEO landing pages.

---

## 14. Working agreement

- Start by proposing the repo structure and asking me to approve it before generating files.
- Commit in small, logical steps with clear messages.
- Write tests for the pricing engine before anything else touches it — it is the part most likely to silently produce wrong numbers.
- Use type hints throughout. Run `ruff` and `black`.
- Keep `.env.example` current. Never commit secrets.
- Add a `README.md` with local setup and deployment steps as you go.
- If any instruction here conflicts with something you consider bad practice, say so and explain rather than silently doing it your own way.

Begin with the repo structure proposal.