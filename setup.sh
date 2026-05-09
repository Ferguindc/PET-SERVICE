#!/bin/bash

# Script de instalación rápida del Pet Service

echo "🚀 Iniciando instalación del Pet Service..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Copiar archivo .env
if [ ! -f .env ]; then
    echo "⚙️  Copiando .env.example a .env..."
    cp .env.example .env
    echo "⚠️  Recuerda actualizar .env con tu configuración"
fi

# Crear migrations
echo "🗂️  Creando migraciones..."
python manage.py makemigrations

# Ejecutar migrations
echo "🔄 Aplicando migraciones..."
python manage.py migrate

# Crear superusuario
echo "👤 Creando superusuario..."
python manage.py createsuperuser

# Crear directorio de media
mkdir -p media staticfiles

echo ""
echo "✨ ¡Instalación completada!"
echo ""
echo "Para iniciar el servidor:"
echo "  source venv/bin/activate  # En Windows: venv\Scripts\activate"
echo "  python manage.py runserver"
echo ""
echo "Para acceder:"
echo "  Admin: http://localhost:8000/admin/"
echo "  API: http://localhost:8000/api/v1/pets/"
echo "  Docs: http://localhost:8000/api/docs/"
