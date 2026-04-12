// ===============================
// SHARED CHATBOT WIDGET
// ===============================

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('chatbot-container');
    const chatWindow = document.getElementById('chatWindow');
    const chatToggle = document.getElementById('chatToggle');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');
    const chatInput = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');
    const chatSendBtn = document.getElementById('chatSendBtn');

    if (!container || !chatWindow || !chatBody || !chatInput || !chatSendBtn) {
        return;
    }

    const messagesUrl = container.dataset.chatbotUrl || '/chatbot/messages/';
    const clearUrl = container.dataset.chatbotClearUrl || '/chatbot/clear/';
    let historyLoaded = false;
    let sending = false;

    function getCsrfToken() {
        const cookie = document.cookie.split('; ').find((row) => row.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    }

    function toggleChat() {
        chatWindow.classList.toggle('active');
        if (window.innerWidth <= 576 && chatWindow.classList.contains('active')) {
            chatWindow.style.bottom = 'auto';
            chatWindow.style.top = '70px';
        } else {
            chatWindow.style.bottom = '100px';
            chatWindow.style.top = 'auto';
        }

        if (chatWindow.classList.contains('active') && !historyLoaded) {
            loadHistory();
        }
    }

    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function createMessageElement(className, text) {
        const message = document.createElement('div');
        message.className = className;
        message.textContent = text;
        return message;
    }

    function appendMessage(className, text) {
        const message = createMessageElement(className, text);
        chatBody.appendChild(message);
        scrollToBottom();
    }

    function showTyping() {
        removeTyping();
        const typing = document.createElement('div');
        typing.className = 'bot-message typing';
        typing.id = 'typingIndicator';
        typing.innerHTML = 'Typing<span>.</span><span>.</span><span>.</span>';
        chatBody.appendChild(typing);
        scrollToBottom();
    }

    function removeTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) {
            typing.remove();
        }
    }

    function setDisabled(disabled) {
        chatInput.disabled = disabled;
        chatSendBtn.disabled = disabled;
        if (chatClearBtn) {
            chatClearBtn.disabled = disabled;
        }
    }

    function renderHistory(messages) {
        chatBody.innerHTML = '';
        if (!messages.length) {
            chatBody.appendChild(createMessageElement('bot-message', '👋 Hello! Ask me anything about StudioSync.'));
            const suggestions = document.createElement('div');
            suggestions.className = 'chat-suggestions mt-2 d-flex flex-wrap gap-2';
            [
                'What can I do on this platform?',
                'How do bookings work?',
                'How do payments and refunds work?'
            ].forEach((prompt) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-sm btn-outline-secondary chat-suggestion';
                button.dataset.prompt = prompt;
                button.textContent = prompt;
                suggestions.appendChild(button);
            });
            chatBody.appendChild(suggestions);
            scrollToBottom();
            return;
        }

        messages.forEach((entry) => {
            const className = entry.is_user ? 'user-message' : 'bot-message';
            appendMessage(className, entry.message || '');
        });
    }

    async function loadHistory() {
        try {
            const response = await fetch(messagesUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            });
            if (!response.ok) return;
            const data = await response.json();
            renderHistory(Array.isArray(data.messages) ? data.messages : []);
            historyLoaded = true;
        } catch (error) {
            console.error('Unable to load chatbot history', error);
        }
    }

    async function sendMessage(messageOverride) {
        const message = (messageOverride || chatInput.value || '').trim();
        if (!message || sending) return;

        sending = true;
        setDisabled(true);
        chatInput.value = '';
        appendMessage('user-message', message);
        showTyping();

        try {
            const response = await fetch(messagesUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            removeTyping();

            if (!response.ok) {
                appendMessage('bot-message', data.error || 'Sorry, I could not answer that right now.');
                return;
            }

            appendMessage('bot-message', data.bot_response || 'I am here to help with StudioSync.');
            historyLoaded = true;
        } catch (error) {
            removeTyping();
            appendMessage('bot-message', 'Connection problem. Please try again.');
            console.error('Chatbot send failed', error);
        } finally {
            sending = false;
            setDisabled(false);
            chatInput.focus();
        }
    }

    async function clearHistory() {
        if (!confirm('Clear chat history?')) return;

        try {
            const response = await fetch(clearUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                historyLoaded = false;
                renderHistory([]);
            }
        } catch (error) {
            console.error('Unable to clear chat history', error);
        }
    }

    chatToggle?.addEventListener('click', toggleChat);
    chatCloseBtn?.addEventListener('click', toggleChat);
    chatSendBtn.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    chatBody.addEventListener('click', (event) => {
        const suggestion = event.target.closest('.chat-suggestion');
        if (!suggestion) return;
        sendMessage(suggestion.dataset.prompt || suggestion.textContent || '');
    });

    chatClearBtn?.addEventListener('click', clearHistory);
});
