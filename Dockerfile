FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Ajusta según tu estructura real
ENV DJANGO_SETTINGS_MODULE=lanube.settings  

# Directorio dentro del contenedor
WORKDIR /code  

# Copia e instala dependencias primero (caché eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .
