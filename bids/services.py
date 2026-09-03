"""
Service functions for bids and auction closing.

Keeping this logic in one place (instead of scattered across views) means
there is a single source of truth for "is this bid valid?" and "how does
an auction close?" - both views and (if you add one later) an API or
management command call the same functions and get the same rules.
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from auctions.models import Auction
from .models import Bid, AuctionResult


class BidError(Exception):
    """Raised when a submitted bid fails validation. The message is safe to show to the user."""
    pass


def _close_auction(auction):
    """
    Actually close a single auction: lock the row, pick the winner from
    the stored bids, and create the AuctionResult. Never called directly
    from outside this module - use close_auction_if_needed / close_expired_auctions.
    """
    with transaction.atomic():
        # select_for_update() locks this row until the transaction ends, so if
        # two requests race to close the same auction at once, only one wins.
        locked = Auction.objects.select_for_update().get(pk=auction.pk)
        if locked.status != Auction.STATUS_ACTIVE:
            return locked  # someone else already closed it

        top_bid = locked.bids.order_by('-amount', 'created_at').first()
        locked.status = Auction.STATUS_CLOSED
        locked.save(update_fields=['status'])

        # get_or_create guards against ever creating two results for one auction
        AuctionResult.objects.get_or_create(
            auction=locked,
            defaults={
                'winner': top_bid.bidder if top_bid else None,
                'winning_bid': top_bid,
                'winning_price': top_bid.amount if top_bid else None,
            },
        )
        return locked


def close_auction_if_needed(auction):
    """Close a single auction if it is ACTIVE and its end_time has passed."""
    if auction.status == Auction.STATUS_ACTIVE and timezone.now() >= auction.end_time:
        return _close_auction(auction)
    return auction


def close_expired_auctions():
    """
    Find every ACTIVE auction whose end_time has passed and close them.

    This is called defensively from views (home, auction list, auction
    detail, dashboard) so auction status is always accurate for whoever is
    browsing, even without a scheduler running. For full reliability in
    production (auctions closing on time even with zero site traffic),
    also schedule the management command:

        python manage.py close_expired_auctions

    to run every minute via cron (Linux/Mac) or Task Scheduler (Windows).
    Both paths call this exact same function, so behaviour is identical.
    """
    now = timezone.now()
    expired = Auction.objects.filter(status=Auction.STATUS_ACTIVE, end_time__lte=now)
    closed = []
    for auction in expired:
        closed.append(_close_auction(auction))
    return closed


def place_bid(auction, user, amount):
    """
    Validate and store a new bid. Raises BidError with a user-friendly
    message if the bid can't be accepted; returns the created Bid on success.

    This is the ONLY place a Bid is ever created from user input - the
    place_bid view in this module's caller never trusts amount/status
    from the browser or from JavaScript, everything is re-checked here
    against the database.
    """
    # In case the auction's status is stale (e.g. end_time passed since the
    # page was loaded), close it first so we validate against reality.
    close_auction_if_needed(auction)
    auction.refresh_from_db()

    if auction.status != Auction.STATUS_ACTIVE:
        raise BidError("This auction is not active. Bidding is closed.")

    now = timezone.now()
    if now < auction.start_time:
        raise BidError("This auction has not started yet.")
    if now > auction.end_time:
        raise BidError("This auction has already ended.")

    if amount is None or amount <= 0:
        raise BidError("Enter a valid bid amount.")

    # Cap bid amounts at 10 digits (max value 9,999,999,999). Checked here,
    # not just via the input's maxlength on the page, because a POST request
    # could skip the browser entirely and send any number directly.
    if amount >= Decimal('10000000000'):
        raise BidError("Bid amount cannot be more than 10 digits.")

    with transaction.atomic():
        # Lock the auction row for the duration of this bid so two buyers
        # submitting the same amount at the same instant can't both "win"
        # the race - the second one to reach here re-checks against the
        # freshly-locked minimum and gets rejected if they're now too low.
        locked_auction = Auction.objects.select_for_update().get(pk=auction.pk)
        current_minimum = locked_auction.minimum_next_bid()
        if amount < current_minimum:
            raise BidError(f"Your bid must be at least ₹{current_minimum}.")
        bid = Bid.objects.create(auction=locked_auction, bidder=user, amount=amount)

    return bid
