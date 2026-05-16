#!/bin/bash
set -euo pipefail

echo "=== EC2 Setup: Fraud Detection System ==="

# System deps
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx

# Start Docker
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu

# Clone project (replace with your repo URL)
# git clone https://github.com/your-org/fraud-detection.git /home/ubuntu/fraud-detection
cd /home/ubuntu/fraud-detection

# Build and start
sudo docker compose -f infra/docker-compose.yml up -d --build

# Nginx reverse proxy
sudo tee /etc/nginx/sites-available/fraud-detection > /dev/null <<'NGINX'
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /home/ubuntu/fraud-detection/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/fraud-detection /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "=== Setup complete ==="
echo "API: http://$(curl -s http://checkip.amazonaws.com)/api/v1/health"
echo "UI: http://$(curl -s http://checkip.amazonaws.com)"
