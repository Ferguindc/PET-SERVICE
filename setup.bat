@echo off
REM Script de instalación rápida del Pet Service (Windows)

echo.
echo Iniciando instalacion del Pet Service...
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python no esta instalado
    exit /b 1
)

echo [+] Python encontrado:
python --version

REM Crear entorno virtual
echo.
echo [+] Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo [+] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo [+] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copiar archivo .env
if not exist .env (
    echo [+] Copiando .env.example a .env...
    copy .env.example .env
    echo [!] Recuerda actualizar .env con tu configuracion
)

REM Crear migrations
echo [+] Creando migraciones...
python manage.py makemigrations

REM Ejecutar migrations
echo [+] Aplicando migraciones...
python manage.py migrate

REM Crear directorio de media
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

echo.
echo [^!] Instalacion completada!
echo.
echo Para iniciar el servidor:
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
echo Para acceder:
echo   Admin: http://localhost:8000/admin/
echo   API: http://localhost:8000/api/v1/pets/
echo   Docs: http://localhost:8000/api/docs/
echo.
pause
