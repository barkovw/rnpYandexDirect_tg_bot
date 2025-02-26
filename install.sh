#!/bin/bash

echo "🤖 Установка бота..."

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Установка Python..."
    sudo apt install -y python3 python3-pip
fi

# Установка зависимостей
python3 -m pip install -r requirements.txt

# Копирование примера конфига
cp .env.example .env.local

echo "⚙️ Пожалуйста, настройте параметры в файле .env.local"
echo "После настройки запустите: python3 main.py"

# Создание systemd сервиса для автозапуска
echo "Создание сервиса автозапуска..."
sudo tee /etc/systemd/system/rnpYandexDirect-bot.service << EOF
[Unit]
Description=RNP Yandex Direct Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 $PWD/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable rnpYandexDirect-bot 