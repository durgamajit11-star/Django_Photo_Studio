// ===============================
// GLOBAL CHATBOT SYSTEM
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const chatWindow = document.getElementById("chatWindow");
    const chatToggle = document.getElementById("chatToggle");
    const chatCloseBtn = document.getElementById("chatCloseBtn");
    const chatInput = document.getElementById("chatInput");
    const chatBody = document.getElementById("chatBody");
    const chatSendBtn = document.getElementById("chatSendBtn");

    if (!chatWindow) return;

    // ===============================
    // Toggle Chat
    // ===============================
    function toggleChat() {
        chatWindow.classList.toggle("active");

        // Mobile positioning
        if (window.innerWidth <= 576 && chatWindow.classList.contains("active")) {
            chatWindow.style.bottom = "auto";
            chatWindow.style.top = "70px";
        } else {
            chatWindow.style.bottom = "100px";
            chatWindow.style.top = "auto";
        }
    }

    chatToggle?.addEventListener("click", toggleChat);
    chatCloseBtn?.addEventListener("click", toggleChat);

    // ===============================
    // Send Message
    // ===============================
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage("user", message);
        chatInput.value = "";

        showTyping();

        setTimeout(() => {
            removeTyping();
            const reply = generateReply(message);
            appendMessage("bot", reply);
        }, 800);
    }

    chatSendBtn?.addEventListener("click", sendMessage);

    chatInput?.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });

    // ===============================
    // Append Message
    // ===============================
    function appendMessage(type, text) {
        const msg = document.createElement("div");
        msg.className = type === "user" ? "user-message" : "bot-message";

        const time = new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

        msg.innerHTML = `
            <div>${text}</div>
            <small class="chat-time">${time}</small>
        `;

        chatBody.appendChild(msg);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // ===============================
    // Typing Indicator
    // ===============================
    function showTyping() {
        const typing = document.createElement("div");
        typing.className = "bot-message typing";
        typing.id = "typingIndicator";
        typing.innerHTML = "Typing<span>.</span><span>.</span><span>.</span>";
        chatBody.appendChild(typing);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function removeTyping() {
        const typing = document.getElementById("typingIndicator");
        if (typing) typing.remove();
    }

    // ===============================
    // Smart Reply Logic
    // ===============================
    function generateReply(message) {
        const text = message.toLowerCase();
        const role = document.body.dataset.role || "USER";

        if (text.includes("booking") || text.includes("book")) {
            return "📅 You can manage bookings from your dashboard.";
        }

        if (text.includes("price") || text.includes("cost")) {
            return "💰 Packages start from ₹5,000. Use filters to compare.";
        }

        if (text.includes("studio")) {
            return "🔍 Browse studios using filters like city and rating.";
        }

        if (text.includes("help")) {
            return "🆘 I'm here to assist you. Ask me anything!";
        }

        if (text.includes("hello") || text.includes("hi")) {
            return "👋 Hello! Welcome to StudioSync.";
        }

        if (role === "STUDIO") {
            return "📊 As a Studio Owner, you can manage portfolio, bookings, and earnings.";
        }

        if (role === "ADMIN") {
            return "🛠 Admin panel allows you to manage users and platform settings.";
        }

        return "✅ Thanks for your message! How else can I help?";
    }

});