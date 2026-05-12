/**
 * CodeSentinel Contest Countdown Engine
 * Handles live countdown timers with premium formatting.
 */
(function () {
    "use strict";

    function pad(n) {
        return n < 10 ? "0" + n : n;
    }

    function updateTimers() {
        var timers = document.querySelectorAll(".contest-timer[data-target]");
        var now = new Date().getTime();

        timers.forEach(function (timer) {
            var targetIso = timer.getAttribute("data-target");
            if (!targetIso) return;
            
            var targetTime = new Date(targetIso).getTime();
            var diff = targetTime - now;

            if (diff <= 0) {
                // Determine if it's Live or Completed based on an end-time if provided
                var endTimeIso = timer.getAttribute("data-end");
                if (endTimeIso) {
                    var endDiff = new Date(endTimeIso).getTime() - now;
                    if (endDiff > 0) {
                        timer.innerHTML = '<span class="timer-live">Live Now</span>';
                        timer.closest('.contest-card')?.classList.add('contest-is-live');
                        return;
                    }
                }
                
                timer.innerHTML = '<span class="timer-ended">Ended</span>';
                timer.closest('.contest-card')?.classList.remove('contest-is-live');
                timer.closest('.contest-card')?.classList.add('contest-is-ended');
                return;
            }

            // Calculate time left
            var days = Math.floor(diff / (1000 * 60 * 60 * 24));
            var hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((diff % (1000 * 60)) / 1000);

            // Build HTML
            var html = "";
            if (days > 0) {
                html += '<div class="timer-segment"><span class="timer-val">' + pad(days) + '</span><span class="timer-lbl">d</span></div><span class="timer-sep">:</span>';
            }
            html += '<div class="timer-segment"><span class="timer-val">' + pad(hours) + '</span><span class="timer-lbl">h</span></div><span class="timer-sep">:</span>';
            html += '<div class="timer-segment"><span class="timer-val">' + pad(minutes) + '</span><span class="timer-lbl">m</span></div><span class="timer-sep">:</span>';
            html += '<div class="timer-segment"><span class="timer-val">' + pad(seconds) + '</span><span class="timer-lbl">s</span></div>';

            timer.innerHTML = html;
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        updateTimers();
        setInterval(updateTimers, 1000);
    });
})();
