document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form submission

    const formData = new FormData();
    const bankName = document.getElementById("bank").value;
    const fileInput = document.getElementById("file").files[0];

    // Append inputs to FormData
    formData.append("bank", bankName);
    formData.append("file", fileInput);

    try {
        // Send request to Flask backend
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json(); // Parse JSON response

        // Display recommendation message
        document.getElementById("recommend_message").innerText = result.recommend_message;

        // Extract date and balance from data
        const data = result.data;
        const dates = data.map(item => item.Date);        // Extract 'date'
        const balances = data.map(item => item.Balance);  // Extract 'balance'

        // Plot the line chart using Chart.js
        const ctx = document.getElementById("lineChart").getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: dates,
                datasets: [{
                    label: "Balance over Time",
                    data: balances,
                    borderColor: "blue",
                    backgroundColor: "rgba(0, 123, 255, 0.2)",
                    borderWidth: 2,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: "blue"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: "top"
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Date"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Balance"
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Error:", error);
        alert("Error: Unable to process the file.");
    }
});

