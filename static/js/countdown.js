// Live countdown timer(s) for auction cards / auction detail page.
//
// SECURITY NOTE: this only updates what the visitor SEES. It never decides
// whether a bid is accepted - the Django backend (bids/services.py) always
// re-checks the real auction end_time in the database before saving a bid,
// so a manipulated or frozen browser clock can't be used to bid late.
document.addEventListener('DOMContentLoaded', function () {
  var countdownEls = document.querySelectorAll('.countdown[data-end]');

  countdownEls.forEach(function (el) {
    var endTime = new Date(el.dataset.end).getTime();
    var timer = null;

    function pad(n) {
      return String(n).padStart(2, '0');
    }

    function tick() {
      var distance = endTime - Date.now();

      if (distance <= 0) {
        el.textContent = 'Auction Closed';
        el.classList.add('countdown-ended');
        if (timer) clearInterval(timer);

        // Disable the bid form immediately for UX - the backend enforces
        // this independently, this just avoids a confusing "rejected" round trip.
        var bidForm = document.getElementById('bid-form');
        if (bidForm) {
          Array.prototype.forEach.call(bidForm.elements, function (field) {
            field.disabled = true;
          });
        }

        // Reload once so the server can process the actual closing
        // (status change, winner selection) and show the final result.
        setTimeout(function () {
          window.location.reload();
        }, 1500);
        return;
      }

      var hours = Math.floor(distance / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      el.textContent = pad(hours) + ':' + pad(minutes) + ':' + pad(seconds);
    }

    tick();
    timer = setInterval(tick, 1000);
  });
});
