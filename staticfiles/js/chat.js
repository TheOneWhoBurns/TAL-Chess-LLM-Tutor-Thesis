document.addEventListener('DOMContentLoaded', () => {
    // Initialize DOM elements
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const historyContent = document.querySelector('.history-content');

    // Function to safely scroll to bottom
    function scrollToBottom(element) {
        if (element) {
            element.scrollTop = element.scrollHeight;
        }
    }

    // Set up MutationObserver for chat messages
    const chatObserver = new MutationObserver(() => {
        scrollToBottom(chatMessages);
    });

    // Start observing chat messages
    chatObserver.observe(chatMessages, {
        childList: true,
        subtree: true
    });

    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatMessages.appendChild(messageElement);
    }

    async function sendMessage(message) {
        try {
            addMessage('You', message);
            userInput.value = '';
            userInput.focus();

            const response = await fetch('/send_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                addMessage('Tutor', data.response);

                // Dispatch server response to chess component
                const serverEvent = new CustomEvent('serverResponse', { detail: data });
                window.dispatchEvent(serverEvent);
            } else {
                throw new Error('Server returned error status');
            }

        } catch (error) {
            console.error('Error:', error);
            addMessage('System', 'An error occurred. Please try again.');
        }
    }

    // Handle form submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;
        sendMessage(message);
    });

    // Listen for chess moves
    window.addEventListener('chessMove', (e) => {
        sendMessage(e.detail);
    });

    // Listen for game reset
    window.addEventListener('chessReset', () => {
        chatMessages.innerHTML = ''; // Clear chat on new game
        sendMessage('new game');
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initial scroll to bottom for both containers
    scrollToBottom(chatMessages);
    scrollToBottom(historyContent);
});