from django.contrib import admin

# Imported from the bids app so admins can see all bids for an auction
# directly on the Auction edit page (see BidInline below).
from bids.models import Bid

from .models import Auction, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('unit',)
    ordering = ('-created_at',)


class BidInline(admin.TabularInline):
    """Read-only view of every bid on this auction, shown right on the Auction admin page."""
    model = Bid
    extra = 0
    can_delete = False
    readonly_fields = ('bidder', 'amount', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request, obj=None):
        # Bids must only ever be created through the real bidding flow
        # (with its validation), never typed directly into the admin.
        return False


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'status', 'starting_price', 'current_price_display', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('item__name',)
    list_editable = ('status',)  # lets the admin quickly activate/close an auction from the list page
    date_hierarchy = 'start_time'
    inlines = [BidInline]
    fields = ('item', 'starting_price', 'minimum_increment', 'start_time', 'end_time', 'status', 'created_at')
    readonly_fields = ('created_at',)

    def current_price_display(self, obj):
        return obj.current_price()
    current_price_display.short_description = 'Current Highest Bid'
