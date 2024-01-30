FROM python:3.10
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    python3-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
# Копирование необходимых файлов
COPY alchemy.py /opt/
COPY config.py /opt/
COPY create_bot.py /opt/
COPY handlers.py /opt/
COPY keyboards.py /opt/
COPY main.py /opt/
COPY coffee-10.db /opt/
COPY requirements.txt /opt/

# Установка рабочей директории
WORKDIR /opt/

# Установка зависимостей
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
# RUN pip3 install aiogram==2.25.1
# ENV FLASK_APP=/opt/main.py
CMD python3 main.py
# ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# docker buildx build --platform linux/amd64 -t plhsh/bot:pm_amd64 --load .
