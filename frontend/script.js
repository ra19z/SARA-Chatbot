const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

// Event listeners
sendButton.addEventListener('click', handleSend);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

async function handleSend() {
    const message = chatInput.value.trim();

    if (message === '') {
        chatInput.focus();
        return;
    }

    // Display user message
    displayUserMessage(message);

    // Clear and focus input
    chatInput.value = '';
    chatInput.focus();

    // Show loading indicator
    const loadingBubble = showLoadingBubble();
    const startTime = Date.now();
    const minWaitTime = 5000; // 5 seconds

    try {
        console.log('📤 Sending:', message);

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        const data = await response.json();
        console.log('Response:', data);

        // Ensure minimum wait time
        const elapsedTime = Date.now() - startTime;
        if (elapsedTime < minWaitTime) {
            await new Promise(resolve => 
                setTimeout(resolve, minWaitTime - elapsedTime)
            );
        }

        // Remove loading bubble
        removeLoadingBubble(loadingBubble);

        if (response.ok && data.reply) {
            // Check if it's a location type response
            if (data.type === 'location') {
                displayLocationMessage(data);
            } else {
                displayBotMessage(data.reply);
            }
        } else {
            const errorMsg = data.error || 'Error tidak diketahui';
            displayBotMessage(`❌ ${errorMsg}`);
        }

    } catch (error) {
        console.error('❌ Error:', error);
        removeLoadingBubble(loadingBubble);
        displayBotMessage(`❌ Koneksi error: ${error.message}`);
    }
}

function displayUserMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${escapeHtml(text)}</p>`;

    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function displayBotMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot';

    const avatar = document.createElement('div');
    avatar.className = 'bot-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${escapeHtml(text)}</p>`;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function displayLocationMessage(data) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot';

    const avatar = document.createElement('div');
    avatar.className = 'bot-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble location-bubble';
    
    bubble.innerHTML = `
        <p style="font-weight: bold; margin-bottom: 8px;">${escapeHtml(data.reply)}</p>
        <p style="font-size: 13px; color: #666; margin-bottom: 8px;">${escapeHtml(data.address)}</p>
        <div style="margin: 10px 0; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px; font-size: 12px;">
            ${escapeHtml(data.details)}
        </div>
        <a href="${data.maps_url}" target="_blank" rel="noopener noreferrer" class="maps-button">
            📍 Buka di Google Maps
        </a>
    `;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function showLoadingBubble() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot';
    wrapper.id = 'loading-bubble';

    const avatar = document.createElement('div');
    avatar.className = 'bot-avatar';
    avatar.textContent = '🤖';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'typing-indicator';
    loadingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    wrapper.appendChild(avatar);
    wrapper.appendChild(loadingDiv);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
    return wrapper;
}

function removeLoadingBubble(loadingBubble) {
    if (loadingBubble && loadingBubble.parentNode) {
        loadingBubble.remove();
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Test connection and show greeting
window.addEventListener('load', () => {
    console.log('🔍 Testing server connection...');
    fetch('/api/test')
        .then(res => res.json())
        .then(data => console.log('✅ Server OK:', data))
        .catch(err => console.error('❌ Server error:', err));
    
    // Show greeting message
    setTimeout(() => {
        displayBotMessage('Halo! 👋 Saya SARA, asisten digital untuk PT Samaratu Daya Teknik.Apa yang bisa saya bantu?');
    }, 500);
});