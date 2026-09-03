from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from auctions.models import Auction
from .services import BidError, place_bid


@login_required
@require_POST
def place_bid_view(request, auction_id):
    """
    Handle a bid submission from the auction detail page.

    Security notes:
    - @login_required means an anonymous user is redirected to login instead
      of ever reaching this view.
    - @require_POST rejects GET requests (so a bid can't be placed just by
      visiting a URL / a link / a bookmark).
    - The Django CSRF middleware (enabled in settings.py) checks the
      {% csrf_token %} in the bid form automatically - no extra code needed here.
    - The actual validation (status, timing, amount) happens in
      bids.services.place_bid, never in JavaScript.
    """
    auction = get_object_or_404(Auction, pk=auction_id)

    raw_amount = request.POST.get('amount', '').strip()
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        messages.error(request, "Please enter a valid numeric bid amount.")
        return redirect('auction_detail', auction_id=auction.id)

    try:
        bid = place_bid(auction, request.user, amount)
    except BidError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Your bid of ₹{bid.amount} was placed successfully.")

    return redirect('auction_detail', auction_id=auction.id)
