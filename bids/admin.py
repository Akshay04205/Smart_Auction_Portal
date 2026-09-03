from django.contrib import admin

from .models import AuctionResult, Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    """
    Bids are shown for auditing/history purposes. They're read-only here
    (see has_add/change_permission) because every real bid must go through
    the validated place_bid() flow, not be typed in by hand.
    """
    list_display = ('auction', 'bidder', 'amount', 'created_at')
    list_filter = ('auction__status',)
    search_fields = ('bidder__username', 'auction__item__name')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuctionResult)
class AuctionResultAdmin(admin.ModelAdmin):
    """Auction results (winners) are created automatically when an auction closes - view only."""
    list_display = ('auction', 'winner', 'winning_price', 'closed_at')
    list_filter = ('auction__status',)
    search_fields = ('auction__item__name', 'winner__username')
    ordering = ('-closed_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
