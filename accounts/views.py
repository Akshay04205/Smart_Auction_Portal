from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bids.models import AuctionResult
from bids.services import close_expired_auctions

from .forms import BuyerRegistrationForm


def register(request):
    """Buyer self-registration. Logs the new user straight in and sends them home."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
    else:
        form = BuyerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# NOTE: dashboard() and my_bids() were removed per request - Dashboard and
# My Bids pages/links no longer exist. My Won Auctions (below) is unchanged.


@login_required
def my_wins(request):
    """/my-wins/ - every auction this buyer has won."""
    close_expired_auctions()
    results = (
        AuctionResult.objects.filter(winner=request.user)
        .select_related('auction', 'auction__item')
        .order_by('-closed_at')
    )
    return render(request, 'my_wins.html', {'results': results})
