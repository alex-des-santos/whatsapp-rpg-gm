# WhatsApp RPG GM Agent

Este projeto implementa um agente de Mestre de Jogo (GM) para RPG via WhatsApp, utilizando Inteligência Artificial e integrando funcionalidades essenciais de RPG.

## Pré-requisitos

- Python 3.10+
- Conta na [Evolution API](https://evolution-api.com/)
- Chave de API da OpenAI
- Docker (opcional)

## Estrutura de Arquivos

```
whatsapp-rpg-gm/
├── core/
│   ├── game_state/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   └── models.py
│   ├── ai_module/
│   │   ├── __init__.py
│   │   ├── llm_integration.py
│   │   └── prompt_templates.py
│   ├── dice_system/
│   │   ├── __init__.py
│   │   └── roller.py
│   └── hitl/
│       ├── __init__.py
│       └── intervention.py
├── integration/
│   ├── __init__.py
│   └── whatsapp_evolution.py
├── gui/
│   ├── __init__.py
│   └── control_panel.py
├── storage/
│   └── game_state.json
├── rpg_data/
│   ├── dnd_5e_rules.md
│   └── world_lore.md
├── config.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

## Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/whatsapp-rpg-gm.git
cd whatsapp-rpg-gm
```

2. Crie e configure o arquivo `.env`:
```env
EVOLUTION_API_URL="http://localhost:3000"
EVOLUTION_API_KEY="sua_chave_api_evolution"
OPENAI_API_KEY="sua_chave_api_openai"
GM_PHONE="5511999999999@c.us"
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Adicione dados de RPG na pasta `rpg_data`:
- `dnd_5e_rules.md`: Regras do sistema D&D 5e
- `world_lore.md`: Lore do seu mundo de RPG

## Execução

### Opção 1: Execução direta
```bash
python main.py
```

### Opção 2: Usando Docker
```bash
docker build -t whatsapp-rpg-gm .
docker run -p 8501:8501 -d whatsapp-rpg-gm
```

O painel de controle do GM estará disponível em:
`http://localhost:8501`

## Funcionalidades

### Comandos via WhatsApp
- **Rolagem de dados**: `/rolar 2d6+3`
- **Ataque**: `/atacar orc com espada`
- **Interação**: `Falar com o ferreiro`
- **Movimentação**: `Ir para a caverna`

### Painel do GM
Acesse `http://localhost:8501` para:
- Visualizar estado do jogo
- Intervir manualmente
- Ajustar parâmetros da IA
- Ver histórico de eventos

### Fluxo do Sistema
1. Recebe mensagem via WhatsApp
2. Processa ação do jogador
3. Gera resposta com IA
4. Atualiza estado do jogo
5. Notifica GM se necessário
6. Envia resposta ao jogador

## Personalização

### Adaptar para outros sistemas de RPG
1. Modifique `core/game_state/models.py`
2. Atualize regras em `rpg_data/`
3. Ajuste templates de prompt em `core/ai_module/prompt_templates.py`

### Adicionar novas funcionalidades
1. Crie novos módulos em `core/`
2. Registre comandos em `main.py`
3. Atualize interface do painel GM

## Contribuição
Contribuições são bem-vindas! Siga os passos:
1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato
Para suporte ou dúvidas:
- Email: suporte@exemplo.com
- Discord: https://discord.gg/seu-servidor

---

Este README fornece todas as informações necessárias para configurar e executar o WhatsApp RPG GM Agent. O sistema está pronto para uso imediato e pode ser facilmente personalizado para diferentes sistemas de RPG.