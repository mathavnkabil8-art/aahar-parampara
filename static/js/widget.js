(function () {
  'use strict';

  // Determine API base URL (either configured or inferred from script location)
  let scriptOrigin = window.location.origin;
  const API_BASE = window.HERITAGE_CHATBOT_API || scriptOrigin;

  // Prevent multiple injections
  if (document.getElementById('heritage-chatbot-widget-root')) {
    return;
  }

  // Inject Styles
  const styles = `
    #heritage-chatbot-widget-root {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #231f20;
      line-height: 1.5;
    }

    /* Floating Launcher Button */
    .h-widget-launcher {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 62px;
      height: 62px;
      border-radius: 50%;
      background: linear-gradient(135deg, #b84a39 0%, #8f2f21 100%);
      box-shadow: 0 6px 24px rgba(184, 74, 57, 0.38), 0 2px 6px rgba(0, 0, 0, 0.12);
      border: 2px solid #ffffff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 999998;
      transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
      outline: none;
    }

    .h-widget-launcher:hover {
      transform: scale(1.08) translateY(-2px);
      box-shadow: 0 10px 30px rgba(184, 74, 57, 0.48);
    }

    .h-widget-launcher:active {
      transform: scale(0.96);
    }

    .h-launcher-icon {
      width: 30px;
      height: 30px;
      fill: #ffffff;
      transition: transform 0.25s ease;
    }

    .h-launcher-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      background: #d97706;
      color: #ffffff;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 10px;
      border: 2px solid #ffffff;
      white-space: nowrap;
      pointer-events: none;
      box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }

    /* Chat Popup Window */
    .h-widget-window {
      position: fixed;
      bottom: 96px;
      right: 24px;
      width: 410px;
      max-width: calc(100vw - 36px);
      height: 630px;
      max-height: calc(100vh - 120px);
      background: #fdfbf7;
      border-radius: 20px;
      box-shadow: 0 12px 40px rgba(45, 25, 20, 0.22), 0 2px 10px rgba(0,0,0,0.06);
      border: 1px solid #ebdccb;
      display: flex;
      flex-direction: column;
      z-index: 999999;
      overflow: hidden;
      opacity: 0;
      visibility: hidden;
      transform: translateY(20px) scale(0.95);
      transform-origin: bottom right;
      transition: opacity 0.26s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.26s cubic-bezier(0.16, 1, 0.3, 1),
                  visibility 0.26s;
    }

    .h-widget-window.open {
      opacity: 1;
      visibility: visible;
      transform: translateY(0) scale(1);
    }

    .h-widget-window.maximized {
      width: 680px;
      height: calc(100vh - 60px);
      max-height: 850px;
      bottom: 24px;
    }

    /* Window Header */
    .h-window-header {
      background: linear-gradient(135deg, #b84a39 0%, #9c3b2c 100%);
      color: #ffffff;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(0,0,0,0.08);
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .h-header-title-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .h-header-avatar {
      width: 36px;
      height: 36px;
      background: rgba(255, 255, 255, 0.18);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      border: 1.5px solid rgba(255, 255, 255, 0.35);
    }

    .h-header-text h4 {
      margin: 0;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.3px;
      color: #ffffff;
    }

    .h-header-text p {
      margin: 2px 0 0 0;
      font-size: 11.5px;
      color: #f7dcd7;
    }

    .h-header-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .h-icon-btn {
      background: rgba(255, 255, 255, 0.14);
      border: none;
      color: #ffffff;
      width: 30px;
      height: 30px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s;
    }

    .h-icon-btn:hover {
      background: rgba(255, 255, 255, 0.28);
    }

    /* Disease Quick Select Strip */
    .h-disease-strip {
      background: #fbf5ed;
      padding: 10px 14px;
      border-bottom: 1px solid #eddccb;
    }

    .h-disease-title {
      font-size: 11px;
      font-weight: 700;
      color: #b84a39;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
      display: block;
    }

    .h-chips-container {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: thin;
    }

    .h-chips-container::-webkit-scrollbar {
      height: 3px;
    }
    .h-chips-container::-webkit-scrollbar-thumb {
      background: #dfcfbd;
      border-radius: 3px;
    }

    .h-chip {
      background: #ffffff;
      border: 1px solid #ebd8c5;
      border-radius: 14px;
      padding: 4px 10px;
      font-size: 11.5px;
      font-weight: 600;
      color: #3b3330;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.15s ease;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    .h-chip:hover {
      background: #b84a39;
      color: #ffffff;
      border-color: #b84a39;
    }

    /* Message Area */
    .h-messages-area {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background: #fdfbf7;
      scrollbar-width: thin;
    }

    .h-messages-area::-webkit-scrollbar {
      width: 5px;
    }
    .h-messages-area::-webkit-scrollbar-thumb {
      background: #dfcfbd;
      border-radius: 4px;
    }

    .h-msg {
      display: flex;
      gap: 8px;
      max-width: 88%;
      animation: hFadeIn 0.2s ease forwards;
    }

    @keyframes hFadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .h-msg-user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .h-msg-assistant {
      align-self: flex-start;
    }

    .h-msg-avatar {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      flex-shrink: 0;
    }

    .h-msg-assistant .h-msg-avatar {
      background: #f7ece0;
      border: 1px solid #e8d5c4;
    }

    .h-msg-user .h-msg-avatar {
      background: #b84a39;
      color: #ffffff;
      font-size: 11px;
      font-weight: bold;
    }

    .h-msg-bubble {
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 13.5px;
      line-height: 1.55;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      word-break: break-word;
    }

    .h-msg-assistant .h-msg-bubble {
      background: #ffffff;
      border: 1px solid #ebdccb;
      border-top-left-radius: 4px;
      color: #2b2523;
    }

    .h-msg-assistant .h-msg-bubble p {
      margin: 0 0 8px 0;
    }
    .h-msg-assistant .h-msg-bubble p:last-child {
      margin-bottom: 0;
    }

    .h-msg-assistant .h-msg-bubble strong {
      color: #b84a39;
    }

    .h-msg-user .h-msg-bubble {
      background: #b84a39;
      color: #ffffff;
      border-top-right-radius: 4px;
    }

    /* Dish Cards inside assistant bubble */
    .h-dish-card {
      margin-top: 10px;
      padding: 10px 12px;
      background: #fffdf9;
      border-left: 3px solid #b84a39;
      border-top: 1px solid #eedecf;
      border-right: 1px solid #eedecf;
      border-bottom: 1px solid #eedecf;
      border-radius: 6px;
    }

    .h-dish-title {
      font-weight: 700;
      color: #b84a39;
      font-size: 13.5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .h-dish-state-badge {
      font-size: 10.5px;
      background: #f8ebd9;
      color: #a14e08;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }

    .h-dish-desc {
      font-size: 12px;
      color: #59514e;
      margin: 4px 0 6px 0;
      line-height: 1.4;
    }

    .h-btn-recipe {
      background: none;
      border: none;
      color: #b84a39;
      font-size: 12px;
      font-weight: 700;
      padding: 0;
      cursor: pointer;
      text-decoration: underline;
    }

    /* Typing Dots */
    .h-typing-bubble {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 10px 14px;
      background: #ffffff;
      border: 1px solid #ebdccb;
      border-radius: 14px;
      width: fit-content;
    }

    .h-dot {
      width: 6px;
      height: 6px;
      background: #d97706;
      border-radius: 50%;
      animation: hWave 1.2s infinite ease-in-out;
    }
    .h-dot:nth-child(2) { animation-delay: 0.2s; }
    .h-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes hWave {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-4px); }
    }

    /* Chat Input */
    .h-input-bar {
      padding: 10px 14px 12px 14px;
      background: #ffffff;
      border-top: 1px solid #eddccb;
    }

    .h-input-wrapper {
      display: flex;
      align-items: center;
      background: #fdfbf7;
      border: 1.5px solid #ebdccb;
      border-radius: 12px;
      padding: 4px 6px 4px 12px;
      transition: border-color 0.15s;
    }

    .h-input-wrapper:focus-within {
      border-color: #b84a39;
      box-shadow: 0 0 0 2px rgba(184, 74, 57, 0.1);
    }

    .h-input-field {
      flex: 1;
      border: none;
      background: transparent;
      outline: none;
      font-size: 13.5px;
      color: #231f20;
    }

    .h-btn-send {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: none;
      background: #b84a39;
      color: #ffffff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s, transform 0.1s;
    }

    .h-btn-send:hover {
      background: #9c3b2c;
    }
    .h-btn-send:active {
      transform: scale(0.95);
    }

    /* In-Widget Recipe Modal Drawer */
    .h-recipe-modal {
      position: absolute;
      inset: 0;
      background: rgba(35, 31, 32, 0.6);
      backdrop-filter: blur(2px);
      z-index: 10;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }

    .h-recipe-modal.open {
      opacity: 1;
      pointer-events: auto;
    }

    .h-recipe-drawer {
      background: #ffffff;
      border-top-left-radius: 18px;
      border-top-right-radius: 18px;
      max-height: 85%;
      overflow-y: auto;
      padding: 16px;
      box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
      animation: hSlideUp 0.22s ease forwards;
    }

    @keyframes hSlideUp {
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    }

    .h-drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid #f0e2d5;
      padding-bottom: 8px;
    }

    .h-drawer-title {
      font-size: 16px;
      font-weight: 700;
      color: #b84a39;
      margin: 0;
    }

    .h-drawer-state {
      font-size: 11px;
      font-weight: 600;
      color: #8c4103;
      background: #fbf0e2;
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-block;
      margin-bottom: 4px;
    }

    .h-drawer-close {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: #7a706b;
      line-height: 1;
    }

    .h-drawer-section {
      margin-bottom: 12px;
    }

    .h-drawer-section h5 {
      font-size: 12px;
      text-transform: uppercase;
      color: #b84a39;
      margin: 0 0 4px 0;
      border-bottom: 1px dashed #ebd8c7;
      padding-bottom: 2px;
    }

    .h-drawer-section p, .h-drawer-section ul {
      font-size: 12.5px;
      color: #3b3330;
      margin: 0;
      line-height: 1.5;
    }

    .h-drawer-section ul {
      padding-left: 18px;
    }
  `;

  // Inject Stylesheet into head
  const styleEl = document.createElement('style');
  styleEl.id = 'heritage-chatbot-widget-styles';
  styleEl.innerHTML = styles;
  document.head.appendChild(styleEl);

  // Widget DOM Structure
  const widgetRoot = document.createElement('div');
  widgetRoot.id = 'heritage-chatbot-widget-root';
  widgetRoot.innerHTML = `
    <!-- Floating Launcher Button -->
    <button class="h-widget-launcher" id="hWidgetLauncher" aria-label="Open Food & Health Assistant">
      <svg class="h-launcher-icon" viewBox="0 0 24 24">
        <!-- Traditional Pot / Bowl with Healing Herb Spark -->
        <path d="M12 3c-4.97 0-9 2.01-9 4.5v.5c0 1.25 1.05 2.39 2.81 3.2C6.73 13.9 9.17 16 12 16s5.27-2.1 6.19-4.8c1.76-.81 2.81-1.95 2.81-3.2v-.5C21 5.01 16.97 3 12 3zm0 2c3.87 0 7 1.34 7 3s-3.13 3-7 3-7-1.34-7-3 3.13-3 7-3zm0 13c-3.31 0-6 1.34-6 3v1h12v-1c0-1.66-2.69-3-6-3z"/>
      </svg>
      <span class="h-launcher-badge">Food AI</span>
    </button>

    <!-- Chat Popup Window -->
    <div class="h-widget-window" id="hWidgetWindow">
      <!-- Window Header -->
      <div class="h-window-header">
        <div class="h-header-title-wrap">
          <div class="h-header-avatar">🍲</div>
          <div class="h-header-text">
            <h4>Traditional Food & Health AI</h4>
            <p>Forgotten state dishes & disease recommendations</p>
          </div>
        </div>
        <div class="h-header-actions">
          <button class="h-icon-btn" id="hMaximizeBtn" title="Expand / Shrink">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
          </button>
          <button class="h-icon-btn" id="hCloseBtn" title="Close">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
      </div>

      <!-- Disease Quick Select Strip -->
      <div class="h-disease-strip">
        <span class="h-disease-title">🌿 Quick Condition Recommendations:</span>
        <div class="h-chips-container" id="hChipsContainer">
          <button class="h-chip" data-q="I have diabetes, what traditional state foods can I eat?">🩸 Diabetes</button>
          <button class="h-chip" data-q="What traditional dishes help relieve joint pain and arthritis?">🦵 Joint Pain & Arthritis</button>
          <button class="h-chip" data-q="What traditional probiotic or fermented foods help gut health and digestion?">🌿 Gut Health & Digestion</button>
          <button class="h-chip" data-q="Which traditional state dishes support heart health and cholesterol?">❤️ Heart & Cholesterol</button>
          <button class="h-chip" data-q="What traditional recipes are rich in iron for anemia?">🩸 Anemia & Iron</button>
          <button class="h-chip" data-q="Which ancient dishes provide high calcium for bone strength?">🦴 Bone Density</button>
          <button class="h-chip" data-q="What traditional postpartum or PCOS healing foods exist in Indian heritage?">🌸 PCOS & Women's Health</button>
          <button class="h-chip" data-q="What traditional foods support kidney health and dissolve stones?">💧 Kidney Stones</button>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="h-messages-area" id="hMessagesArea">
        <div class="h-msg h-msg-assistant">
          <div class="h-msg-avatar">🏛️</div>
          <div class="h-msg-bubble">
            <p><strong>Namaste!</strong> Across every Indian state, ancestral foods were crafted as natural medicine (<em>"Aahar evam Aushadhi"</em>).</p>
            <p>Ask me about any <strong>disease or health condition</strong> (like <em>diabetes, joint pain, gut health, anemia, or cholesterol</em>), or ask for dishes from any <strong>Indian state</strong> to discover forgotten traditional recipes!</p>
          </div>
        </div>
      </div>

      <!-- Input Bar -->
      <div class="h-input-bar">
        <form id="hChatForm" style="margin:0;">
          <div class="h-input-wrapper">
            <input 
              type="text" 
              class="h-input-field" 
              id="hInputField" 
              placeholder="Ask about a disease or state..." 
              autocomplete="off"
              required
            />
            <button type="submit" class="h-btn-send" title="Send">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </form>
      </div>

      <!-- Recipe Drawer Modal Overlay -->
      <div class="h-recipe-modal" id="hRecipeModal">
        <div class="h-recipe-drawer">
          <div class="h-drawer-header">
            <div>
              <span class="h-drawer-state" id="hDrawerState">State</span>
              <h4 class="h-drawer-title" id="hDrawerTitle">Dish Title</h4>
            </div>
            <button class="h-drawer-close" id="hDrawerClose">&times;</button>
          </div>
          <div id="hDrawerBody"></div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(widgetRoot);

  // Widget Logic & State
  let isOpen = false;
  let isMaximized = false;
  let conversationHistory = [];

  const launcher = document.getElementById('hWidgetLauncher');
  const windowEl = document.getElementById('hWidgetWindow');
  const closeBtn = document.getElementById('hCloseBtn');
  const maximizeBtn = document.getElementById('hMaximizeBtn');
  const chatForm = document.getElementById('hChatForm');
  const inputField = document.getElementById('hInputField');
  const messagesArea = document.getElementById('hMessagesArea');
  const chipsContainer = document.getElementById('hChipsContainer');
  const recipeModal = document.getElementById('hRecipeModal');
  const drawerClose = document.getElementById('hDrawerClose');
  const drawerTitle = document.getElementById('hDrawerTitle');
  const drawerState = document.getElementById('hDrawerState');
  const drawerBody = document.getElementById('hDrawerBody');

  // Toggle open/close
  function toggleChat(openState) {
    isOpen = typeof openState === 'boolean' ? openState : !isOpen;
    if (isOpen) {
      windowEl.classList.add('open');
      setTimeout(() => inputField.focus(), 150);
    } else {
      windowEl.classList.remove('open');
      recipeModal.classList.remove('open');
    }
  }

  launcher.addEventListener('click', () => toggleChat());
  closeBtn.addEventListener('click', () => toggleChat(false));

  // Maximize / Restore
  maximizeBtn.addEventListener('click', () => {
    isMaximized = !isMaximized;
    if (isMaximized) {
      windowEl.classList.add('maximized');
    } else {
      windowEl.classList.remove('maximized');
    }
  });

  // Drawer close
  drawerClose.addEventListener('click', () => {
    recipeModal.classList.remove('open');
  });
  recipeModal.addEventListener('click', (e) => {
    if (e.target === recipeModal) recipeModal.classList.remove('open');
  });

  // Quick chips
  chipsContainer.addEventListener('click', (e) => {
    const chip = e.target.closest('.h-chip');
    if (chip && chip.dataset.q) {
      inputField.value = chip.dataset.q;
      sendMessage();
    }
  });

  // Message click for recipe drawer
  messagesArea.addEventListener('click', (e) => {
    const btn = e.target.closest('.h-btn-recipe');
    if (btn && btn.dataset.dishId !== undefined) {
      openRecipeDrawer(parseInt(btn.dataset.dishId, 10));
    }
  });

  // Form submit
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage();
  });

  // Send message
  async function sendMessage() {
    const text = inputField.value.trim();
    if (!text) return;

    inputField.value = '';
    appendMessage('user', text);

    const typingEl = showTyping();

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: conversationHistory
        })
      });

      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      removeTyping(typingEl);

      conversationHistory.push({ role: 'user', content: text });
      conversationHistory.push({ role: 'assistant', content: data.reply });

      appendMessage('assistant', data.reply, data.matched_foods);
    } catch (err) {
      console.error('Widget error:', err);
      removeTyping(typingEl);
      appendMessage('assistant', 'Sorry, I could not connect to the food knowledge base. Please try again.');
    }
  }

  function appendMessage(role, text, matchedFoods = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `h-msg h-msg-${role}`;

    let contentHtml = formatSimpleMarkdown(text);

    if (matchedFoods && matchedFoods.length > 0) {
      let cardsHtml = '';
      matchedFoods.forEach((f) => {
        cardsHtml += `
          <div class="h-dish-card">
            <div class="h-dish-title">
              <span>🍲 ${escapeHtml(f.title)}</span>
              <span class="h-dish-state-badge">${escapeHtml(f.state)}</span>
            </div>
            <p class="h-dish-desc">${escapeHtml(f.cultural_significance || f.heritage_value || '')}</p>
            <button class="h-btn-recipe" data-dish-id="${f.id}">View Traditional Recipe &rarr;</button>
          </div>
        `;
      });
      contentHtml += cardsHtml;
    }

    msgDiv.innerHTML = `
      <div class="h-msg-avatar">${role === 'user' ? 'You' : '🏛️'}</div>
      <div class="h-msg-bubble">${contentHtml}</div>
    `;

    messagesArea.appendChild(msgDiv);
    
    // Smooth scroll to the top of the AI's message so they don't have to scroll up
    if (role === 'assistant') {
      setTimeout(() => {
        messagesArea.scrollTo({
          top: msgDiv.offsetTop - 15,
          behavior: 'smooth'
        });
      }, 50);
    } else {
      messagesArea.scrollTop = messagesArea.scrollHeight;
    }
  }

  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'h-msg h-msg-assistant';
    typing.innerHTML = `
      <div class="h-msg-avatar">🏛️</div>
      <div class="h-typing-bubble">
        <div class="h-dot"></div>
        <div class="h-dot"></div>
        <div class="h-dot"></div>
      </div>
    `;
    messagesArea.appendChild(typing);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    return typing;
  }

  function removeTyping(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  async function openRecipeDrawer(dishId) {
    try {
      const res = await fetch(`${API_BASE}/api/dish/${dishId}`);
      const dish = await res.json();
      if (dish.error) return;

      drawerTitle.innerText = dish.title;
      drawerState.innerText = `${dish.state} • ${dish.region || ''}`;

      const content = dish.content || {};
      const ingredients = content.ingredients || [];
      const preparation = content.preparation || [];
      const cooking = content.cooking || [];

      let ingHtml = '<ul>';
      ingredients.forEach((i) => ingHtml += `<li>${escapeHtml(String(i))}</li>`);
      ingHtml += '</ul>';

      let prepHtml = '<ul>';
      preparation.forEach((p) => prepHtml += `<li>${escapeHtml(String(p))}</li>`);
      prepHtml += '</ul>';

      drawerBody.innerHTML = `
        <div class="h-drawer-section">
          <h5>🏛️ Cultural Heritage</h5>
          <p>${escapeHtml(dish.cultural_significance || '')}</p>
        </div>
        <div class="h-drawer-section">
          <h5>🧑‍🍳 Cooking Technique</h5>
          <p>${escapeHtml(dish.traditional_cooking || 'Traditional wood fire / earthen method')}</p>
        </div>
        <div class="h-drawer-section">
          <h5>🌿 Key Ingredients</h5>
          ${ingHtml}
        </div>
        ${preparation.length ? `
        <div class="h-drawer-section">
          <h5>🥣 Preparation</h5>
          ${prepHtml}
        </div>` : ''}
      `;

      recipeModal.classList.add('open');
    } catch (e) {
      console.error(e);
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function formatSimpleMarkdown(str) {
    if (!str) return '';
    let s = escapeHtml(str);
    
    // Custom replacements for bold/headers
    s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Headers
    s = s.replace(/^### (.*$)/gim, '<h4>$1</h4>');
    s = s.replace(/^## (.*$)/gim, '<h3>$1</h3>');
    
    // Bullet points
    s = s.replace(/^\• (.*$)/gim, '<li>$1</li>');
    s = s.replace(/^- (.*$)/gim, '<li>$1</li>');
    
    // Wrap lists
    s = s.replace(/(<li>.*?<\/li>)/gs, '<ul style="margin: 0.5rem 0; padding-left: 1.2rem;">$1</ul>');
    // Ensure multiple adjacent <ul> tags are merged (simple hack)
    s = s.replace(/<\/ul>\s*<ul[^>]*>/g, '');
    
    // Line breaks
    s = s.replace(/\n\n/g, '</p><p>');
    s = s.replace(/\n/g, '<br/>');
    
    return `<p>${s}</p>`;
  }

})();
