from django.conf import settings
from django.db import models
from auctions.models import Auction


class Bid(models.Model):
    """
    A single bid placed by a buyer on an auction.

    IMPORTANT: every bid is its own row. We never overwrite a previous bid -
    the full bidding history (Buyer A -> 31000, Buyer B -> 32000, ...) is
    kept so it can be displayed and so the highest bid can be recalculated
    at any time from the data itself.
    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest bids first, matching the required bid-history display

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on Auction #{self.auction_id}"


class AuctionResult(models.Model):
    """
    The outcome of a closed auction. Created only once, when the auction
    closes (Phase 6). If nobody bid, winner/winning_bid/winning_price stay
    null - the auction still closes, it just has no winner.
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='result')
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions'
    )
    winning_bid = models.ForeignKey(
        Bid, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    winning_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    closed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.winner:
            return f"Result for Auction #{self.auction_id}: {self.winner.username} won at {self.winning_price}"
        return f"Result for Auction #{self.auction_id}: no bids, no winner"
