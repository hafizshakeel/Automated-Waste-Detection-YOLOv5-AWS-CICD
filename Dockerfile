FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y \
    awscli \
    ffmpeg \
    libsm6 \
    libxext6 \
    unzip \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Start Streamlit with specific port and binding to all interfaces
CMD ["streamlit", "run", "app_ui.py", "--server.port", "8501", "--server.address", "0.0.0.0"]