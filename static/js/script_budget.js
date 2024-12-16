document.addEventListener("DOMContentLoaded", async () => {
    const serialId = 22;  // Default serial ID
    const transactionsTable = document.querySelector("#transactions-table tbody");

    try {
        // Fetch transactions from Flask backend
        const response = await fetch(`/get_transaction/${serialId}`);
        if (!response.ok) {
            throw new Error("Failed to fetch transactions");
        }

        const transactions = await response.json();

        // Populate table with transactions
        transactions.forEach(transaction => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${transaction.transaction_date}</td>
                <td>${transaction.transaction_type}</td>
                <td>${transaction.category}</td>
                <td>$${transaction.amount}</td>
                <td>${transaction.total ? `$${transaction.total}` : 'N/A'}</td>
            `;

            transactionsTable.appendChild(row);
        });
    } catch (error) {
        console.error("Error loading transactions:", error);
        alert("Failed to load transactions. Please try again later.");
    }
});
