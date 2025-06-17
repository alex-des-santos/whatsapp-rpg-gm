@echo off
REM ==========================================
REM Script de início rápido para Windows 11
REM Alternativa simples ao PowerShell
REM ==========================================

title WhatsApp RPG GM - Windows 11

echo.
echo ============================================================
echo   WhatsApp RPG Game Master - Windows 11
echo ============================================================
echo.

REM Verificar se está no diretório correto
if not exist "app\main.py" (
    echo ERRO: Execute este script no diretório raiz do projeto!
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual não encontrado!
    echo Execute primeiro: setup-windows.ps1
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar arquivo .env
if not exist ".env" (
    echo AVISO: Arquivo .env não encontrado!
    if exist ".env.windows" (
        echo Copiando .env.windows para .env...
        copy ".env.windows" ".env"
    ) else (
        echo Copiando .env.example para .env...
        copy ".env.example" ".env"
    )
    echo IMPORTANTE: Edite o arquivo .env com suas configurações!
    pause
)

REM Aplicar migrações
echo Aplicando migrações do banco de dados...
alembic upgrade head

REM Iniciar aplicação
echo.
echo Iniciando WhatsApp RPG GM...
echo Acesse: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar a aplicacao
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

pause
