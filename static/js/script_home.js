document.addEventListener('DOMContentLoaded', () => {
    const typewriterElement = document.getElementById("typewriter");
    const typewriterText = "Let's explore FinBuild..."; // The text to animate

    let i = 0;
    
    function typeWriter() {
        if (i < typewriterText.length) {
            typewriterElement.innerHTML += typewriterText.charAt(i);
            i++;
            setTimeout(typeWriter, 100); // Adjust typing speed here
        } else {
            // Reset the typewriter effect to start over after a short delay
            setTimeout(() => {
                typewriterElement.innerHTML = "";  // Clear the text
                i = 0;  // Reset the index to start typing again
                typeWriter();  // Restart typing
            }, 1500);  // Adjust the delay before restarting (in milliseconds)
        }
    }

    typeWriter();

    // Handle the login button click
    document.getElementById("loginBtn").addEventListener("click", () => {
        alert("Login functionality is not implemented yet.");
    });

    // Handle redirection to Statement Analysis page
    document.getElementById("goToStatementAnalysisBtn").addEventListener("click", () => {
        window.location.href = "/statement_analyse";
    });

    // Handle redirection to Budget Planner page
    document.getElementById("goToBudgetPlannerBtn").addEventListener("click", () => {
        window.location.href = "/budget_planner";
    });

    // Handle redirection to Budget Planner page
    document.getElementById("goToArticlesBtn").addEventListener("click", () => {
        window.location.href = "/articles";
    });
});
