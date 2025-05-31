# Sistema de GM de RPG com IA para WhatsApp
**Protótipo de Interface e Demonstração**

Uma demonstração web interativa que simula um sistema de Mestre de Jogo (GM) de RPG utilizando Inteligência Artificial para WhatsApp. Este projeto apresenta um dashboard visual que demonstra como seria a interface de controle para um sistema completo de GM automatizado.

## 🎯 O que é este projeto

Este é um **protótipo de interface** que demonstra visualmente como funcionaria um sistema completo de GM de RPG com IA. A aplicação simula:

- Interface de chat do WhatsApp
- Dashboard de controle do GM
- Sistema de rolagem de dados
- Gestão de estado do jogo
- Configurações de IA
- Sistema Human-in-the-Loop (HITL)

**⚠️ Importante**: Esta é uma demonstração frontend. Não inclui integração real com WhatsApp, APIs de IA funcionais ou backend persistente.

## 📁 Estrutura do Projeto

```
whatsapp-rpg-gm/
├── index.html              # Interface web principal
├── app.js                  # Lógica JavaScript da aplicação
├── style.css               # Estilos CSS
├── script.py              # Gerador de dados de exemplo
├── rpg_ai_system_data.json # Dados estruturados de exemplo
├── app_1.js               # Versão alternativa do app.js
└── rpg-ai-gm-whatsapp.zip # Arquivos comprimidos
```

## 🚀 Como Executar

### Pré-requisitos

- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Python 3.6+ (apenas para regenerar dados de exemplo)

### Execução Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/alex-des-santos/whatsapp-rpg-gm.git
   cd whatsapp-rpg-gm
   ```

2. **Abra a aplicação**
   - Opção 1: Abra `index.html` diretamente no navegador
   - Opção 2: Use um servidor local simples:
   ```bash
   # Com Python
   python -m http.server 8000
   # Ou com Node.js
   npx serve
   ```

3. **Acesse no navegador**
   ```
   http://localhost:8000
   ```

### Regerar Dados de Exemplo (Opcional)

Se quiser modificar os dados de exemplo:

```bash
python script.py
```

Isso irá recriar o arquivo `rpg_ai_system_data.json` com novos dados estruturados.

## 🎮 Funcionalidades da Demonstração

### Dashboard Principal
- Visão geral de métricas do sistema
- Status dos serviços simulados
- Feed de atividades recentes
- Indicadores de performance

### Simulador WhatsApp
- Interface de chat simulada
- Botões de ação interativos (Atacar, Investigar, Conversar, Magia)
- Envio de mensagens de texto
- Simulação de respostas da IA

### Gestão de Estado do Jogo
- Visualização de personagens com estatísticas D&D
- Estado atual do mundo do jogo
- Lista de NPCs presentes na cena
- Informações de localização e tempo

### Módulo de IA
- Configuração simulada de diferentes provedores LLM
- Ajuste de parâmetros (temperatura, tokens)
- Teste de prompts com diferentes técnicas
- Simulação de respostas de diferentes modelos

### Sistema de Dados
- Rolagem de dados D&D (d4, d6, d8, d10, d12, d20)
- Rolagem customizada (ex: 2d6+3)
- Calculadora de testes de habilidade
- Histórico de rolagens

### Sistema HITL
- Simulação de alertas para intervenção humana
- Controle manual para GM humano
- Transcrição de sessão
- Interface para respostas manuais

## 🔧 Personalização

### Modificar Personagens
Edite o array `characters` em `app.js` para alterar os personagens de exemplo:

```javascript
const appData = {
  "characters": [
    {
      "name": "Seu Personagem",
      "class": "Classe",
      "level": 1,
      "hp": {"current": 10, "max": 10},
      // ... outras propriedades
    }
  ]
  // ...
};
```

### Adicionar Novos Dados
Execute `script.py` para gerar uma nova estrutura de dados JSON baseada nos templates definidos no código Python.

### Modificar Interface
- `index.html`: Estrutura HTML e layout das seções
- `style.css`: Estilos visuais e temas
- `app.js`: Lógica JavaScript e interações

## 🛠️ Funcionalidades Simuladas

Esta demonstração simula as seguintes funcionalidades que estariam presentes em um sistema completo:

- **Integração WhatsApp**: Via Evolution API (simulado)
- **Múltiplos LLMs**: OpenAI, Anthropic, Google, Ollama (simulado)
- **Sistema RAG**: LlamaIndex para conhecimento D&D (simulado)
- **Persistência**: Banco de dados PostgreSQL/Redis (simulado)
- **Notificações**: Sistema HITL para GM humano (simulado)

## 📋 Dependências Reais vs Simuladas

### Dependências Atuais (apenas para desenvolvimento)
```json
{
  "frontend": "HTML, CSS, JavaScript (vanilla)",
  "geração_dados": "Python 3.6+",
  "servidor_local": "http.server ou similar"
}
```

### Dependências que seriam necessárias em um sistema real
```json
{
  "backend": "FastAPI, Flask ou Node.js",
  "whatsapp": "Evolution API ou WhatsApp Business API",
  "ia": "OpenAI, Anthropic, Google APIs",
  "dados": "PostgreSQL, Redis",
  "rpg": "dicepy, bibliotecas de D&D",
  "interface": "Streamlit, Gradio ou React"
}
```

## 🎯 Próximos Passos

Para transformar esta demonstração em um sistema funcional, seria necessário implementar:

1. **Backend completo** com APIs REST
2. **Integração real com Evolution API** para WhatsApp
3. **Conexões com provedores de LLM** (OpenAI, Anthropic, etc.)
4. **Banco de dados** para persistência de estado
5. **Sistema de autenticação** e segurança
6. **Deploy em servidor** com domínio próprio

## 📖 Como Usar a Demonstração

1. **Navegue pelas seções** usando o menu lateral
2. **Teste o chat** na seção "Simulador WhatsApp"
3. **Role dados** na seção "Sistema de Dados"
4. **Experimente configurações** na seção "Módulo de IA"
5. **Explore o estado do jogo** na seção "Gestão de Estado"
6. **Simule intervenções** na seção "Sistema HITL"

## 🤝 Contribuição

Este projeto serve como base para discussão e desenvolvimento de um sistema real. Contribuições para melhorar a demonstração são bem-vindas:

1. Melhorias na interface visual
2. Novas funcionalidades simuladas
3. Dados de exemplo mais ricos
4. Melhor responsividade mobile

## 📄 Licença

Este projeto de demonstração está disponível sob licença MIT.

## ⚠️ Disclaimers

- **Não é um sistema funcional**: Esta é apenas uma demonstração visual
- **Dados simulados**: Todas as respostas e dados são fictícios
- **Sem conexões reais**: Não há integração com APIs externas
- **Apenas frontend**: Não inclui backend ou persistência real

---

Desenvolvido como conceito e demonstração para a comunidade de RPG ⚔️
