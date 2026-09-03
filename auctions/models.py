from django.db import models


class Item(models.Model):
    """
    Anything that can be put up for auction. Generic on purpose - a lot of
    steel scrap, a piece of furniture, electronics, a vehicle, whatever.
    Example: "Vintage Desk", 1, "units", "Solid oak, minor scuffs".
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(
        max_length=20, blank=True,
        help_text="e.g. units, kg, Tons, Liters, pieces - leave blank if not applicable",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.unit:
            return f"{self.name} ({self.quantity} {self.unit})"
        return self.name


class Auction(models.Model):
    """
    An auction event for a specific Item.
    Holds pricing rules and the time window during which bidding is open.
    """

    # Status choices control what buyers can see/do:
    # DRAFT     -> admin is still setting it up, not visible to buyers
    # SCHEDULED -> visible but bidding hasn't started yet
    # ACTIVE    -> bidding is open
    # CLOSED    -> bidding has ended, winner has been decided
    STATUS_DRAFT = 'DRAFT'
    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_CLOSED, 'Closed'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='auctions')
    starting_price = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_increment = models.DecimalField(max_digits=12, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auction #{self.pk} - {self.item.name} [{self.status}]"

    # --- Helper methods used by views/bidding logic ---

    def highest_bid(self):
        """Return the current highest Bid for this auction, or None if no bids yet."""
        return self.bids.order_by('-amount', 'created_at').first()

    def current_price(self):
        """Current highest bid amount, or the starting price if nobody has bid yet."""
        top_bid = self.highest_bid()
        return top_bid.amount if top_bid else self.starting_price

    def minimum_next_bid(self):
        """The smallest amount a new bid must be to be accepted."""
        top_bid = self.highest_bid()
        if top_bid:
            return top_bid.amount + self.minimum_increment
        return self.starting_price

    def has_ended(self):
        from django.utils import timezone
        return timezone.now() >= self.end_time

    def has_started(self):
        from django.utils import timezone
        return timezone.now() >= self.start_time
