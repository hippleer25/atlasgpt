FROM python:3.11-slim
WORKDIR /app
# Copiar os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .
# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt
# Copiar o restante do projeto
COPY . .
# Expor a porta que a aplicação Flask vai utilizar
EXPOSE 5000
# Comando para iniciar a aplicação
CMD ["python", "main.py"]
