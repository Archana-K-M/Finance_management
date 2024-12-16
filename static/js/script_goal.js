document.addEventListener("DOMContentLoaded", function () {
    const budgetContainer = document.getElementById("budget-container");

    // Fetch and display budgets for serial_id 22
    async function fetchBudgets() {
        const response = await fetch("/get_budgets/22");
        const data = await response.json();

        if (data.message) {
            budgetContainer.innerHTML = `<p>${data.message}</p>`;
            return;
        }

        data.forEach(budget => {
            const budgetCard = document.createElement("div");
            budgetCard.className = "budget-card";
            budgetCard.innerHTML = `
                <h3>Category: ${budget.category}</h3>
                <p>Limit: $${budget.limit}</p>
                <p>Spent: $${budget.spent}</p>
                <p>Remaining: $${budget.remaining}</p>
            `;
            budgetContainer.appendChild(budgetCard);
        });
    }

    fetchBudgets();

    // Navigate to Add Budget Page
    window.navigateToAddPage = function () {
        window.location.href = "/add_goal";
    };

    // Submit Budget Form
    const budgetForm = document.getElementById("budget-form");
    if (budgetForm) {
        budgetForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const category = document.getElementById("category").value;
            const limit = document.getElementById("limit").value;

            const response = await fetch("/set_budget", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    serial_id: 22,
                    category: category,
                    limit: parseFloat(limit)
                })
            });

            const result = await response.json();

            if (result.message === "Budget set successfully") {
                document.getElementById("popup").style.display = "block";
            }
        });
    }

    // Close Popup and redirect
    window.closePopup = function () {
        document.getElementById("popup").style.display = "none";
        window.location.href = "/goal";
    };
});
