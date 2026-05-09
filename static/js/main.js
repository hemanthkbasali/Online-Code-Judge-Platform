(function () {
    function animateCounters() {
        document.querySelectorAll(".counter").forEach(function (counter) {
            var target = Number(counter.dataset.target || "0");
            var isDecimal = String(counter.dataset.target || "").includes(".");
            var duration = 900;
            var startTime = performance.now();

            function tick(now) {
                var progress = Math.min((now - startTime) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                var value = target * eased;
                counter.textContent = isDecimal ? value.toFixed(1) : Math.round(value);
                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            requestAnimationFrame(tick);
        });
    }

    function setupPasswordToggles() {
        document.querySelectorAll(".password-toggle").forEach(function (button) {
            button.addEventListener("click", function () {
                var input = button.closest(".password-wrap").querySelector("input");
                var icon = button.querySelector("i");
                var showing = input.type === "text";
                input.type = showing ? "password" : "text";
                icon.className = showing ? "bi bi-eye" : "bi bi-eye-slash";
            });
        });
    }

    function setupToasts() {
        document.querySelectorAll(".toast").forEach(function (toastNode) {
            var toast = bootstrap.Toast.getOrCreateInstance(toastNode, { delay: 3200 });
            toast.show();
        });
    }

    window.getCookie = function (name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    };

    document.addEventListener("DOMContentLoaded", function () {
        animateCounters();
        setupPasswordToggles();
        setupToasts();
    });
})();
