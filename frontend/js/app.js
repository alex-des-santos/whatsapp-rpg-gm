// =============================================================================
// WhatsApp RPG GM - JavaScript Principal
// =============================================================================

class WhatsAppRPGApp {
    constructor() {
        this.apiUrl = '/api';
        this.wsUrl = `ws://${window.location.host}/ws`;
        this.websocket = null;
        this.currentTab = 'dashboard';
        this.stats = {
            activeSessions: 0,
            totalPlayers: 0,
            diceRolls: 0,
            messagesToday: 0
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadInitialData();
        this.startPeriodicUpdates();

        console.log('WhatsApp RPG GM inicializado');
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Search functionality
        const searchInput = document.getElementById('character-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchCharacters(e.target.value);
            });
        }

        // Dice roller
        const diceInput = document.getElementById('dice-expression');
        if (diceInput) {
            diceInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.rollDice();
                }
            });
        }

        // Log level filter
        const logLevelSelect = document.getElementById('log-level');
        if (logLevelSelect) {
            logLevelSelect.addEventListener('change', (e) => {
                this.filterLogs(e.target.value);
            });
        }
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(this.wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket conectado');
                this.updateConnectionStatus('api', true);
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                console.log('WebSocket desconectado');
                this.updateConnectionStatus('api', false);

                // Reconectar após 5 segundos
                setTimeout(() => {
                    this.connectWebSocket();
                }, 5000);
            };

            this.websocket.onerror = (error) => {
                console.error('Erro no WebSocket:', error);
                this.updateConnectionStatus('api', false);
            };

        } catch (error) {
            console.error('Erro ao conectar WebSocket:', error);
            this.updateConnectionStatus('api', false);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'stats_update':
                this.updateStats(data.stats);
                break;
            case 'new_activity':
                this.addActivity(data.activity);
                break;
            case 'session_update':
                this.updateSession(data.session);
                break;
            case 'character_update':
                this.updateCharacter(data.character);
                break;
            case 'system_status':
                this.updateSystemStatus(data.status);
                break;
        }
    }

    async loadInitialData() {
        this.showLoading(true);

        try {
            // Carregar estatísticas
            await this.loadStats();

            // Carregar dados baseados na aba atual
            switch (this.currentTab) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'sessions':
                    await this.loadSessions();
                    break;
                case 'characters':
                    await this.loadCharacters();
                    break;
                case 'logs':
                    await this.loadLogs();
                    break;
            }

            // Verificar status do sistema
            await this.checkSystemStatus();

        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.showNotification('Erro ao carregar dados', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`);
            const stats = await response.json();
            this.updateStats(stats);
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    async loadDashboardData() {
        try {
            const [statsResponse, activityResponse] = await Promise.all([
                fetch(`${this.apiUrl}/stats`),
                fetch(`${this.apiUrl}/activity/recent`)
            ]);

            const stats = await statsResponse.json();
            const activities = await activityResponse.json();

            this.updateStats(stats);
            this.updateActivityList(activities);

        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        }
    }

    async loadSessions() {
        try {
            const response = await fetch(`${this.apiUrl}/sessions`);
            const sessions = await response.json();
            this.updateSessionsGrid(sessions);
        } catch (error) {
            console.error('Erro ao carregar sessões:', error);
        }
    }

    async loadCharacters() {
        try {
            const response = await fetch(`${this.apiUrl}/characters`);
            const characters = await response.json();
            this.updateCharactersGrid(characters);
        } catch (error) {
            console.error('Erro ao carregar personagens:', error);
        }
    }

    async loadLogs() {
        try {
            const response = await fetch(`${this.apiUrl}/logs`);
            const logs = await response.json();
            this.updateLogsContent(logs);
        } catch (error) {
            console.error('Erro ao carregar logs:', error);
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/health');
            const status = await response.json();
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            this.updateConnectionStatus('api', false);
        }
    }

    switchTab(tabName) {
        // Atualizar botões
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Atualizar conteúdo
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;

        // Carregar dados específicos da aba
        switch (tabName) {
            case 'sessions':
                this.loadSessions();
                break;
            case 'characters':
                this.loadCharacters();
                break;
            case 'logs':
                this.loadLogs();
                break;
        }
    }

    updateStats(stats) {
        this.stats = { ...this.stats, ...stats };

        // Atualizar elementos do DOM
        this.updateElement('active-sessions', stats.activeSessions || 0);
        this.updateElement('total-players', stats.totalPlayers || 0);
        this.updateElement('dice-rolls', stats.diceRolls || 0);
        this.updateElement('messages-today', stats.messagesToday || 0);
    }

    updateActivityList(activities) {
        const list = document.getElementById('activity-list');
        if (!list) return;

        list.innerHTML = '';

        activities.forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="activity-icon">
                    <i class="fas ${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            `;
            list.appendChild(item);
        });
    }

    updateSessionsGrid(sessions) {
        const grid = document.getElementById('sessions-grid');
        if (!grid) return;

        grid.innerHTML = '';

        sessions.forEach(session => {
            const card = document.createElement('div');
            card.className = 'session-card';
            card.innerHTML = `
                <div class="session-header">
                    <h3>${session.name || `Sessão ${session.id.substring(0, 8)}`}</h3>
                    <span class="session-status ${session.state}">${this.translateState(session.state)}</span>
                </div>
                <div class="session-info">
                    <p><i class="fas fa-users"></i> ${session.players.length} jogadores</p>
                    <p><i class="fas fa-clock"></i> ${this.formatTime(session.lastActivity)}</p>
                    <p><i class="fas fa-map-marker-alt"></i> ${session.currentScene}</p>
                </div>
                <div class="session-actions">
                    <button onclick="app.viewSession('${session.id}')" class="btn btn-primary btn-sm">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                    <button onclick="app.pauseSession('${session.id}')" class="btn btn-secondary btn-sm">
                        <i class="fas fa-pause"></i> Pausar
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    updateCharactersGrid(characters) {
        const grid = document.getElementById('characters-grid');
        if (!grid) return;

        grid.innerHTML = '';

        characters.forEach(character => {
            const card = document.createElement('div');
            card.className = 'character-card';
            card.innerHTML = `
                <div class="character-header">
                    <h3>${character.name}</h3>
                    <span class="character-level">Nível ${character.level}</span>
                </div>
                <div class="character-info">
                    <p><strong>${character.race} ${character.characterClass}</strong></p>
                    <div class="hp-bar">
                        <div class="hp-fill" style="width: ${(character.hpCurrent / character.hpMax) * 100}%"></div>
                        <span class="hp-text">${character.hpCurrent}/${character.hpMax} HP</span>
                    </div>
                    <p><i class="fas fa-shield-alt"></i> CA ${character.armorClass}</p>
                </div>
                <div class="character-actions">
                    <button onclick="app.viewCharacter('${character.playerId}', '${character.sessionId}')" class="btn btn-primary btn-sm">
                        <i class="fas fa-user"></i> Ver
                    </button>
                    <button onclick="app.editCharacter('${character.playerId}', '${character.sessionId}')" class="btn btn-secondary btn-sm">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    updateLogsContent(logs) {
        const content = document.getElementById('logs-content');
        if (!content) return;

        content.innerHTML = '';

        logs.forEach(log => {
            const entry = document.createElement('div');
            entry.className = `log-entry ${log.level}`;
            entry.innerHTML = `
                <span class="log-timestamp">[${this.formatTime(log.timestamp)}]</span>
                <span class="log-level">[${log.level.toUpperCase()}]</span>
                <span class="log-message">${log.message}</span>
            `;
            content.appendChild(entry);
        });

        // Scroll para o final
        content.scrollTop = content.scrollHeight;
    }

    updateSystemStatus(status) {
        // Atualizar indicadores de status
        this.updateConnectionStatus('api', status.services?.api === 'online');
        this.updateConnectionStatus('whatsapp', status.services?.evolution_api === 'online');
        this.updateConnectionStatus('db', status.services?.database === 'online');
    }

    updateConnectionStatus(service, isOnline) {
        const element = document.getElementById(`${service}-status`);
        if (!element) return;

        element.classList.remove('online', 'offline');
        element.classList.add(isOnline ? 'online' : 'offline');
    }

    async rollDice() {
        const expression = document.getElementById('dice-expression').value;
        const advantageType = document.getElementById('advantage-type').value;

        if (!expression) {
            this.showNotification('Digite uma expressão de dados', 'warning');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/dice/roll`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    expression: expression,
                    advantage: advantageType
                })
            });

            const result = await response.json();
            this.displayDiceResult(result);

        } catch (error) {
            console.error('Erro ao rolar dados:', error);
            this.showNotification('Erro ao rolar dados', 'error');
        }
    }

    quickRoll(expression) {
        document.getElementById('dice-expression').value = expression;
        this.rollDice();
    }

    displayDiceResult(result) {
        const resultDiv = document.getElementById('dice-result');
        if (!resultDiv) return;

        resultDiv.classList.add('has-result');
        resultDiv.innerHTML = `
            <div class="dice-result-content">
                <div class="result-expression">${result.expression}</div>
                <div class="result-total ${result.isCritical ? 'critical' : ''} ${result.isFumble ? 'fumble' : ''}">${result.total}</div>
                <div class="result-rolls">${result.rolls}</div>
                ${result.isCritical ? '<div class="result-special">CRÍTICO! 🎯</div>' : ''}
                ${result.isFumble ? '<div class="result-special">FALHA CRÍTICA! 💀</div>' : ''}
            </div>
        `;
    }

    searchCharacters(query) {
        const cards = document.querySelectorAll('.character-card');
        cards.forEach(card => {
            const name = card.querySelector('h3').textContent.toLowerCase();
            const visible = name.includes(query.toLowerCase());
            card.style.display = visible ? 'block' : 'none';
        });
    }

    filterLogs(level) {
        const entries = document.querySelectorAll('.log-entry');
        entries.forEach(entry => {
            const visible = level === 'all' || entry.classList.contains(level);
            entry.style.display = visible ? 'block' : 'none';
        });
    }

    // Utility methods
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleString('pt-BR');
    }

    getActivityIcon(type) {
        const icons = {
            'message': 'fa-comment',
            'dice_roll': 'fa-dice',
            'character_created': 'fa-user-plus',
            'session_started': 'fa-play',
            'session_ended': 'fa-stop',
            'combat_started': 'fa-sword',
            'error': 'fa-exclamation-triangle'
        };
        return icons[type] || 'fa-info-circle';
    }

    translateState(state) {
        const translations = {
            'active': 'Ativa',
            'inactive': 'Inativa',
            'paused': 'Pausada',
            'combat': 'Em Combate',
            'exploration': 'Explorando',
            'social': 'Interação Social',
            'waiting_gm': 'Aguardando GM'
        };
        return translations[state] || state;
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.toggle('show', show);
        }
    }

    showNotification(message, type = 'info') {
        // Criar notificação toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 100);

        // Remover após 3 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    startPeriodicUpdates() {
        // Atualizar estatísticas a cada 30 segundos
        setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadStats();
            }
        }, 30000);

        // Verificar status do sistema a cada minuto
        setInterval(() => {
            this.checkSystemStatus();
        }, 60000);
    }

    // Métodos para ações do GM
    async sendGlobalMessage() {
        const message = prompt('Digite o anúncio global:');
        if (!message) return;

        try {
            await fetch(`${this.apiUrl}/gm/announce`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            this.showNotification('Anúncio enviado com sucesso', 'success');
        } catch (error) {
            this.showNotification('Erro ao enviar anúncio', 'error');
        }
    }

    async pauseAllSessions() {
        if (!confirm('Tem certeza que deseja pausar todas as sessões?')) return;

        try {
            await fetch(`${this.apiUrl}/gm/pause-all`, { method: 'POST' });
            this.showNotification('Todas as sessões foram pausadas', 'success');
            this.loadSessions();
        } catch (error) {
            this.showNotification('Erro ao pausar sessões', 'error');
        }
    }

    async backupData() {
        try {
            const response = await fetch(`${this.apiUrl}/gm/backup`, { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showNotification('Backup criado com sucesso', 'success');
            } else {
                this.showNotification('Erro ao criar backup', 'error');
            }
        } catch (error) {
            this.showNotification('Erro ao criar backup', 'error');
        }
    }

    refreshLogs() {
        this.loadLogs();
    }

    viewLogs() {
        this.switchTab('logs');
    }
}

// Funções globais para eventos onclick
function sendGlobalMessage() { app.sendGlobalMessage(); }
function pauseAllSessions() { app.pauseAllSessions(); }
function backupData() { app.backupData(); }
function viewLogs() { app.viewLogs(); }
function rollDice() { app.rollDice(); }
function quickRoll(expr) { app.quickRoll(expr); }
function refreshLogs() { app.refreshLogs(); }

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WhatsAppRPGApp();
});

// Adicionar estilos para notificações toast
const toastStyles = `
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-primary);
    z-index: 1000;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    min-width: 300px;
    box-shadow: var(--shadow-lg);
}

.toast.show {
    transform: translateX(0);
}

.toast.toast-success {
    border-left: 4px solid var(--success-color);
}

.toast.toast-error {
    border-left: 4px solid var(--danger-color);
}

.toast.toast-warning {
    border-left: 4px solid var(--warning-color);
}

.toast.toast-info {
    border-left: 4px solid var(--accent-color);
}
`;

// Adicionar estilos ao head
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);
