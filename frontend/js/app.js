// RPG GM Dashboard Application
class RPGDashboard {
    constructor() {
        this.data = {
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
            "metrics": {
                "messages_today": 127,
                "active_sessions": 3,
                "human_interventions": 2,
                "dice_rolls": 45,
                "avg_response_time": "1.2s"
            }
        };

        this.currentSection = 'dashboard';
        this.chatMessages = [];
        this.diceHistory = [];
        this.activityFeed = [];
        this.alerts = [];
        this.transcript = [];
        this.currentLLM = 'openai';
        this.isManualMode = false;

        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupDashboard();
        this.setupWhatsApp();
        this.setupGameState();
        this.setupAIModule();
        this.setupDiceSystem();
        this.setupHITL();
        this.setupSettings();
        this.startRealTimeUpdates();
    }

    setupNavigation() {
        const menuItems = document.querySelectorAll('.menu-item');
        const sections = document.querySelectorAll('.content-section');

        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetSection = item.dataset.section;
                
                // Update active menu item
                menuItems.forEach(mi => mi.classList.remove('active'));
                item.classList.add('active');
                
                // Update active section
                sections.forEach(section => section.classList.remove('active'));
                document.getElementById(targetSection).classList.add('active');
                
                this.currentSection = targetSection;
                this.onSectionChange(targetSection);
            });
        });
    }

    onSectionChange(section) {
        switch(section) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'game-state':
                this.updateGameState();
                break;
            case 'ai-module':
                this.updateAIModule();
                break;
        }
    }

    setupDashboard() {
        this.updateDashboard();
        this.generateActivityFeed();
    }

    updateDashboard() {
        // Update metrics
        document.getElementById('messages-today').textContent = this.data.metrics.messages_today;
        document.getElementById('active-sessions').textContent = this.data.metrics.active_sessions;
        document.getElementById('human-interventions').textContent = this.data.metrics.human_interventions;
        document.getElementById('dice-rolls').textContent = this.data.metrics.dice_rolls;

        // Update activity feed
        this.renderActivityFeed();
    }

    generateActivityFeed() {
        this.activityFeed = [
            {
                icon: '💬',
                text: 'Nova mensagem de Aria Nightwhisper: "Vou investigar os rastros"',
                time: '2 min atrás'
            },
            {
                icon: '🎲',
                text: 'Thorin rolou d20 para Investigação: 15 (Sucesso)',
                time: '5 min atrás'
            },
            {
                icon: '🤖',
                text: 'IA interveio na conversa sobre regras de combate',
                time: '8 min atrás'
            },
            {
                icon: '👤',
                text: 'Intervenção humana solicitada para decisão moral',
                time: '12 min atrás'
            },
            {
                icon: '⚔️',
                text: 'Combate iniciado: Grupo vs Bandidos',
                time: '15 min atrás'
            }
        ];
    }

    renderActivityFeed() {
        const feedContainer = document.getElementById('activity-feed');
        feedContainer.innerHTML = this.activityFeed.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">${activity.icon}</div>
                <div class="activity-content">
                    <div class="activity-text">${activity.text}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
    }

    setupWhatsApp() {
        this.chatMessages = [
            {
                type: 'ai',
                text: 'Olá! Sou seu GM AI Assistant. Como posso ajudar na sessão de hoje?',
                time: '14:30'
            },
            {
                type: 'user',
                text: 'Quero investigar a taverna em busca de pistas sobre os comerciantes desaparecidos.',
                time: '14:32'
            },
            {
                type: 'ai',
                text: 'Excelente! Role um teste de Investigação (d20 + modificador). Enquanto isso, você nota que o bartender Willem parece nervoso e evita contato visual.',
                time: '14:33'
            }
        ];

        this.renderChatMessages();
        this.setupChatControls();
    }

    renderChatMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = this.chatMessages.map(message => `
            <div class="message ${message.type}">
                <div class="message-bubble">
                    ${message.text}
                    <div class="message-time">${message.time}</div>
                </div>
            </div>
        `).join('');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    setupChatControls() {
        const sendButton = document.getElementById('send-message');
        const messageInput = document.getElementById('message-input');
        const actionButtons = document.querySelectorAll('.action-btn');

        sendButton.addEventListener('click', () => {
            const message = messageInput.value.trim();
            if (message) {
                this.sendMessage(message);
                messageInput.value = '';
            }
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendButton.click();
            }
        });

        actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    sendMessage(text) {
        const currentTime = new Date().toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        this.chatMessages.push({
            type: 'user',
            text: text,
            time: currentTime
        });

        // Simulate AI response
        setTimeout(() => {
            const responses = [
                'Interessante escolha! Role um d20 para ver o resultado.',
                'O GM considera sua ação... Um momento.',
                'Você sente que algo importante está para acontecer.',
                'A tensão no ar aumenta conforme você age.',
                'Role para Iniciativa, o combate está prestes a começar!'
            ];
            
            const response = responses[Math.floor(Math.random() * responses.length)];
            this.chatMessages.push({
                type: 'ai',
                text: response,
                time: new Date().toLocaleTimeString('pt-BR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                })
            });
            
            this.renderChatMessages();
        }, 1000);

        this.renderChatMessages();
        this.updateMetrics('messages');
    }

    handleQuickAction(action) {
        const actions = {
            attack: '⚔️ Eu ataco!',
            defend: '🛡️ Entro em posição defensiva.',
            investigate: '🔍 Quero investigar o ambiente.',
            talk: '💬 Tento conversar com os NPCs presentes.'
        };

        if (actions[action]) {
            this.sendMessage(actions[action]);
        }
    }

    setupGameState() {
        this.updateGameState();
    }

    updateGameState() {
        this.renderCharacters();
        this.renderWorldState();
        this.renderNPCs();
    }

    renderCharacters() {
        const container = document.getElementById('characters-container');
        container.innerHTML = this.data.characters.map(char => {
            const hpPercentage = (char.hp.current / char.hp.max) * 100;
            let hpClass = '';
            if (hpPercentage < 25) hpClass = 'critical';
            else if (hpPercentage < 75) hpClass = 'wounded';

            return `
                <div class="character-card">
                    <div class="character-header">
                        <div>
                            <div class="character-name">${char.name}</div>
                            <div class="character-class">${char.class} Nível ${char.level}</div>
                        </div>
                        <div class="status status--${char.status === 'healthy' ? 'success' : 'warning'}">
                            ${char.status === 'healthy' ? 'Saudável' : 'Ferido'}
                        </div>
                    </div>
                    
                    <div class="hp-bar">
                        <div class="hp-label">HP: ${char.hp.current}/${char.hp.max}</div>
                        <div class="hp-progress">
                            <div class="hp-fill ${hpClass}" style="width: ${hpPercentage}%"></div>
                        </div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.strength}</div>
                            <div class="stat-name">FOR</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.dexterity}</div>
                            <div class="stat-name">DES</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.constitution}</div>
                            <div class="stat-name">CON</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.intelligence}</div>
                            <div class="stat-name">INT</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.wisdom}</div>
                            <div class="stat-name">SAB</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${char.stats.charisma}</div>
                            <div class="stat-name">CAR</div>
                        </div>
                    </div>
                    
                    <div class="character-location">
                        <strong>Localização:</strong> ${char.location}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderWorldState() {
        const world = this.data.world_state;
        document.getElementById('current-scene').textContent = world.current_scene;
        document.getElementById('active-quest').textContent = world.active_quest;
        document.getElementById('location').textContent = world.environment.location;
        document.getElementById('environment').textContent = `${world.environment.time}, ${world.environment.weather}`;
    }

    renderNPCs() {
        const container = document.getElementById('npcs-container');
        container.innerHTML = this.data.world_state.npcs_present.map(npc => `
            <div class="npc-card">
                <div class="npc-name">${npc.name}</div>
                <div class="npc-disposition">Disposição: ${npc.disposition}</div>
                <div style="font-size: 12px; color: var(--color-text-secondary); margin-top: 4px;">
                    Sabe: ${npc.knows}
                </div>
            </div>
        `).join('');
    }

    setupAIModule() {
        this.setupLLMTabs();
        this.updateAIModule();
        this.setupPromptTester();
    }

    setupLLMTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.currentLLM = tab.dataset.llm;
                this.updateLLMConfig();
            });
        });
    }

    updateAIModule() {
        this.updateLLMConfig();
    }

    updateLLMConfig() {
        const config = this.data.llm_configs[this.currentLLM];
        const container = document.getElementById('llm-config');
        
        container.innerHTML = `
            <div class="config-item">
                <label class="config-label">Modelo: ${config.model}</label>
            </div>
            <div class="config-item">
                <label class="config-label">Caso de Uso:</label>
                <div style="font-size: 14px; color: var(--color-text-secondary);">
                    ${config.use_case}
                </div>
            </div>
            <div class="config-item">
                <label class="config-label">Temperatura: <span id="temp-value">${config.temperature}</span></label>
                <div class="slider-container">
                    <input type="range" class="slider" id="temperature-slider" 
                           min="0" max="1" step="0.1" value="${config.temperature}">
                </div>
            </div>
            <div class="config-item">
                <label class="config-label">Max Tokens: <span id="tokens-value">${config.max_tokens}</span></label>
                <div class="slider-container">
                    <input type="range" class="slider" id="tokens-slider" 
                           min="100" max="2000" step="50" value="${config.max_tokens}">
                </div>
            </div>
        `;

        // Setup sliders
        const tempSlider = document.getElementById('temperature-slider');
        const tokensSlider = document.getElementById('tokens-slider');
        
        tempSlider.addEventListener('input', (e) => {
            document.getElementById('temp-value').textContent = e.target.value;
            this.data.llm_configs[this.currentLLM].temperature = parseFloat(e.target.value);
        });
        
        tokensSlider.addEventListener('input', (e) => {
            document.getElementById('tokens-value').textContent = e.target.value;
            this.data.llm_configs[this.currentLLM].max_tokens = parseInt(e.target.value);
        });
    }

    setupPromptTester() {
        const testButton = document.getElementById('test-llm');
        testButton.addEventListener('click', () => {
            const prompt = document.getElementById('test-prompt').value.trim();
            if (prompt) {
                this.testLLM(prompt);
            }
        });
    }

    testLLM(prompt) {
        const resultContainer = document.getElementById('test-result');
        const resultContent = resultContainer.querySelector('.result-content');
        
        resultContainer.style.display = 'block';
        resultContent.textContent = 'Processando...';
        
        // Simulate LLM response
        setTimeout(() => {
            const responses = [
                'Como seu GM AI, interpreto que você deseja explorar mais profundamente a taverna. O ambiente está carregado de tensão...',
                'Baseado no contexto atual, sugiro que o personagem role um teste de Percepção para notar detalhes importantes.',
                'A narrativa aponta para um momento crucial. Os NPCs presentes parecem esconder algo importante.',
                'Analisando as regras de D&D 5e, esta situação requer cuidado especial com as mecânicas de investigação.'
            ];
            
            const response = responses[Math.floor(Math.random() * responses.length)];
            resultContent.textContent = `[${this.data.llm_configs[this.currentLLM].model}] ${response}`;
        }, 2000);
    }

    setupDiceSystem() {
        this.setupDiceButtons();
        this.setupCustomRoll();
        this.setupDCCalculator();
        this.renderDiceHistory();
    }

    setupDiceButtons() {
        const diceButtons = document.querySelectorAll('.dice-btn');
        diceButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const sides = parseInt(btn.dataset.sides);
                this.rollDice(1, sides);
            });
        });
    }

    setupCustomRoll() {
        const rollButton = document.getElementById('roll-custom');
        const customInput = document.getElementById('custom-dice');
        
        rollButton.addEventListener('click', () => {
            const diceString = customInput.value.trim();
            if (diceString) {
                this.parseAndRollCustom(diceString);
            }
        });
        
        customInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                rollButton.click();
            }
        });
    }

    setupDCCalculator() {
        const rollDCButton = document.getElementById('roll-dc');
        rollDCButton.addEventListener('click', () => {
            const dc = parseInt(document.getElementById('dc-value').value);
            if (dc && dc >= 1 && dc <= 30) {
                this.rollDC(dc);
            }
        });
    }

    rollDice(quantity, sides, modifier = 0) {
        const rolls = [];
        for (let i = 0; i < quantity; i++) {
            rolls.push(Math.floor(Math.random() * sides) + 1);
        }
        
        const total = rolls.reduce((sum, roll) => sum + roll, 0) + modifier;
        
        const result = {
            dice: `${quantity}d${sides}${modifier ? (modifier > 0 ? `+${modifier}` : `${modifier}`) : ''}`,
            rolls: rolls,
            modifier: modifier,
            total: total,
            timestamp: new Date().toLocaleTimeString('pt-BR')
        };
        
        this.diceHistory.unshift(result);
        if (this.diceHistory.length > 20) {
            this.diceHistory = this.diceHistory.slice(0, 20);
        }
        
        this.displayDiceResult(result);
        this.renderDiceHistory();
        this.updateMetrics('dice');
    }

    parseAndRollCustom(diceString) {
        // Simple parser for dice notation like "2d6+3" or "1d20-1"
        const match = diceString.match(/(\d+)d(\d+)([+-]\d+)?/i);
        if (match) {
            const quantity = parseInt(match[1]);
            const sides = parseInt(match[2]);
            const modifier = match[3] ? parseInt(match[3]) : 0;
            this.rollDice(quantity, sides, modifier);
        }
    }

    rollDC(dc) {
        const roll = Math.floor(Math.random() * 20) + 1;
        const success = roll >= dc;
        
        const result = {
            dice: `d20 vs DC ${dc}`,
            rolls: [roll],
            modifier: 0,
            total: roll,
            dc: dc,
            success: success,
            timestamp: new Date().toLocaleTimeString('pt-BR')
        };
        
        this.diceHistory.unshift(result);
        this.displayDiceResult(result);
        this.renderDiceHistory();
        this.updateMetrics('dice');
    }

    displayDiceResult(result) {
        const container = document.getElementById('current-result');
        const isSuccess = result.dc !== undefined;
        
        container.innerHTML = `
            <div class="result-display" style="color: ${isSuccess ? (result.success ? 'var(--color-success)' : 'var(--color-error)') : 'var(--color-primary)'}">
                ${result.total}
            </div>
            <div class="result-details">
                ${result.dice} = [${result.rolls.join(', ')}]${result.modifier ? ` ${result.modifier > 0 ? '+' : ''}${result.modifier}` : ''}
                ${isSuccess ? `<br><strong>${result.success ? 'SUCESSO' : 'FALHA'}</strong>` : ''}
            </div>
        `;
    }

    renderDiceHistory() {
        const container = document.getElementById('dice-history');
        container.innerHTML = this.diceHistory.map(roll => `
            <div class="history-item">
                <div>
                    <div class="history-roll">${roll.dice}</div>
                    <div style="font-size: 11px; color: var(--color-text-secondary);">${roll.timestamp}</div>
                </div>
                <div class="history-result" style="color: ${roll.dc !== undefined ? (roll.success ? 'var(--color-success)' : 'var(--color-error)') : 'var(--color-primary)'}">
                    ${roll.total}${roll.dc !== undefined ? (roll.success ? ' ✓' : ' ✗') : ''}
                </div>
            </div>
        `).join('');
    }

    setupHITL() {
        this.generateAlerts();
        this.setupModeToggle();
        this.setupTranscript();
        this.renderAlerts();
        this.renderTranscript();
    }

    generateAlerts() {
        this.alerts = [
            {
                type: 'warning',
                title: 'Decisão Moral Complexa',
                description: 'Jogador quer torturar NPC para obter informações. Intervenção recomendada.',
                timestamp: '2 min atrás'
            },
            {
                type: 'critical',
                title: 'Conflito de Regras',
                description: 'Disputa sobre mecânicas de combate. Arbitragem necessária.',
                timestamp: '5 min atrás'
            }
        ];
    }

    renderAlerts() {
        const container = document.getElementById('alerts-container');
        container.innerHTML = this.alerts.map(alert => `
            <div class="alert-item alert-${alert.type}">
                <div class="alert-icon">${alert.type === 'critical' ? '🚨' : '⚠️'}</div>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                    <div class="alert-actions">
                        <button class="btn btn--sm btn--primary">Intervir</button>
                        <button class="btn btn--sm btn--secondary">Ignorar</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    setupModeToggle() {
        const autoModeBtn = document.getElementById('auto-mode');
        const manualModeBtn = document.getElementById('manual-mode');
        const manualResponse = document.getElementById('manual-response');
        const sendManualBtn = document.getElementById('send-manual');

        autoModeBtn.addEventListener('click', () => {
            this.isManualMode = false;
            autoModeBtn.classList.add('active');
            autoModeBtn.classList.remove('btn--outline');
            autoModeBtn.classList.add('btn--secondary');
            manualModeBtn.classList.remove('active');
            manualModeBtn.classList.add('btn--outline');
            manualModeBtn.classList.remove('btn--secondary');
            manualResponse.style.display = 'none';
        });

        manualModeBtn.addEventListener('click', () => {
            this.isManualMode = true;
            manualModeBtn.classList.add('active');
            manualModeBtn.classList.remove('btn--outline');
            manualModeBtn.classList.add('btn--secondary');
            autoModeBtn.classList.remove('active');
            autoModeBtn.classList.add('btn--outline');
            autoModeBtn.classList.remove('btn--secondary');
            manualResponse.style.display = 'block';
        });

        sendManualBtn.addEventListener('click', () => {
            const response = document.getElementById('gm-response').value.trim();
            if (response) {
                this.addToTranscript('GM (Manual)', response);
                document.getElementById('gm-response').value = '';
                this.updateMetrics('interventions');
            }
        });
    }

    setupTranscript() {
        this.transcript = [
            {
                speaker: 'Aria',
                text: 'Quero investigar os comerciantes desaparecidos.',
                timestamp: '14:25'
            },
            {
                speaker: 'GM AI',
                text: 'Role um teste de Investigação.',
                timestamp: '14:26'
            },
            {
                speaker: 'Thorin',
                text: 'Vou ajudar na investigação.',
                timestamp: '14:27'
            },
            {
                speaker: 'GM (Manual)',
                text: 'Vocês notam pegadas suspeitas perto da entrada.',
                timestamp: '14:28'
            }
        ];
    }

    addToTranscript(speaker, text) {
        this.transcript.push({
            speaker: speaker,
            text: text,
            timestamp: new Date().toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            })
        });
        this.renderTranscript();
    }

    renderTranscript() {
        const container = document.getElementById('transcript-container');
        container.innerHTML = this.transcript.map(entry => `
            <div class="transcript-entry">
                <div class="transcript-timestamp">${entry.timestamp}</div>
                <div>
                    <span class="transcript-speaker">${entry.speaker}:</span>
                    <span class="transcript-text">${entry.text}</span>
                </div>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    }

    setupSettings() {
        // Settings are mostly display-only for this demo
        console.log('Settings initialized');
    }

    updateMetrics(type) {
        switch(type) {
            case 'messages':
                this.data.metrics.messages_today++;
                document.getElementById('messages-today').textContent = this.data.metrics.messages_today;
                break;
            case 'dice':
                this.data.metrics.dice_rolls++;
                document.getElementById('dice-rolls').textContent = this.data.metrics.dice_rolls;
                break;
            case 'interventions':
                this.data.metrics.human_interventions++;
                document.getElementById('human-interventions').textContent = this.data.metrics.human_interventions;
                break;
        }
    }

    startRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            if (Math.random() < 0.1) { // 10% chance every 5 seconds
                this.simulateActivity();
            }
        }, 5000);
    }

    simulateActivity() {
        const activities = [
            {
                icon: '💬',
                text: 'Nova mensagem recebida no sistema',
                time: 'agora'
            },
            {
                icon: '🎲',
                text: 'Rolagem automática de dados detectada',
                time: 'agora'
            },
            {
                icon: '🤖',
                text: 'IA processou nova consulta',
                time: 'agora'
            }
        ];

        const newActivity = activities[Math.floor(Math.random() * activities.length)];
        this.activityFeed.unshift(newActivity);
        
        if (this.activityFeed.length > 10) {
            this.activityFeed = this.activityFeed.slice(0, 10);
        }

        if (this.currentSection === 'dashboard') {
            this.renderActivityFeed();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.rpgDashboard = new RPGDashboard();
});