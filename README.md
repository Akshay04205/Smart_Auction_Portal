# Auction Portal

A working Django + SQLite auction website: buyers register, browse active
auctions, place competitive bids, and win auctions when the timer runs out.
Auctions any kind of item (not tied to any one industry). Built with Django
templates + vanilla HTML/CSS/JS (no frontend framework).

## 1. Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations (this creates db.sqlite3 automatically - no separate
# database server or credentials needed)
python manage.py migrate

# Create your own admin account
python manage.py createsuperuser
```

## 2. (Optional) Load demo data

A ready-made fixture with a sample item, an active auction, and two buyer
accounts is included:

```bash
python manage.py loaddata auctions/fixtures/demo_data.json
```

This creates:
- **Item:** Sample Auction Item, 1 unit
- **Auction:** starting price ₹1,000, minimum increment ₹50, status ACTIVE
- **Users:** `admin` / `adminpass123` (superuser), `buyer1` / `BuyerPass123!`, `buyer2` / `BuyerPass123!`

Note: the auction's `end_time` in the fixture is a fixed timestamp set when
it was generated. If it's already in the past by the time you load it, open
it in `/admin/` and push `end_time` into the future, or just create a fresh
auction yourself (see step 4).

## 3. Run it

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Admin site is at `http://127.0.0.1:8000/admin/`.

## 4. Create your own item + auction (if not using the fixture)

In `/admin/`:
1. **Auctions → Items → Add** - name, description, quantity, unit.
2. **Auctions → Auctions → Add** - pick the item, set starting price,
   minimum increment, start time, end time, and status `ACTIVE`.

## 5. Keep auctions closing on time (recommended for production)

The site auto-closes any expired ACTIVE auction whenever *any* page is
loaded, so it self-heals even without a scheduler. For auctions to close
exactly on time with zero site traffic, also schedule this every minute:

```bash
python manage.py close_expired_auctions
```

Linux/Mac cron example:
```
* * * * * cd /path/to/project && /path/to/venv/bin/python manage.py close_expired_auctions
```

## Project structure

```
steel_auction/        Django project settings, root urls.py
                       (internal package name only - not user-facing)
accounts/              registration, login/logout wiring, my-wins
  forms.py             BuyerRegistrationForm (UserCreationForm + email)
  views.py, urls.py
auctions/              Item + Auction models, home/list/detail views
  models.py
  admin.py             Item & Auction admin (searchable/filterable, inline bids)
  management/commands/close_expired_auctions.py
  fixtures/demo_data.json
bids/                  Bid + AuctionResult models, bidding & closing logic
  models.py
  services.py          place_bid(), close_expired_auctions() - single source of truth
  views.py, urls.py
  admin.py             read-only Bid & AuctionResult admin
templates/             base.html + all pages + registration/
static/css/style.css   dark theme, "digital scale" price readout
static/js/countdown.js live countdown timer (cosmetic only)
scripts/e2e_check.py   optional dev smoke test (see below)
```

**Note on the `steel_auction/` folder name:** this is the internal Django
project package (settings, WSGI, URL root) - it's a technical name only,
never shown to site visitors, and renaming it would require updating any
hosting provider's WSGI configuration that already points at it. Everything
user-facing has been renamed to "Auction Portal."

## How the auction workflow works

1. **Admin** creates an `Item`, then an `Auction` for it with a starting
   price, minimum increment, and a start/end time window. Setting status to
   `ACTIVE` makes it visible and biddable on the public site.
2. **Buyers** register at `/accounts/register/` (auto-logs them in) or log
   in at `/accounts/login/`.
3. On `/auctions/` or an auction's detail page (`/auction/<id>/`), a logged-in
   buyer sees the current highest bid and the minimum amount they're allowed
   to bid next (`starting_price` if no bids yet, else `highest_bid + minimum_increment`).
4. Submitting the bid form **POST**s to `/auction/<id>/bid/`. The view
   (`bids/views.py`) never trusts the browser - it hands the raw amount to
   `bids/services.py::place_bid()`, which re-checks: is the auction ACTIVE,
   is `now` between `start_time` and `end_time`, and is the amount high
   enough (and no more than 10 digits) - all against the database, inside a
   row-locked transaction so two buyers bidding the same instant can't both
   "win" the same bid.
5. Every accepted bid is stored as its own `Bid` row - nothing is ever
   overwritten, so the full history is always available (newest first).
6. The countdown timer on the page is pure JavaScript for display only.
   Security-wise it's irrelevant: the backend re-validates `end_time`
   independently on every single bid submission.
7. Once `end_time` passes, the **next** page load (by anyone) or the
   `close_expired_auctions` management command calls
   `bids/services.py::close_expired_auctions()`, which locks the auction,
   picks the bid with the highest amount as the winner, and creates a single
   `AuctionResult` row (winner, winning bid, winning price, closed_at). If
   nobody bid, the auction still closes but the result has no winner.
8. The winning buyer sees the auction under **My Won Auctions**
   (`/my-wins/`).

## What was verified before handoff

The core bidding/closing workflow was tested end-to-end using Django's test
client (registration → login → viewing auctions → placing valid bids →
rejecting an invalid low bid → bid history ordering → auction auto-closing
at end_time → winner selection → winning price lock → AuctionResult
creation → rejecting bids after close → the winner seeing the auction in
"My Won Auctions" → admin viewing auctions and bids). All 26 checks passed.
The `Scrap` → `Item` rename migration (`auctions/migrations/0003_rename_scrap_to_item.py`)
was additionally tested by applying it to a **real copy of live data**
(existing items, auctions, and users) to confirm nothing is lost - only
names change, not data. The script is included at `scripts/e2e_check.py` if
you want to rerun it yourself (it deletes and recreates its own test data -
safe to run against a dev database, not recommended against real data).

## Redeploying this update (e.g. to PythonAnywhere)

If you already have this site running on a host, update it with:

```bash
python manage.py migrate                 # applies the Scrap -> Item rename
python manage.py collectstatic --clear   # refreshes static files (see below)
```
Then reload your web app from the hosting provider's dashboard.

## Note: uses SQLite, and STATIC_ROOT is now set

This project uses SQLite (`db.sqlite3`, created automatically by `migrate`,
listed in `.gitignore`). `STATIC_ROOT` is now set in `settings.py`, which
was missing before - that omission was the cause of unstyled/overlapping
admin pages on real hosting (`runserver` on your own machine doesn't need
it, which is why it worked locally without it). After deploying, always run
`python manage.py collectstatic` and reload the web app for CSS/JS to load
correctly.
