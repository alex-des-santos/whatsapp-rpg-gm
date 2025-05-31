// RPG AI Master Application Logic

// Application data
const appData = {
  "characters": [
    {
      "name": "Aria Nightwhisper",
      "class": "Ranger",
      "level": 5,
      "hp": {"current": 45, "max": 45},
      "stats": {
        "strength": 14,
        "dexterity": 18,
        "constitution": 16,
        "intelligence": 12,
        "wisdom": 15,
        "charisma": 10
      },
      "location": "Floresta Sombria",
      "inventory": ["Arco Élfico", "Aljava com 30 flechas", "Armadura de Couro", "Kit de Sobrevivência"],
      "status": "healthy"
    },
    {
      "name": "Thorin Barbaferro", 
      "class": "Fighter",
      "level": 4,
      "hp": {"current": 38, "max": 42},
      "stats": {
        "strength": 17,
        "dexterity": 13,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 14
      },
      "location": "Taverna do Dragão",
      "inventory": ["Machado de Batalha", "Escudo", "Armadura de Placas", "Poção de Cura"],
      "status": "slightly_wounded"
    }
  ],
  "world_state": {
    "current_scene": "Investigação na Taverna",
    "active_quest": "O Mistério dos Comerciantes Desaparecidos",
    "npcs_present": [
      {"name": "Bartender Willem", "disposition": "friendly", "knows": "informações sobre comerciantes"},
      {"name": "Comerciante Suspeito", "disposition": "nervous", "knows": "pistas sobre o desaparecimento"}
    ],
    "environment": {
      "location": "Taverna do Dragão Dourado",
      "time": "Final da tarde",
      "weather": "Chuva leve",
      "mood": "tenso, suspeitas no ar"
    }
  },
  "llm_configs": {
    "openai": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1000,
      "use_case": "Narrativa principal e diálogos complexos"
    },
    "anthropic": {
      "model": "claude-3-sonnet", 
      "temperature": 0.6,
      "max_tokens": 1000,
      "use_case": "Análise de regras e decisões éticas"
    },
    "google": {
      "model": "gemini-pro",
      "temperature": 0.8,
      "max_tokens": 800,
      "use_case": "Geração criativa e descrições ambientais"
    },
    "local": {
      "model": "llama3:8b",
      "temperature": 0.5,
      "max_tokens": 600,
      "use_case": "Backup offline e operações simples"
    }
  },
  "system_status": {
    "whatsapp_api": "online",
    "llm_primary": "online", 
    "llm_fallback": "online",
    "knowledge_base": "online",
    "dice_system": "online"
  },
  "recent_messages": [
    {
      "type": "player",
      "content": "Quero investigar o comerciante suspeito",
      "timestamp": "14:32",
      "character": "Aria"
    },
    {
      "type": "gm",
      "content": "Você se aproxima discretamente do comerciante. Role um teste de Percepção (Sabedoria).",
      "timestamp": "14:32"
    },
    {
      "type": "dice",
      "content": "🎲 Rolagem: d20 + 2 = 17 (Sucesso!)",
      "timestamp": "14:33"
    },
    {
      "type": "gm", 
      "content": "Você nota que ele está nervoso, suas mãos tremem ligeiramente enquanto bebe. Há lama fresca em suas botas, apesar da chuva ter começado há pouco.",
      "timestamp": "14:33"
    }
  ],
  "metrics": {
    "messages_today": 127,
    "active_sessions": 3,
    "human_interventions": 2,
    "dice_rolls": 45,
    "avg_response_time": "1.2s"
  }
};

// Application state
let currentSection = 'dashboard';
let chatMessages = [...appData.recent_messages];
let rollHistory = [];
let isHumanControl = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeApp();
});

function initializeApp() {
    console.log('Initializing app...');
    setupNavigation();
    populateDashboard();
    populateGameState();
    populateWhatsAppChat();
    setupEventListeners();
    setupAIModule();
    setupDiceSystem();
    setupHITLSystem();
    initializeDemoData();
    
    // Show dashboard by default
    showSection('dashboard');
    console.log('App initialized successfully');
}

// Navigation System
function setupNavigation() {
    console.log('Setting up navigation...');
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.content-section');

    console.log(`Found ${navLinks.length} nav links and ${sections.length} sections`);

    navLinks.forEach((link, index) => {
        console.log(`Setting up nav link ${index}:`, link.getAttribute('data-section'));
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            console.log(`Navigating to section: ${targetSection}`);
            showSection(targetSection);
        });
    });
}

function showSection(sectionId) {
    console.log(`Showing section: ${sectionId}`);
    
    // Update active nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionId) {
            link.classList.add('active');
        }
    });
    
    // Update active section
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionId) {
            section.classList.add('active');
            console.log(`Section ${sectionId} is now active`);
        }
    });
    
    currentSection = sectionId;
}

// Dashboard Population
function populateDashboard() {
    console.log('Populating dashboard...');
    // Activities feed
    const activityFeed = document.getElementById('activity-feed');
    if (activityFeed) {
        const activities = [
            { time: '14:35', action: 'Aria realizou teste de Percepção', type: 'dice' },
            { time: '14:33', action: 'Nova mensagem de jogador recebida', type: 'message' },
            { time: '14:30', action: 'IA processou comando de investigação', type: 'ai' },
            { time: '14:28', action: 'Sistema HITL detectou situação complexa', type: 'alert' },
            { time: '14:25', action: 'Thorin entrou na taverna', type: 'game' }
        ];

        activityFeed.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-time">${activity.time}</div>
                <div>${activity.action}</div>
            </div>
        `).join('');
        console.log('Activity feed populated');
    }
}

// Game State Population
function populateGameState() {
    console.log('Populating game state...');
    
    // Characters list
    const charactersList = document.getElementById('characters-list');
    if (charactersList) {
        charactersList.innerHTML = appData.characters.map(char => {
            const hpPercentage = (char.hp.current / char.hp.max) * 100;
            const statusClass = char.status === 'healthy' ? 'success' : 'warning';
            
            return `
                <div class="character-card">
                    <div class="character-header">
                        <div>
                            <div class="character-name">${char.name}</div>
                            <div class="character-class">${char.class} Nível ${char.level}</div>
                        </div>
                        <span class="status status--${statusClass}">${char.status === 'healthy' ? 'Saudável' : 'Ferido'}</span>
                    </div>
                    <div class="hp-info">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>HP: ${char.hp.current}/${char.hp.max}</span>
                            <span>${Math.round(hpPercentage)}%</span>
                        </div>
                        <div class="hp-bar">
                            <div class="hp-fill" style="width: ${hpPercentage}%"></div>
                        </div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.strength}</div>
                            <div class="stat-label">FOR</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.dexterity}</div>
                            <div class="stat-label">DES</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.constitution}</div>
                            <div class="stat-label">CON</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.intelligence}</div>
                            <div class="stat-label">INT</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.wisdom}</div>
                            <div class="stat-label">SAB</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.charisma}</div>
                            <div class="stat-label">CAR</div>
                        </div>
                    </div>
                    <div style="margin-top: 12px;">
                        <strong>Localização:</strong> ${char.location}
                    </div>
                    <div style="margin-top: 8px;">
                        <strong>Inventário:</strong> ${char.inventory.join(', ')}
                    </div>
                </div>
            `;
        }).join('');
        console.log('Characters list populated');
    }

    // World state
    const elements = [
        { id: 'current-scene', value: appData.world_state.current_scene },
        { id: 'active-quest', value: appData.world_state.active_quest },
        { id: 'current-location', value: appData.world_state.environment.location },
        { id: 'game-time', value: appData.world_state.environment.time }
    ];
    
    elements.forEach(({ id, value }) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });

    // NPCs list
    const npcsList = document.getElementById('npcs-list');
    if (npcsList) {
        npcsList.innerHTML = appData.world_state.npcs_present.map(npc => `
            <div class="npc-item">
                <div>
                    <div class="npc-name">${npc.name}</div>
                    <div style="font-size: 12px; color: var(--color-text-secondary);">${npc.knows}</div>
                </div>
                <span class="npc-disposition ${npc.disposition}">${npc.disposition === 'friendly' ? 'Amigável' : 'Nervoso'}</span>
            </div>
        `).join('');
        console.log('NPCs list populated');
    }
}

// WhatsApp Chat Population
function populateWhatsAppChat() {
    console.log('Populating WhatsApp chat...');
    updateChatMessages();
}

function updateChatMessages() {
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
        chatContainer.innerHTML = chatMessages.map(msg => {
            const messageClass = msg.type;
            return `
                <div class="message ${messageClass}">
                    <div class="message-bubble">
                        ${msg.content}
                        ${msg.character ? `<div style="font-size: 11px; opacity: 0.7; margin-top: 4px;">${msg.character}</div>` : ''}
                    </div>
                    <div class="message-time">${msg.timestamp}</div>
                </div>
            `;
        }).join('');
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
        console.log('Chat messages updated');
    }
}

// Event Listeners Setup
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // WhatsApp message sending
    const sendButton = document.getElementById('send-message');
    const messageInput = document.getElementById('message-input');
    
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
        console.log('Send button listener added');
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        console.log('Message input listener added');
    }

    // Action buttons
    const actionButtons = document.querySelectorAll('[data-action]');
    console.log(`Found ${actionButtons.length} action buttons`);
    
    actionButtons.forEach((button, index) => {
        button.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            console.log(`Action button clicked: ${action}`);
            handleActionButton(action);
        });
    });
}

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message) {
        console.log(`Sending message: ${message}`);
        
        // Add player message
        chatMessages.push({
            type: 'player',
            content: message,
            timestamp: getCurrentTime(),
            character: 'Jogador'
        });
        
        messageInput.value = '';
        updateChatMessages();
        
        // Simulate AI response
        setTimeout(() => {
            simulateAIResponse(message);
        }, 1000);
    }
}

function handleActionButton(action) {
    const actions = {
        'attack': 'Quero atacar!',
        'investigate': 'Quero investigar o ambiente',
        'talk': 'Quero conversar com os NPCs',
        'magic': 'Quero lançar uma magia'
    };
    
    const actionMessage = actions[action];
    console.log(`Handling action: ${action} -> ${actionMessage}`);
    
    chatMessages.push({
        type: 'player',
        content: actionMessage,
        timestamp: getCurrentTime(),
        character: 'Jogador'
    });
    
    updateChatMessages();
    
    setTimeout(() => {
        simulateAIResponse(actionMessage);
    }, 1000);
}

function simulateAIResponse(playerMessage) {
    const responses = {
        'atacar': 'Role um teste de Ataque (d20 + modificador de Força ou Destreza)',
        'investigar': 'Role um teste de Investigação ou Percepção (d20 + modificador de Inteligência ou Sabedoria)',
        'conversar': 'Escolha com qual NPC você gostaria de conversar. Role um teste de Persuasão se necessário.',
        'magia': 'Qual magia você gostaria de lançar? Lembre-se de verificar seus slots de magia disponíveis.',
        'default': 'Interessante ação! Role um d20 para ver como procede.'
    };
    
    let response = responses.default;
    for (let key in responses) {
        if (playerMessage.toLowerCase().includes(key)) {
            response = responses[key];
            break;
        }
    }
    
    chatMessages.push({
        type: 'gm',
        content: response,
        timestamp: getCurrentTime()
    });
    
    updateChatMessages();
    console.log(`AI response sent: ${response}`);
}

function getCurrentTime() {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
}

// AI Module Setup
function setupAIModule() {
    console.log('Setting up AI module...');
    
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const testPromptBtn = document.getElementById('test-prompt-btn');
    
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', (e) => {
            temperatureValue.textContent = e.target.value;
        });
        console.log('Temperature slider listener added');
    }
    
    if (testPromptBtn) {
        testPromptBtn.addEventListener('click', testPrompt);
        console.log('Test prompt button listener added');
    }
}

function testPrompt() {
    const promptText = document.getElementById('test-prompt').value;
    const technique = document.getElementById('prompt-technique').value;
    const provider = document.getElementById('llm-provider').value;
    const resultDiv = document.getElementById('prompt-result');
    
    if (!promptText.trim()) {
        resultDiv.innerHTML = '<div style="color: var(--color-rpg-red);">Por favor, insira um prompt para testar.</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div class="loading">Processando prompt...</div>';
    
    setTimeout(() => {
        const mockResponses = {
            'chain-of-thought': `Resposta usando Chain of Thought:

1. Primeiro, vou analisar a situação...
2. Considerando as regras de D&D...
3. Baseado no contexto atual...
4. Portanto, minha resposta é:

${generateMockAIResponse(promptText, provider)}`,
            'tree-of-thought': `Resposta usando Tree of Thought:

Opção A: ${generateMockAIResponse(promptText, provider)}
Opção B: Abordagem alternativa considerando...
Opção C: Terceira possibilidade seria...

Melhor opção: A, porque...`,
            'standard': generateMockAIResponse(promptText, provider)
        };
        
        resultDiv.innerHTML = `<div style="white-space: pre-line; line-height: 1.6;">${mockResponses[technique]}</div>`;
    }, 2000);
}

function generateMockAIResponse(prompt, provider) {
    const responses = {
        'openai': 'Como GPT-4, eu processaria isso considerando o contexto narrativo completo e as nuances dos personagens...',
        'anthropic': 'Analisando eticamente esta situação, considero importante manter o equilíbrio do jogo...',
        'google': 'Gerando uma resposta criativa e imersiva para esta situação única...',
        'local': 'Processando localmente com recursos limitados, mas mantendo a coerência...'
    };
    
    return responses[provider] || 'Resposta processada com sucesso!';
}

// Dice System Setup
function setupDiceSystem() {
    console.log('Setting up dice system...');
    
    // Dice buttons
    const diceButtons = document.querySelectorAll('.dice-btn');
    console.log(`Found ${diceButtons.length} dice buttons`);
    
    diceButtons.forEach((button, index) => {
        button.addEventListener('click', (e) => {
            const diceType = e.target.getAttribute('data-dice');
            console.log(`Rolling ${diceType}`);
            rollDice(diceType);
        });
    });
    
    // Custom roll
    const rollCustomBtn = document.getElementById('roll-custom');
    if (rollCustomBtn) {
        rollCustomBtn.addEventListener('click', rollCustomDice);
        console.log('Custom roll button listener added');
    }
    
    // Test system
    const performTestBtn = document.getElementById('perform-test');
    if (performTestBtn) {
        performTestBtn.addEventListener('click', performTest);
        console.log('Perform test button listener added');
    }
    
    updateRollHistory();
}

function rollDice(diceType) {
    const sides = parseInt(diceType.substring(1));
    const result = Math.floor(Math.random() * sides) + 1;
    
    console.log(`Rolled ${diceType}: ${result}`);
    
    const rollData = {
        dice: diceType,
        result: result,
        timestamp: getCurrentTime()
    };
    
    rollHistory.unshift(rollData);
    displayRollResult(`🎲 ${diceType}: ${result}`);
    updateRollHistory();
    
    // Add to chat if in WhatsApp section
    if (currentSection === 'whatsapp') {
        chatMessages.push({
            type: 'dice',
            content: `🎲 Rolagem: ${diceType} = ${result}`,
            timestamp: getCurrentTime()
        });
        updateChatMessages();
    }
}

function rollCustomDice() {
    const customInput = document.getElementById('custom-dice').value.trim();
    if (!customInput) return;
    
    try {
        const result = parseAndRollDice(customInput);
        const rollData = {
            dice: customInput,
            result: result.total,
            details: result.details,
            timestamp: getCurrentTime()
        };
        
        rollHistory.unshift(rollData);
        displayRollResult(`🎲 ${customInput}: ${result.total} ${result.details ? `(${result.details})` : ''}`);
        updateRollHistory();
        
        document.getElementById('custom-dice').value = '';
    } catch (error) {
        displayRollResult('❌ Formato inválido. Use: 2d6+3, d20, etc.');
    }
}

function parseAndRollDice(expression) {
    // Simple dice parser for expressions like "2d6+3", "d20", "3d8-2"
    const regex = /^(\d*)d(\d+)([+-]\d+)?$/i;
    const match = expression.match(regex);
    
    if (!match) throw new Error('Invalid format');
    
    const numDice = parseInt(match[1] || '1');
    const sides = parseInt(match[2]);
    const modifier = parseInt(match[3] || '0');
    
    const rolls = [];
    for (let i = 0; i < numDice; i++) {
        rolls.push(Math.floor(Math.random() * sides) + 1);
    }
    
    const sum = rolls.reduce((a, b) => a + b, 0);
    const total = sum + modifier;
    
    return {
        total: total,
        details: `${rolls.join('+')}${modifier !== 0 ? (modifier > 0 ? '+' + modifier : modifier) : ''}`
    };
}

function displayRollResult(text) {
    const resultDiv = document.getElementById('roll-result');
    if (resultDiv) {
        resultDiv.textContent = text;
        resultDiv.classList.add('glow');
        setTimeout(() => resultDiv.classList.remove('glow'), 2000);
    }
}

function updateRollHistory() {
    const historyDiv = document.getElementById('roll-history');
    if (historyDiv) {
        historyDiv.innerHTML = rollHistory.slice(0, 10).map(roll => `
            <div class="roll-item">
                <span>${roll.dice}</span>
                <span>${roll.result}</span>
                <span style="font-size: 11px; color: var(--color-text-secondary);">${roll.timestamp}</span>
            </div>
        `).join('');
    }
}

function performTest() {
    const testType = document.getElementById('test-type').value;
    const modifier = parseInt(document.getElementById('modifier').value);
    const difficulty = parseInt(document.getElementById('difficulty').value);
    
    const roll = Math.floor(Math.random() * 20) + 1;
    const total = roll + modifier;
    const success = total >= difficulty;
    
    console.log(`Performing test: ${testType}, roll: ${roll}, modifier: ${modifier}, total: ${total}, DC: ${difficulty}, success: ${success}`);
    
    const testData = {
        type: testType,
        roll: roll,
        modifier: modifier,
        total: total,
        difficulty: difficulty,
        success: success,
        timestamp: getCurrentTime()
    };
    
    rollHistory.unshift({
        dice: `${testType} (d20+${modifier})`,
        result: total,
        timestamp: getCurrentTime()
    });
    
    const resultDiv = document.getElementById('test-result');
    if (resultDiv) {
        resultDiv.className = `test-result ${success ? 'success' : 'failure'}`;
        resultDiv.innerHTML = `
            <div>🎲 d20: ${roll} + ${modifier} = ${total}</div>
            <div>CD: ${difficulty}</div>
            <div style="font-size: 18px; margin-top: 8px;">
                ${success ? '✅ SUCESSO!' : '❌ FALHA!'}
            </div>
        `;
    }
    
    updateRollHistory();
    
    // Add to chat if appropriate
    if (currentSection === 'whatsapp') {
        chatMessages.push({
            type: 'dice',
            content: `🎲 Teste de ${testType}: d20(${roll}) + ${modifier} = ${total} vs CD ${difficulty} - ${success ? 'SUCESSO!' : 'FALHA!'}`,
            timestamp: getCurrentTime()
        });
        updateChatMessages();
    }
}

// HITL System Setup
function setupHITLSystem() {
    console.log('Setting up HITL system...');
    
    const takeControlBtn = document.getElementById('take-control');
    const returnAIBtn = document.getElementById('return-ai');
    
    if (takeControlBtn) {
        takeControlBtn.addEventListener('click', toggleHumanControl);
        console.log('Take control button listener added');
    }
    
    if (returnAIBtn) {
        returnAIBtn.addEventListener('click', toggleHumanControl);
        console.log('Return AI button listener added');
    }
    
    populateSessionTranscript();
}

function toggleHumanControl() {
    isHumanControl = !isHumanControl;
    
    const controlStatus = document.querySelector('.control-status .status');
    const takeControlBtn = document.getElementById('take-control');
    const manualResponse = document.getElementById('manual-response');
    
    if (controlStatus && takeControlBtn && manualResponse) {
        if (isHumanControl) {
            controlStatus.textContent = 'GM Humano Ativo';
            controlStatus.className = 'status status--warning';
            takeControlBtn.style.display = 'none';
            manualResponse.style.display = 'block';
        } else {
            controlStatus.textContent = 'IA Ativa';
            controlStatus.className = 'status status--info';
            takeControlBtn.style.display = 'inline-block';
            manualResponse.style.display = 'none';
        }
        console.log(`Human control toggled: ${isHumanControl}`);
    }
}

function populateSessionTranscript() {
    const transcript = document.getElementById('session-transcript');
    if (transcript) {
        const transcriptData = [
            '[14:25] SYSTEM: Sessão iniciada',
            '[14:26] PLAYER(Thorin): Entro na taverna',
            '[14:26] GM_AI: Você entra na taverna...',
            '[14:30] PLAYER(Aria): Quero investigar',
            '[14:30] GM_AI: Role um teste de Percepção',
            '[14:32] DICE: d20+2 = 17',
            '[14:32] GM_AI: Você nota que...',
            '[14:35] SYSTEM: Situação complexa detectada'
        ];
        
        transcript.innerHTML = transcriptData.map(line => `<div>${line}</div>`).join('');
        console.log('Session transcript populated');
    }
}

// Initialize demo data
function initializeDemoData() {
    console.log('Initializing demo data...');
    // Add some initial roll history
    rollHistory = [
        { dice: 'd20', result: 17, timestamp: '14:33' },
        { dice: '2d6+3', result: 11, timestamp: '14:30' },
        { dice: 'd12', result: 8, timestamp: '14:28' }
    ];
    console.log('Demo data initialized');
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: var(--color-rpg-primary);
        color: white;
        border-radius: 8px;
        z-index: 1000;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}