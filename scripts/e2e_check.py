"""
One-off end-to-end verification script (not part of the shipped project -
delete it, or keep it as a handy smoke test). Exercises the exact
"COMPLETE TEST" workflow from the spec against the real database (SQLite)
using Django's test Client, which renders real templates and goes through
real URL routing, views, and CSRF-protected forms.

Run with:
  python3 e2e_check.py
"""
import os
import django
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steel_auction.settings')
django.setup()

from django.conf import settings
# django.test.Client sends Host: testserver by default. Allow it ONLY for
# this throwaway verification script - the real settings.py shipped to the
# user intentionally does NOT include 'testserver' in ALLOWED_HOSTS.
settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

from django.conf import settings
# Only for this standalone script - Django's test Client sends Host: testserver.
# The real settings.py correctly restricts ALLOWED_HOSTS to localhost/127.0.0.1.
settings.ALLOWED_HOSTS.append('testserver')


from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone

from auctions.models import Auction, Item
from bids.models import Bid, AuctionResult

def line(msg, ok=True):
    print(("PASS " if ok else "FAIL ") + msg)

# --- Clean slate for repeatable runs ---
Bid.objects.all().delete()
AuctionResult.objects.all().delete()
Auction.objects.all().delete()
Item.objects.all().delete()
User.objects.filter(username__in=['buyer1', 'buyer2']).delete()

# 1-2. Admin creates an item
item = Item.objects.create(name='Sample Item', description='Example lot for testing', quantity=Decimal('1'), unit='units')
line(f"Item created: {item}")

# 3. Admin creates auction: starting 30000, increment 500, ACTIVE, short window so we can test closing
now = timezone.now()
auction = Auction.objects.create(
    item=item,
    starting_price=Decimal('30000'),
    minimum_increment=Decimal('500'),
    start_time=now - timedelta(minutes=5),
    end_time=now + timedelta(seconds=3),
    status=Auction.STATUS_ACTIVE,
)
line(f"Auction created: {auction} (ends in 3s)")

# 4. Create two buyers via the real /accounts/register/ view
client1 = Client()
resp = client1.post('/accounts/register/', {
    'username': 'buyer1', 'email': 'buyer1@example.com',
    'password1': 'StrongPass123!', 'password2': 'StrongPass123!',
})
line(f"buyer1 registered via /accounts/register/ (redirect={resp.status_code == 302})", resp.status_code == 302)

client2 = Client()
resp = client2.post('/accounts/register/', {
    'username': 'buyer2', 'email': 'buyer2@example.com',
    'password1': 'StrongPass123!', 'password2': 'StrongPass123!',
})
line(f"buyer2 registered via /accounts/register/ (redirect={resp.status_code == 302})", resp.status_code == 302)

buyer1 = User.objects.get(username='buyer1')
buyer2 = User.objects.get(username='buyer2')

# 5. buyer1 logs in (already logged in via register+auto-login, but test explicit login too)
client1_fresh = Client()
assert client1_fresh.login(username='buyer1', password='StrongPass123!')
line("buyer1 can log in with registered credentials")

# 6. buyer1 sees the active auction on /auctions/
resp = client1_fresh.get('/auctions/')
line("GET /auctions/ returns 200", resp.status_code == 200)
line("Active auction appears on /auctions/", b'Sample Item' in resp.content)

# 7. buyer1 opens auction detail
resp = client1_fresh.get(f'/auction/{auction.id}/')
line("GET auction detail returns 200", resp.status_code == 200)
line('"Place Bid" form shown to logged-in user', b'Place Bid' in resp.content)

# 8. buyer1 sees current price (starting price, no bids yet)
line("Current price shown as starting price", b'30000' in resp.content or b'30,000' in resp.content)

# 9. buyer1 bids 30000 (equal to starting price -> should be accepted)
resp = client1_fresh.post(f'/auction/{auction.id}/bid/', {'amount': '30000'}, follow=True)
line("buyer1's 30000 bid accepted", b'placed successfully' in resp.content)

# 10. Bid stored in the database
line("Bid row exists in DB for buyer1", Bid.objects.filter(auction=auction, bidder=buyer1, amount=Decimal('30000')).exists())

# 11. buyer2 bids 30500 (valid next increment)
client2_fresh = Client()
client2_fresh.login(username='buyer2', password='StrongPass123!')
resp = client2_fresh.post(f'/auction/{auction.id}/bid/', {'amount': '30500'}, follow=True)
line("buyer2's 30500 bid accepted", b'placed successfully' in resp.content)

# 12. Current highest bid updates
auction.refresh_from_db()
line(f"Current highest bid is now {auction.current_price()}", auction.current_price() == Decimal('30500'))

# 13. buyer1 attempts an invalid lower bid 30400 -> must be rejected
resp = client1_fresh.post(f'/auction/{auction.id}/bid/', {'amount': '30400'}, follow=True)
rejected = b'must be at least' in resp.content
line("buyer1's invalid 30400 bid rejected with a clear message", rejected)
line("No 30400 bid row was created", not Bid.objects.filter(auction=auction, amount=Decimal('30400')).exists())

# buyer1 bids 31000 -> valid, should be accepted
resp = client1_fresh.post(f'/auction/{auction.id}/bid/', {'amount': '31000'}, follow=True)
line("buyer1's 31000 bid accepted", b'placed successfully' in resp.content)

# 14. Bid history updates (newest first)
resp = client1_fresh.get(f'/auction/{auction.id}/')
history_index_31000 = resp.content.find(b'31000')
history_index_30500 = resp.content.find(b'30500')
line("Bid history shows newest bid (31000) before older bid (30500)", 0 <= history_index_31000 < history_index_30500)

# 15-16. Wait for the auction to actually reach its end_time, then hit a page to trigger auto-close
import time
time.sleep(4)
resp = client1_fresh.get(f'/auction/{auction.id}/')  # any page view triggers close_expired_auctions()
auction.refresh_from_db()
line(f"Auction status is now CLOSED after end_time passed: {auction.status}", auction.status == Auction.STATUS_CLOSED)

# 17-19. Highest bidder becomes winner, final price locked, result stored
result = AuctionResult.objects.filter(auction=auction).first()
line("AuctionResult was created", result is not None)
if result:
    line(f"Winner is buyer1: {result.winner}", result.winner_id == buyer1.id)
    line(f"Winning price is 31000: {result.winning_price}", result.winning_price == Decimal('31000'))

# Bidding after close must be rejected
resp = client2_fresh.post(f'/auction/{auction.id}/bid/', {'amount': '32000'}, follow=True)
line("Bid after auction close is rejected", b'not active' in resp.content or b'closed' in resp.content or b'ended' in resp.content)

# 20. Winner sees the auction in "My Won Auctions"
resp = client1_fresh.get('/my-wins/')
line('buyer1 sees the auction in "My Won Auctions"', b'Sample Item' in resp.content and b'31000' in resp.content)

# Admin can log in and see the admin site
admin_client = Client()
assert admin_client.login(username='admin', password='adminpass123')
resp = admin_client.get('/admin/auctions/auction/')
line("Admin can view the Auction admin list", resp.status_code == 200 and b'Sample Item' in resp.content)
resp = admin_client.get('/admin/bids/bid/')
line("Admin can view all bids", resp.status_code == 200)

print("\nDone.")
