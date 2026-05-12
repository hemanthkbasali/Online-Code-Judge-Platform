/**
 * CodeSentinel Activity Heatmap
 * Renders a GitHub-style contribution graph from server-side JSON.
 * Completely self-contained — no external libs required.
 */
(function () {
    "use strict";

    // ── Helpers ────────────────────────────────────────────────────────────

    /** Format an ISO date string as "Mon DD, YYYY" */
    function formatDate(iso) {
        if (!iso) return "";
        var d = new Date(iso + "T00:00:00");
        var months = ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"];
        return months[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
    }

    /** Pluralise a word based on count */
    function plural(n, word) {
        return n + " " + word + (n === 1 ? "" : "s");
    }

    // ── Tooltip singleton ──────────────────────────────────────────────────

    var tooltip = null;

    function createTooltip() {
        tooltip = document.createElement("div");
        tooltip.className = "hm-tooltip";
        tooltip.innerHTML =
            '<span class="hm-tooltip-count"></span>' +
            '<span class="hm-tooltip-date"></span>';
        document.body.appendChild(tooltip);
    }

    function showTooltip(cell, count, dateStr, x, y) {
        var countEl = tooltip.querySelector(".hm-tooltip-count");
        var dateEl  = tooltip.querySelector(".hm-tooltip-date");

        countEl.textContent = count === 0
            ? "No submissions"
            : plural(count, "submission");
        dateEl.textContent = formatDate(dateStr);

        // Position above the cell, centred horizontally
        var GAP = 10;
        tooltip.style.left = "0px";
        tooltip.style.top  = "0px";
        tooltip.classList.add("hm-tooltip-visible");

        var tw = tooltip.offsetWidth;
        var th = tooltip.offsetHeight;
        var left = x - tw / 2;
        var top  = y - th - GAP;

        // Clamp to viewport
        left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
        if (top < 8) top = y + GAP + 10;

        tooltip.style.left = left + "px";
        tooltip.style.top  = top  + "px";
    }

    function hideTooltip() {
        if (tooltip) tooltip.classList.remove("hm-tooltip-visible");
    }

    // ── Grid builder ───────────────────────────────────────────────────────

    /**
     * Build the heatmap grid inside `root`.
     *
     * The CSS grid has:
     *   rows  = [month-label-row] + 7 day rows (Sun … Sat)
     *   columns = one per week (auto-flow column)
     *
     * Each week column contains:
     *   - optionally a .hm-month-label in row 1
     *   - 7 .hm-cell divs in rows 2-8
     *
     * @param {HTMLElement} root   - #hm-grid-root
     * @param {Array}       weeks  - [[{date,count,level}, …×7], …] oldest first
     * @param {Array}       months - [{label:"Jan", col:weekIndex}, …]
     */
    function buildGrid(root, weeks, months) {
        // Build a quick lookup: col-index → month label
        var monthMap = {};
        months.forEach(function (m) { monthMap[m.col] = m.label; });

        var fragment = document.createDocumentFragment();

        weeks.forEach(function (week, colIdx) {
            // Month label (row 1) — only emit when this col has a label
            if (monthMap[colIdx] !== undefined) {
                var label = document.createElement("span");
                label.className = "hm-month-label";
                label.style.gridColumn = String(colIdx + 1);
                label.style.gridRow    = "1";
                label.textContent = monthMap[colIdx];
                fragment.appendChild(label);
            }

            // Day cells (rows 2-8 → grid rows 2 through 8)
            week.forEach(function (day, dayIdx) {
                var cell = document.createElement("span");
                var lvl  = day.level;

                // Map negative level to CSS-safe class name (hm-l-1 → invisible)
                cell.className = "hm-cell hm-l" + (lvl < 0 ? "-1" : String(lvl));
                cell.style.gridColumn = String(colIdx + 1);
                cell.style.gridRow    = String(dayIdx + 2); // +2 because row 1 is month labels

                if (lvl >= 0 && day.date) {
                    // Tooltip events
                    cell.addEventListener("mouseenter", function (e) {
                        showTooltip(cell, day.count, day.date, e.clientX, e.clientY);
                    });
                    cell.addEventListener("mousemove", function (e) {
                        showTooltip(cell, day.count, day.date, e.clientX, e.clientY);
                    });
                    cell.addEventListener("mouseleave", hideTooltip);

                    // Accessibility
                    var label = day.count === 0
                        ? "No submissions on " + formatDate(day.date)
                        : plural(day.count, "submission") + " on " + formatDate(day.date);
                    cell.setAttribute("aria-label", label);
                    cell.setAttribute("role", "img");
                }

                fragment.appendChild(cell);
            });
        });

        root.appendChild(fragment);
    }

    // ── Animate-in ─────────────────────────────────────────────────────────

    /**
     * Staggered reveal: cells animate from opacity 0 → 1 in column order
     * using a lightweight requestAnimationFrame cascade.
     */
    function animateCells(root) {
        var cells = root.querySelectorAll(".hm-cell:not(.hm-l-1)");
        cells.forEach(function (cell, i) {
            cell.style.opacity = "0";
            cell.style.transition = "opacity 220ms ease " + Math.min(i * 2, 800) + "ms, " +
                "transform 140ms cubic-bezier(0.34, 1.56, 0.64, 1), " +
                "box-shadow 140ms ease, filter 140ms ease";
        });

        // Trigger reflow then fade in
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                cells.forEach(function (cell) {
                    cell.style.opacity = "1";
                });
            });
        });
    }

    // ── Init ───────────────────────────────────────────────────────────────

    function init() {
        var dataEl = document.getElementById("hm-data");
        var root   = document.getElementById("hm-grid-root");

        if (!dataEl || !root) return; // Not on dashboard page — bail silently

        var weeks, months;
        try {
            weeks  = JSON.parse(dataEl.dataset.weeks  || "[]");
            months = JSON.parse(dataEl.dataset.months || "[]");
        } catch (e) {
            console.warn("[heatmap] Failed to parse heatmap data:", e);
            return;
        }

        if (!weeks.length) return;

        createTooltip();
        buildGrid(root, weeks, months);
        animateCells(root);
    }

    document.addEventListener("DOMContentLoaded", init);
})();
