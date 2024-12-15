document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatBox = document.getElementById("chat-box");

    // Function to add a message to the chatbox
    function addMessage(sender, message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        messageDiv.innerText = message;
        chatBox.appendChild(messageDiv);

        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Send user input to Flask backend
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        addMessage("user", message);
        userInput.value = "";

        // Fetch bot response from Flask backend
        fetch("http://127.0.0.1:5000/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.response) {
                addMessage("bot", data.response);
            } else {
                addMessage("bot", "Sorry, something went wrong.");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            addMessage("bot", "Error connecting to the server.");
        });
    }

    // Event listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // Redirect to home
    document.getElementById("homeBtn").addEventListener("click", () => {
        window.location.href = "/dashboard";
    });
});
