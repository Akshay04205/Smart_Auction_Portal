from django.core.management.base import BaseCommand

from bids.services import close_expired_auctions


class Command(BaseCommand):
    help = (
        "Closes any ACTIVE auction whose end_time has passed: locks bidding, "
        "picks the highest bidder as winner, and stores the AuctionResult. "
        "The website also does this automatically whenever a page is loaded, "
        "but for auctions to close exactly on time even with no visitors, "
        "schedule this command to run every minute, e.g. with cron:\n\n"
        "  * * * * * cd /path/to/project && /path/to/venv/bin/python manage.py close_expired_auctions"
    )

    def handle(self, *args, **options):
        closed = close_expired_auctions()
        if closed:
            self.stdout.write(self.style.SUCCESS(f"Closed {len(closed)} auction(s): " +
                                                   ", ".join(f"#{a.pk}" for a in closed)))
        else:
            self.stdout.write("No expired auctions to close.")
