document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("foodSearchForm");
    const searchInput = document.getElementById("foodSearch");
    const filterForm = document.getElementById("foodFiltersForm");

    const categorySelect = document.getElementById("category");
    const locationSelect = document.getElementById("location");
    const maxPriceInput = document.getElementById("max_price");
    const expirySelect = document.getElementById("expiry");
    const sortSelect = document.getElementById("sort");

    const foodGrid = document.getElementById("foodGrid");
    const foodCount = document.getElementById("foodCount");

    if (!foodGrid || !foodCount || !searchInput) {
        console.error("FoodLoop: Required Marketplace elements are missing.");
        return;
    }

    // Get the original food cards.
    const cards = Array.from(
        foodGrid.querySelectorAll(".marketplace-card")
    );

    const originalOrder = new Map(
        cards.map((card, index) => [card, index])
    );

    function normalize(value) {
        const text = (value || "").trim().toLowerCase();

        if (text.includes("cook")) return "cooked";
        if (text.includes("baker")) return "bakery";
        if (text.includes("produce") || text.includes("fruit")) {
            return "produce";
        }
        if (text.includes("beverage") || text.includes("drink")) {
            return "beverages";
        }
        if (text.includes("snack")) return "snacks";

        return text;
    }

    
    
    function getTitle(card) {
        return (
            card.querySelector("h3")?.textContent || ""
        ).trim().toLowerCase();
    }
    
    function getSearchText(card) {
        return [
            getTitle(card),
            card.querySelector(".food-description")?.textContent || "",
            card.dataset.category || "",
            card.dataset.location || ""
        ].join(" ").toLowerCase();
    }



    function getExpiryDate(card) {
        const value = card.dataset.expiry;

        if (value) {
            const date = new Date(value);

            if (!Number.isNaN(date.getTime())) {
                return date;
            }
        }

        // Fallback for cards displaying a time such as 5:30 PM.
        const timeText = card.querySelector(
            ".food-card-info div:last-child p"
        )?.textContent.trim();

        const match = timeText?.match(
            /^(\d{1,2}):(\d{2})\s*(AM|PM)$/i
        );

        if (!match) return null;

        let hours = Number(match[1]) % 12;

        if (match[3].toUpperCase() === "PM") {
            hours += 12;
        }

        const date = new Date();
        date.setHours(hours, Number(match[2]), 0, 0);

        return date;
    }

    function applyFilters() {
        const query = searchInput.value.trim().toLowerCase();
        const category = categorySelect?.value || "";
        const location = locationSelect?.value.toLowerCase() || "";
        const priceText = maxPriceInput?.value.trim() || "";
        const maxPrice = priceText === "" ? Infinity : Number(priceText);
        const expiryFilter = expirySelect?.value || "";
        const sortBy = sortSelect?.value || "";

        const now = new Date();

        // Filter the original cards using their actual displayed titles.
        let visibleCards = cards.filter(card => {
            const title = getTitle(card);
            const cardCategory = normalize(card.dataset.category);
            const cardLocation = (
                card.dataset.location || ""
            ).trim().toLowerCase();
            const price = Number(card.dataset.price);

            // Searching matches the food name, not its description.
            const matchesSearch =
                query === "" || title.includes(query);

            const matchesCategory =
                !category || cardCategory === category;

            const matchesLocation =
                !location || cardLocation.includes(location);

            const matchesPrice =
                priceText === "" ||
                (Number.isFinite(price) && price <= maxPrice);

            let matchesExpiry = true;

            if (expiryFilter) {
                const expiry = getExpiryDate(card);

                if (!expiry) {
                    matchesExpiry = false;
                } else {
                    const hoursRemaining =
                        (expiry.getTime() - now.getTime()) / 3600000;

                    if (expiryFilter === "today") {
                        matchesExpiry =
                            expiry.toDateString() === now.toDateString() &&
                            hoursRemaining >= 0;
                    } else {
                        matchesExpiry =
                            hoursRemaining >= 0 &&
                            hoursRemaining <= Number(expiryFilter);
                    }
                }
            }

            return (
                matchesSearch &&
                matchesCategory &&
                matchesLocation &&
                matchesPrice &&
                matchesExpiry
            );
        });

        // Sort the matching cards.
        visibleCards.sort((a, b) => {
            const priceA = Number(a.dataset.price);
            const priceB = Number(b.dataset.price);

            if (sortBy === "price_low") return priceA - priceB;
            if (sortBy === "price_high") return priceB - priceA;

            if (sortBy === "newest") {
                const dateA = new Date(a.dataset.created || 0);
                const dateB = new Date(b.dataset.created || 0);
                return dateB - dateA;
            }

            if (sortBy === "expiry") {
                const dateA = getExpiryDate(a);
                const dateB = getExpiryDate(b);

                if (!dateA && !dateB) return 0;
                if (!dateA) return 1;
                if (!dateB) return -1;

                return dateA - dateB;
            }

            return originalOrder.get(a) - originalOrder.get(b);
        });

        // Hide every card first.
        cards.forEach(card => {
            card.hidden = true;
        });

        // Show only matching cards, in the selected order.
        visibleCards.forEach(card => {
            card.hidden = false;
            foodGrid.appendChild(card);
        });

        // Show a message if nothing matches.
        let emptyMessage = foodGrid.querySelector(".js-no-results");

        if (visibleCards.length === 0) {
            if (!emptyMessage) {
                emptyMessage = document.createElement("div");
                emptyMessage.className =
                    "marketplace-empty js-no-results";

                emptyMessage.innerHTML = `
                    <div class="empty-icon">🍽️</div>
                    <h2>No food found</h2>
                    <p>Try another food name or change your filters.</p>
                `;

                foodGrid.appendChild(emptyMessage);
            }

            emptyMessage.hidden = false;
        } else if (emptyMessage) {
            emptyMessage.hidden = true;
        }

        foodCount.textContent =
            `${visibleCards.length} food listing` +
            `${visibleCards.length === 1 ? "" : "s"} found`;
    }

    // Search button: filter without reloading the page.
    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {
            event.preventDefault();
            applyFilters();
        });
    }

    // Apply Filters button: filter without reloading the page.
    if (filterForm) {
        filterForm.addEventListener("submit", function (event) {
            event.preventDefault();
            applyFilters();
        });
    }

    // Search as the user types.
    searchInput.addEventListener("input", applyFilters);

    // Apply filters whenever a selection changes.
    [
        categorySelect,
        locationSelect,
        maxPriceInput,
        expirySelect,
        sortSelect
    ].forEach(control => {
        if (control) {
            control.addEventListener("change", applyFilters);
        }
    });

    // Clear all search and filter values.
    const clearLink = document.querySelector(".filter-header a");

    if (clearLink) {
        clearLink.addEventListener("click", function (event) {
            event.preventDefault();

            searchInput.value = "";

            if (categorySelect) categorySelect.value = "";
            if (locationSelect) locationSelect.value = "";
            if (maxPriceInput) maxPriceInput.value = "";
            if (expirySelect) expirySelect.value = "";
            if (sortSelect) sortSelect.value = "";

            applyFilters();

            window.history.replaceState(
                {},
                "",
                window.location.pathname
            );
        });
    }

    // Display all cards when the page first loads.
    applyFilters();
});




document.addEventListener("DOMContentLoaded", function () {

    // ========================================
    // FOODLOOP: BACK TO TOP BUTTON
    // ========================================

    const backToTopButton = document.getElementById("backToTop");

    // Stop if the button does not exist on this page.
    if (backToTopButton) {

        // Show or hide the button based on scroll position.
        function toggleBackToTop() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add("show");
            } else {
                backToTopButton.classList.remove("show");
            }
        }

        // Smoothly scroll to the top when clicked.
        backToTopButton.addEventListener("click", function () {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });

        // Listen for scrolling.
        window.addEventListener("scroll", toggleBackToTop, {
            passive: true
        });

        // Set the correct button state on page load.
        toggleBackToTop();
    }

});


document.addEventListener("DOMContentLoaded", function () {
    const toggler = document.getElementById("foodloopToggler");
    const nav = document.getElementById("foodloopNav");

    if (!toggler || !nav) return;

    toggler.addEventListener("click", function () {
        const isOpen = nav.classList.toggle("open");

        toggler.classList.toggle("open", isOpen);
        toggler.setAttribute("aria-expanded", String(isOpen));
    });

    // Close the menu after clicking a navigation link
    nav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            nav.classList.remove("open");
            toggler.classList.remove("open");
            toggler.setAttribute("aria-expanded", "false");
        });
    });
});


document.getElementById("filterOpen").addEventListener("click", function () {
    document.querySelectorAll(".hidden").forEach(function (element) {
        element.classList.toggle("show");
    });
});