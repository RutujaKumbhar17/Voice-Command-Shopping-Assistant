/**
 * FreshRoot - AI Voice Assistant Floating Widget Engine
 * Features:
 * - Direct activation without redirection
 * - Soft, natural female voice speech synthesis & MiniMax TTS
 * - Immediate speech interruption when microphone is activated
 * - Persistent conversation history across pages
 * - Prominent cart price summary card displayed in chat
 * - Short, crisp, direct assistant answers
 * - Live real-time sync with backend cart database & UI
 */

(function () {
    const STORAGE_KEY = 'freshroot_voice_chat_history';
    let recognition = null;
    let isListening = false;
    let isSpeaking = false;
    let widgetOpen = false;
    let selectedLanguage = 'en-US';
    let audioElement = null;
    let availableVoices = [];

    // Preload & Cache Browser Voices for Soft Female Speech
    function loadVoices() {
        if ('speechSynthesis' in window) {
            availableVoices = window.speechSynthesis.getVoices();
        }
    }
    loadVoices();
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Find the softest, most natural female voice for given language
    function getSoftFemaleVoice(langCode) {
        if (!window.speechSynthesis) return null;
        if (!availableVoices || availableVoices.length === 0) {
            availableVoices = window.speechSynthesis.getVoices();
        }
        if (!availableVoices || availableVoices.length === 0) return null;

        const langPrefix = (langCode || 'en').split('-')[0].toLowerCase();
        const matchingLangVoices = availableVoices.filter(v => v.lang.toLowerCase().startsWith(langPrefix));
        const pool = matchingLangVoices.length > 0 ? matchingLangVoices : availableVoices;

        const preferredFemaleNames = [
            'microsoft jenny online (natural)',
            'microsoft zira',
            'microsoft aria online (natural)',
            'microsoft sonia online (natural)',
            'google us english',
            'google uk english female',
            'samantha',
            'victoria',
            'karen',
            'moira',
            'tessa',
            'serena',
            'female',
            'natural',
            'en-us'
        ];

        for (const nameKeyword of preferredFemaleNames) {
            const found = pool.find(v => v.name.toLowerCase().includes(nameKeyword));
            if (found) return found;
        }

        return pool[0] || availableVoices[0];
    }

    // Stop all audio playback & speech synthesis immediately
    function stopAllSpeech() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        if (audioElement) {
            audioElement.pause();
            audioElement.currentTime = 0;
        }
        isSpeaking = false;
    }

    // Initialize Web Speech Recognition
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function () {
            stopAllSpeech();
            isListening = true;
            updateWidgetUIState('listening');
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            handleUserVoiceInput(transcript);
        };

        recognition.onerror = function (event) {
            console.warn('[AI Assistant] Recognition error:', event.error);
            isListening = false;
            updateWidgetUIState('idle');
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
                addChatMessage('bot', `I couldn't hear you clearly (${event.error}). Please click the microphone or type below.`);
            }
        };

        recognition.onend = function () {
            isListening = false;
            if (!isSpeaking) {
                updateWidgetUIState('idle');
            }
        };
    }

    // Audio Player for backend TTS
    function getAudioElement() {
        if (!audioElement) {
            audioElement = document.createElement('audio');
            audioElement.id = 'aiWidgetAudioPlayer';
            audioElement.style.display = 'none';
            document.body.appendChild(audioElement);
        }
        return audioElement;
    }

    // Speak Text with a Soft, Natural Female Voice
    function speakText(text, onComplete) {
        if (!text) {
            if (onComplete) onComplete();
            return;
        }

        stopAllSpeech();

        if ('speechSynthesis' in window) {
            isSpeaking = true;
            updateWidgetUIState('speaking');

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.pitch = 1.08;
            utterance.rate = 0.96;
            utterance.volume = 1.0;
            utterance.lang = selectedLanguage;

            const femaleVoice = getSoftFemaleVoice(selectedLanguage);
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }

            utterance.onend = function () {
                isSpeaking = false;
                updateWidgetUIState('idle');
                if (onComplete) onComplete();
            };

            utterance.onerror = function () {
                isSpeaking = false;
                updateWidgetUIState('idle');
                if (onComplete) onComplete();
            };

            window.speechSynthesis.speak(utterance);
        } else {
            if (onComplete) onComplete();
        }
    }

    // Conversation History Storage in LocalStorage
    function getStoredHistory() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveHistoryItem(sender, text, extraHtml) {
        try {
            const history = getStoredHistory();
            history.push({
                sender: sender,
                text: text,
                extraHtml: extraHtml || '',
                timestamp: new Date().toISOString()
            });
            if (history.length > 40) history.shift();
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        } catch (e) {}
    }

    function clearStoredHistory() {
        try {
            localStorage.removeItem(STORAGE_KEY);
            const chat = document.getElementById('aiChatMessages');
            if (chat) {
                chat.innerHTML = `
                    <div class="ai-msg system">
                        <i class="fa-solid fa-microphone-lines"></i> History cleared. Soft Female Voice active.
                    </div>
                `;
            }
        } catch (e) {}
    }

    function renderStoredHistory() {
        const chat = document.getElementById('aiChatMessages');
        if (!chat) return;

        const history = getStoredHistory();
        if (!history || history.length === 0) {
            chat.innerHTML = `
                <div class="ai-msg system">
                    <i class="fa-solid fa-microphone-lines"></i> Soft Female Voice Active • Speak or tap chips
                </div>
            `;
            return;
        }

        chat.innerHTML = `
            <div class="ai-msg system">
                <i class="fa-solid fa-clock-rotate-left"></i> Restored previous conversation
            </div>
        `;

        history.forEach(item => {
            const msgDiv = document.createElement('div');
            msgDiv.className = `ai-msg ${item.sender}`;
            if (item.sender === 'bot') {
                msgDiv.innerHTML = `
                    <div class="ai-badge"><i class="fa-solid fa-robot"></i> FreshRoot Assistant</div>
                    <div>${item.text}</div>
                    ${item.extraHtml || ''}
                `;
            } else if (item.sender === 'user') {
                msgDiv.innerHTML = `<div>${item.text}</div>`;
            } else {
                msgDiv.innerHTML = item.text;
            }
            chat.appendChild(msgDiv);
        });

        chat.scrollTop = chat.scrollHeight;
    }

    // Inject Widget HTML into DOM
    function injectWidgetDOM() {
        if (document.getElementById('freshrootVoiceWidget')) return;

        const widgetHTML = `
        <div id="freshrootVoiceWidget" class="ai-voice-widget">
            <div class="ai-widget-header">
                <div class="ai-widget-title">
                    <i class="fa-solid fa-robot"></i>
                    <span>FreshRoot AI Assistant</span>
                </div>
                <div class="ai-widget-controls">
                    <button class="ai-widget-clear-btn" id="aiWidgetClearBtn" title="Clear Conversation History">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                    <button class="ai-widget-close-btn" id="aiWidgetCloseBtn" title="Close Assistant">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            </div>

            <div class="ai-widget-status" id="aiWidgetStatusBar">
                <div class="ai-status-indicator">
                    <span class="ai-status-dot" id="aiStatusDot"></span>
                    <span id="aiStatusLabel">Ready</span>
                </div>
                <div class="ai-audio-wave" id="aiAudioWave" style="display: none;">
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
            </div>

            <div class="ai-chat-messages" id="aiChatMessages"></div>

            <div class="ai-quick-chips">
                <button class="ai-chip" data-cmd="What is in my cart?">🛒 What is in my cart?</button>
                <button class="ai-chip" data-cmd="What is the price of my cart?">💰 Cart Cost</button>
                <button class="ai-chip" data-cmd="Add bananas to cart">🍌 Add Bananas</button>
                <button class="ai-chip" data-cmd="Add 2 kg potatoes to cart">🥔 Add 2kg Potatoes</button>
                <button class="ai-chip" data-cmd="What is the price of apples?">🍎 Price of Apples</button>
                <button class="ai-chip" data-cmd="How many items in store?">🥦 Store Inventory</button>
            </div>

            <div class="ai-widget-bottom">
                <button class="ai-mic-trigger" id="aiWidgetMicBtn" title="Speak to Assistant">
                    <i class="fa-solid fa-microphone"></i>
                </button>
                <input type="text" id="aiWidgetTextInput" class="ai-text-input" placeholder="Ask 'What is in my cart?' or 'Add apples'..." />
                <button class="ai-send-btn" id="aiWidgetSendBtn" title="Send">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </div>
        </div>
        `;

        const div = document.createElement('div');
        div.innerHTML = widgetHTML;
        document.body.appendChild(div.firstElementChild);

        // Inject Popup Tooltip above Floating Robot Icon
        if (!document.getElementById('aiVoiceTooltip')) {
            const tooltipDiv = document.createElement('div');
            tooltipDiv.id = 'aiVoiceTooltip';
            tooltipDiv.className = 'floating-ai-tooltip';
            tooltipDiv.innerHTML = `
                <span class="tooltip-icon"><i class="fa-solid fa-microphone-lines"></i></span>
                <span class="tooltip-text">AI Voice Assistant<br><span style="color: #10b981; font-weight: 500; font-size: 11px;">Tap robot to speak</span></span>
                <button class="tooltip-close" title="Dismiss" onclick="event.stopPropagation(); document.getElementById('aiVoiceTooltip').style.display='none';">&times;</button>
            `;
            tooltipDiv.onclick = function (e) {
                e.stopPropagation();
                activateVoiceAssistant();
            };
            document.body.appendChild(tooltipDiv);
        }

        renderStoredHistory();

        // Bind events
        document.getElementById('aiWidgetCloseBtn').addEventListener('click', closeVoiceWidget);
        document.getElementById('aiWidgetClearBtn').addEventListener('click', clearStoredHistory);
        document.getElementById('aiWidgetMicBtn').addEventListener('click', function (e) {
            e.preventDefault();
            toggleListening();
        });

        document.getElementById('aiWidgetSendBtn').addEventListener('click', sendTextMessage);
        document.getElementById('aiWidgetTextInput').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendTextMessage();
        });

        document.querySelectorAll('.ai-chip').forEach(chip => {
            chip.addEventListener('click', function () {
                const cmd = this.getAttribute('data-cmd');
                handleUserVoiceInput(cmd);
            });
        });
    }

    // Update UI states
    function updateWidgetUIState(state) {
        const dot = document.getElementById('aiStatusDot');
        const label = document.getElementById('aiStatusLabel');
        const wave = document.getElementById('aiAudioWave');
        const micBtn = document.getElementById('aiWidgetMicBtn');
        const fabBtn = document.querySelector('.floating-ai-btn');

        if (!dot || !label) return;

        dot.className = 'ai-status-dot';
        if (micBtn) micBtn.className = 'ai-mic-trigger';
        if (fabBtn) fabBtn.classList.remove('active-listening', 'speaking');

        if (state === 'listening') {
            dot.classList.add('listening');
            label.innerText = 'Listening to you...';
            if (wave) wave.style.display = 'flex';
            if (micBtn) micBtn.classList.add('listening');
            if (fabBtn) fabBtn.classList.add('active-listening');
        } else if (state === 'speaking') {
            dot.classList.add('speaking');
            label.innerText = 'Assistant speaking...';
            if (wave) wave.style.display = 'flex';
            if (fabBtn) fabBtn.classList.add('speaking');
        } else if (state === 'processing') {
            dot.classList.add('processing');
            label.innerText = 'Processing...';
            if (wave) wave.style.display = 'none';
        } else {
            label.innerText = 'Ready • Click Mic to talk';
            if (wave) wave.style.display = 'none';
        }
    }

    // Add message to chat box & save to history
    function addChatMessage(sender, text, extraHtml = '', saveToStorage = true) {
        const chat = document.getElementById('aiChatMessages');
        if (!chat) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-msg ${sender}`;

        if (sender === 'bot') {
            msgDiv.innerHTML = `
                <div class="ai-badge"><i class="fa-solid fa-robot"></i> FreshRoot Assistant</div>
                <div>${text}</div>
                ${extraHtml}
            `;
        } else if (sender === 'user') {
            msgDiv.innerHTML = `<div>${text}</div>`;
        } else {
            msgDiv.innerHTML = text;
        }

        chat.appendChild(msgDiv);
        chat.scrollTop = chat.scrollHeight;

        if (saveToStorage) {
            saveHistoryItem(sender, text, extraHtml);
        }
    }

    // Activate Voice Assistant Function
    function activateVoiceAssistant() {
        injectWidgetDOM();
        const widget = document.getElementById('freshrootVoiceWidget');
        if (!widget) return;

        // Hide tooltip popup when assistant is open
        const tooltip = document.getElementById('aiVoiceTooltip');
        if (tooltip) tooltip.style.display = 'none';

        widget.classList.add('open');
        widgetOpen = true;

        const history = getStoredHistory();
        const activationGreeting = "Voice assistant activated. How can I help you?";

        if (history.length === 0) {
            addChatMessage('bot', `<strong>Activated!</strong> How can I help you?
            <ul style="margin: 6px 0 0 16px; font-size: 12px; line-height: 1.5;">
                <li>"What is the price of my cart?"</li>
                <li>"Add bananas to my shopping list"</li>
                <li>"What is the price of apples?"</li>
                <li>"Add 2 kg potatoes to cart"</li>
            </ul>`);
        }

        speakText(activationGreeting, function () {
            startListening();
        });
    }

    function closeVoiceWidget() {
        const widget = document.getElementById('freshrootVoiceWidget');
        if (widget) {
            widget.classList.remove('open');
            widgetOpen = false;
        }

        // Show tooltip popup when assistant is closed
        const tooltip = document.getElementById('aiVoiceTooltip');
        if (tooltip) tooltip.style.display = 'flex';

        stopListening();
        stopAllSpeech();
    }

    function toggleListening() {
        stopAllSpeech();
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    }

    function startListening() {
        stopAllSpeech();

        if (!recognition) {
            addChatMessage('bot', "Speech recognition is not supported in this browser. You can type commands in the box below!");
            return;
        }

        try {
            recognition.lang = selectedLanguage;
            recognition.start();
        } catch (e) {
            console.warn('[AI Assistant] Recognition start failed or already active:', e);
        }
    }

    function stopListening() {
        if (recognition && isListening) {
            try {
                recognition.stop();
            } catch (e) {}
        }
        isListening = false;
        updateWidgetUIState('idle');
    }

    function sendTextMessage() {
        const input = document.getElementById('aiWidgetTextInput');
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        handleUserVoiceInput(text);
    }

    function getApiUrl(path) {
        if (window.location.protocol === 'file:' || (window.location.port !== '5000' && window.location.port !== '')) {
            return 'http://127.0.0.1:5000' + path;
        }
        return path;
    }

    // Global session context for conversational flow (e.g. pending item quantity)
    window.voiceSessionContext = window.voiceSessionContext || {};

    // Process user input (from voice or text)
    async function handleUserVoiceInput(transcript) {
        if (!transcript || !transcript.trim()) return;

        stopAllSpeech();
        addChatMessage('user', transcript);
        updateWidgetUIState('processing');

        try {
            const res = await fetch(getApiUrl('/api/voice-command'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: transcript,
                    language: selectedLanguage,
                    context: window.voiceSessionContext
                })
            });

            const data = await res.json();

            if (data && data.success) {
                let extraHtml = '';

                // Cache live cart snapshot to localStorage
                if (data.cart) {
                    try {
                        localStorage.setItem('freshroot_live_cart', JSON.stringify(data.cart));
                    } catch (e) {}
                }

                // 1. Ask for Quantity when user didn't specify
                if (data.intent === 'ask_quantity') {
                    window.voiceSessionContext = { pending_item: data.pending_item };
                    const pItem = data.pending_item || 'item';
                    extraHtml += `
                        <div style="margin-top: 10px; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px;">
                            <div style="font-size: 12.5px; color: #94a3b8; margin-bottom: 6px;">Tap or speak a quantity:</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                <button class="ai-chip" onclick="window.FreshRootVoice.handleCommand('1 kg')">1 kg</button>
                                <button class="ai-chip" onclick="window.FreshRootVoice.handleCommand('2 kg')">2 kg</button>
                                <button class="ai-chip" onclick="window.FreshRootVoice.handleCommand('3 kg')">3 kg</button>
                                <button class="ai-chip" onclick="window.FreshRootVoice.handleCommand('5 kg')">5 kg</button>
                            </div>
                        </div>
                    `;
                }

                // 2. Add Item: Automatic addition already completed on backend
                else if (data.intent === 'add_item') {
                    window.voiceSessionContext = {};
                    // Instantly sync UI
                    refreshCartBadge();
                    if (typeof window.loadCart === 'function') window.loadCart();
                    window.dispatchEvent(new CustomEvent('cartUpdated', { detail: data.cart }));

                    if (data.matched_products && data.matched_products.length > 0) {
                        const p = data.matched_products[0];
                        extraHtml += `
                            <div class="ai-cart-summary-card" style="border-left: 4px solid #10b981; margin-top: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #10b981; font-weight: 700;"><i class="fa-solid fa-circle-check"></i> Automatically Added to Cart</span>
                                    <strong style="color: #f8fafc;">₹${p.product_price}/kg</strong>
                                </div>
                                <div style="font-size: 13px; color: #cbd5e1; margin: 5px 0 8px;">
                                    ${p.product_title || p.product_type} has been added directly to your cart.
                                </div>
                                <a href="cart.html" class="ai-view-cart-link">View Cart & Checkout →</a>
                            </div>
                        `;
                    }
                }

                // 2. View Cart Total
                else if (data.intent === 'get_cart_total' || data.intent === 'view_cart') {
                    const cart = data.cart || [];
                    const total = cart.reduce((sum, item) => sum + (item.subtotal || 0), 0);

                    if (cart.length > 0) {
                        extraHtml += `
                            <div class="ai-cart-summary-card">
                                <div class="ai-cart-summary-header">
                                    <span><i class="fa-solid fa-cart-shopping"></i> Shopping Cart</span>
                                    <strong>Total: ₹${total}</strong>
                                </div>
                                <div class="ai-cart-summary-items">
                                    ${cart.map(i => `<div>• ${i.qty} ${i.product_type || i.product_title} - ₹${i.subtotal}</div>`).join('')}
                                </div>
                                <a href="cart.html" class="ai-view-cart-link">Go to Cart & Checkout →</a>
                            </div>
                        `;
                    }
                }

                // 3. Search Discovery (Render cards with Add button only on search/browse)
                else if (data.intent === 'search_item' && data.matched_products && data.matched_products.length > 0) {
                    extraHtml += '<div style="margin-top:8px;">';
                    data.matched_products.slice(0, 3).forEach(p => {
                        extraHtml += `
                            <div class="ai-product-card">
                                <img src="./image/${p.product_image || 'capsicum.jpg'}" onerror="this.src='./image/background1.jpg'" alt="${p.product_title || p.product_type}" />
                                <div class="ai-product-info">
                                    <div class="ai-product-title">${p.product_title || p.product_type}</div>
                                    <div class="ai-product-price">₹${p.product_price || p.subtotal}</div>
                                </div>
                                <button class="ai-add-cart-btn" onclick="window.FreshRootVoice.addToCartDirect(${p.product_id})">Add to Cart</button>
                            </div>
                        `;
                    });
                    extraHtml += '</div>';

                    if (typeof window.renderProductsGrid === 'function') {
                        window.renderProductsGrid(data.matched_products);
                    }
                }

                if (data.suggestions && data.suggestions.recommendations) {
                    extraHtml += '<div style="font-size:12px; margin-top:8px; color:#cbd5e1; background:rgba(255,255,255,0.05); padding:6px 10px; border-radius:8px;"><strong>Recommendations:</strong> ';
                    extraHtml += data.suggestions.recommendations.map(r => `${r.name} (₹${r.price})`).join(', ');
                    extraHtml += '</div>';
                }

                addChatMessage('bot', data.response_speech, extraHtml);

                // Play soft female audio response
                if (data.audio_b64) {
                    playAudioB64(data.audio_b64, data.response_speech);
                } else {
                    speakText(data.response_speech);
                }

                // Sync Cart Badges & Live Cart on cart.html
                refreshCartBadge();
                if (typeof window.loadCart === 'function') {
                    window.loadCart();
                }
                window.dispatchEvent(new CustomEvent('cartUpdated'));
                if (typeof window.updateCartBadge === 'function') {
                    window.updateCartBadge();
                }
                window.dispatchEvent(new CustomEvent('cartUpdated', { detail: data.cart }));

            } else {
                const errMsg = (data && data.error) ? data.error : "I couldn't process that command. Please try again.";
                addChatMessage('bot', errMsg);
                speakText(errMsg);
            }
        } catch (err) {
            console.error('[AI Assistant] Error calling backend:', err);
            const errMsg = "Connection issue with server. Please ensure python server is running.";
            addChatMessage('bot', errMsg);
            speakText(errMsg);
        }
    }

    function playAudioB64(b64, fallbackText) {
        stopAllSpeech();
        const player = getAudioElement();
        player.src = "data:audio/mp3;base64," + b64;
        isSpeaking = true;
        updateWidgetUIState('speaking');

        player.onended = function () {
            isSpeaking = false;
            updateWidgetUIState('idle');
        };

        player.onerror = function () {
            isSpeaking = false;
            updateWidgetUIState('idle');
            if (fallbackText) {
                speakText(fallbackText);
            }
        };

        player.play().catch(e => {
            console.warn('[AI Assistant] Audio playback fallback to synthesis:', e);
            isSpeaking = false;
            updateWidgetUIState('idle');
            if (fallbackText) {
                speakText(fallbackText);
            }
        });
    }

    async function refreshCartBadge() {
        try {
            const res = await fetch(getApiUrl('/api/cart'));
            const data = await res.json();
            const count = data.cart ? data.cart.length : 0;
            const badges = document.querySelectorAll('#cartCountBadge, .cart-badge');
            badges.forEach(b => b.innerText = count);
        } catch (e) {}
    }

    async function addToCartDirect(productId) {
        try {
            await fetch(getApiUrl('/api/cart'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId, qty: 1 })
            });
            refreshCartBadge();
            if (typeof window.loadCart === 'function') window.loadCart();
            if (typeof window.updateCartBadge === 'function') window.updateCartBadge();
            window.dispatchEvent(new CustomEvent('cartUpdated'));
            addChatMessage('bot', `Added item to your cart.`);
            speakText("Added item to your cart.");
        } catch (e) {
            console.error(e);
        }
    }

    // Public API
    window.FreshRootVoice = {
        activate: activateVoiceAssistant,
        close: closeVoiceWidget,
        toggleListening: toggleListening,
        speakText: speakText,
        handleCommand: handleUserVoiceInput,
        addToCartDirect: addToCartDirect,
        refreshCartBadge: refreshCartBadge,
        clearHistory: clearStoredHistory,
        stopAllSpeech: stopAllSpeech
    };

    // Auto-bind robot buttons on page load
    function initButtons() {
        const currentPath = (window.location.pathname || '').toLowerCase();
        if (currentPath.includes('login') || currentPath.includes('signup')) {
            return; // Completely disable voice assistant and popup on login/signup pages
        }

        injectWidgetDOM();
        refreshCartBadge();

        document.querySelectorAll('.floating-ai-btn').forEach(btn => {
            btn.removeAttribute('onclick');
            btn.onclick = function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (widgetOpen && isListening) {
                    stopListening();
                } else if (widgetOpen) {
                    startListening();
                } else {
                    activateVoiceAssistant();
                }
            };
        });

        document.querySelectorAll('button.ai-mic-nav-btn, .activate-ai-btn').forEach(el => {
            el.onclick = function (e) {
                e.preventDefault();
                activateVoiceAssistant();
            };
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initButtons);
    } else {
        initButtons();
    }
})();
