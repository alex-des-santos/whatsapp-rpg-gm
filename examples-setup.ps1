# ==========================================
# Exemplos de Uso do Setup Interativo
# Diferentes cenários de configuração
# ==========================================

Write-Host "=== Exemplos de Uso do WhatsApp RPG GM Setup ===" -ForegroundColor Green
Write-Host ""

Write-Host "1. Setup Completo Interativo (Recomendado):" -ForegroundColor Yellow
Write-Host "   .\setup-windows.ps1" -ForegroundColor Cyan
Write-Host "   • Detecta instalações existentes"
Write-Host "   • Pergunta sobre configurações"
Write-Host "   • Testa conectividade"
Write-Host "   • Configura tudo automaticamente"
Write-Host ""

Write-Host "2. Setup Automático (sem interação):" -ForegroundColor Yellow
Write-Host "   .\setup-windows.ps1 -AutoMode" -ForegroundColor Cyan
Write-Host "   • Usa valores padrão quando possível"
Write-Host "   • Mais rápido para desenvolvimento"
Write-Host ""

Write-Host "3. Teste de Conectividade:" -ForegroundColor Yellow
Write-Host "   .\test-connectivity.ps1 -Interactive" -ForegroundColor Cyan
Write-Host "   • Pergunta hosts para testar"
Write-Host "   • Verifica se serviços estão acessíveis"
Write-Host ""

Write-Host "4. Teste com Hosts Específicos:" -ForegroundColor Yellow
Write-Host "   .\test-connectivity.ps1 -PostgreSQLHost '192.168.1.100' -RedisHost '192.168.1.101'" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Iniciar Aplicação:" -ForegroundColor Yellow
Write-Host "   .\start-windows.ps1" -ForegroundColor Cyan
Write-Host "   • Verifica serviços automaticamente"
Write-Host "   • Inicia aplicação FastAPI"
Write-Host ""

Write-Host "=== Cenários Comuns ===" -ForegroundColor Green
Write-Host ""

Write-Host "• Servidor PostgreSQL e Redis locais:" -ForegroundColor Yellow
Write-Host "  1. .\setup-windows.ps1"
Write-Host "  2. Escolher 'local' para PostgreSQL e Redis"
Write-Host "  3. .\start-windows.ps1"
Write-Host ""

Write-Host "• Servidor PostgreSQL remoto, Redis local:" -ForegroundColor Yellow
Write-Host "  1. .\setup-windows.ps1"
Write-Host "  2. Escolher 'remoto' para PostgreSQL"
Write-Host "  3. Informar IP/host do PostgreSQL"
Write-Host "  4. Escolher 'local' para Redis"
Write-Host "  5. .\start-windows.ps1"
Write-Host ""

Write-Host "• Ambos os serviços remotos:" -ForegroundColor Yellow
Write-Host "  1. .\setup-windows.ps1"
Write-Host "  2. Escolher 'remoto' para ambos"
Write-Host "  3. Informar IPs/hosts dos serviços"
Write-Host "  4. .\start-windows.ps1"
Write-Host ""

Write-Host "• Docker/Containers:" -ForegroundColor Yellow
Write-Host "  1. .\setup-windows.ps1"
Write-Host "  2. Escolher 'docker' para os serviços"
Write-Host "  3. Informar portas mapeadas"
Write-Host "  4. .\start-windows.ps1"
Write-Host ""

Write-Host "• Serviços na nuvem:" -ForegroundColor Yellow
Write-Host "  1. .\setup-windows.ps1"
Write-Host "  2. Escolher 'nuvem' para os serviços"
Write-Host "  3. Informar endpoints da nuvem"
Write-Host "  4. .\start-windows.ps1"
Write-Host ""

Write-Host "=== Dicas Importantes ===" -ForegroundColor Green
Write-Host ""
Write-Host "• Execute como Administrador para instalações automáticas" -ForegroundColor Yellow
Write-Host "• Configure as chaves de API no arquivo .env após o setup" -ForegroundColor Yellow
Write-Host "• Use .\test-connectivity.ps1 para diagnosticar problemas" -ForegroundColor Yellow
Write-Host "• O arquivo .env é gerado automaticamente com suas configurações" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Estrutura Resultante ===" -ForegroundColor Green
Write-Host ""
Write-Host "Após o setup você terá:" -ForegroundColor Yellow
Write-Host "• .env - Configurações específicas da sua infraestrutura"
Write-Host "• venv/ - Ambiente virtual Python"
Write-Host "• data/, logs/, sessions/ - Diretórios de dados"
Write-Host "• Banco PostgreSQL configurado e criado"
Write-Host "• Redis configurado e testado"
Write-Host ""

$choice = Read-Host "Executar setup agora? (S/N)"
if ($choice.ToUpper() -eq "S") {
    .\setup-windows.ps1
} else {
    Write-Host "Execute .\setup-windows.ps1 quando estiver pronto!" -ForegroundColor Green
}
