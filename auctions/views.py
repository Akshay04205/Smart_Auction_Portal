from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from bids.services import close_expired_auctions
from .models import Auction


@login_required
def home(request):
    """Homepage: hero section + a preview of currently active auctions.
    Login required first - anonymous visitors are redirected to /accounts/login/."""
    # Close anything that expired since the last time someone loaded a page,
    # so the homepage never shows a stale ACTIVE auction that has actually ended.
    close_expired_auctions()

    active_auctions = Auction.objects.filter(status=Auction.STATUS_ACTIVE).order_by('end_time')[:6]
    return render(request, 'home.html', {'active_auctions': active_auctions})


@login_required
def auction_list(request):
    """/auctions/ - full auction listing (scheduled, active, and closed; drafts are admin-only)."""
    close_expired_auctions()

    # Order ACTIVE first, then SCHEDULED, then CLOSED, rather than plain
    # alphabetical status ordering (which would be confusing to a visitor).
    status_order = Case(
        When(status=Auction.STATUS_ACTIVE, then=Value(0)),
        When(status=Auction.STATUS_SCHEDULED, then=Value(1)),
        When(status=Auction.STATUS_CLOSED, then=Value(2)),
        output_field=IntegerField(),
    )
    auctions = (
        Auction.objects.exclude(status=Auction.STATUS_DRAFT)
        .annotate(_status_order=status_order)
        .order_by('_status_order', 'end_time')
        .select_related('item')
    )
    return render(request, 'auction_list.html', {'auctions': auctions})


@login_required
def auction_detail(request, auction_id):
    """/auction/<id>/ - full details, bid history, and the bid form."""
    close_expired_auctions()

    auction = get_object_or_404(Auction, pk=auction_id)

    # Draft auctions are still being set up by the admin - buyers shouldn't
    # be able to view them even if they guess the URL.
    if auction.status == Auction.STATUS_DRAFT and not request.user.is_staff:
        raise Http404("Auction not found.")

    highest_bid = auction.highest_bid()
    bid_history = auction.bids.select_related('bidder').all()

    context = {
        'auction': auction,
        'highest_bid': highest_bid,
        'bid_history': bid_history,
        'minimum_next_bid': auction.minimum_next_bid(),
        'now': timezone.now(),
    }
    return render(request, 'auction_detail.html', context)
