# EC2 배포 가이드

## 1. EC2 인스턴스 설정

### 인스턴스 생성
- **AMI**: Ubuntu 22.04 LTS
- **인스턴스 타입**: t3.micro (무료 티어) 또는 t3.small
- **키 페어**: SSH 접속용 키 페어 생성

### 보안 그룹 설정
```bash
# 인바운드 규칙 추가
SSH (22) - 본인 IP만 허용
HTTP (80) - 0.0.0.0/0
HTTPS (443) - 0.0.0.0/0
Custom TCP (8000) - 0.0.0.0/0
```

## 2. 서버 초기 설정

```bash
# SSH 접속
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-venv git nginx

# 프로젝트 디렉토리로 이동
cd /home/ubuntu
git clone https://github.com/your-username/deep-brochures.git
cd deep-brochures

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 3. 환경 변수 설정

```bash
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key-here
FIRECRAWL_API_KEY=fc-6c6fb40857a14880b0145507e929b14a
EOF
```

## 4. Systemd 서비스 설정

```bash
# 서비스 파일 생성
sudo tee /etc/systemd/system/media-kit-api.service > /dev/null << EOF
[Unit]
Description=Media Kit Search API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/deep-brochures
Environment=PATH=/home/ubuntu/deep-brochures/venv/bin
ExecStart=/home/ubuntu/deep-brochures/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable media-kit-api
sudo systemctl start media-kit-api

# 서비스 상태 확인
sudo systemctl status media-kit-api
```

## 5. Nginx 리버스 프록시 설정

```bash
# Nginx 설정 파일 생성
sudo tee /etc/nginx/sites-available/media-kit-api > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com your-ec2-public-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 설정 활성화
sudo ln -s /etc/nginx/sites-available/media-kit-api /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 6. 방화벽 설정 (UFW)

```bash
# UFW 방화벽 설정
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

## 7. SSL 인증서 설정 (Let's Encrypt - 선택사항)

도메인이 있는 경우:

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 줄 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 8. 배포 완료 확인

```bash
# 서비스 상태 확인
sudo systemctl status media-kit-api
sudo systemctl status nginx

# API 테스트
curl -X POST "http://your-ec2-public-ip/search" \
  -H "Content-Type: application/json" \
  -d '{"media_name": "중앙일보"}'
```

## 9. 로그 확인

```bash
# 애플리케이션 로그
sudo journalctl -u media-kit-api -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 10. 업데이트 방법

```bash
cd /home/ubuntu/deep-brochures
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart media-kit-api
```

## 접근 URL

- **API 문서**: http://your-ec2-public-ip/docs
- **API 엔드포인트**: http://your-ec2-public-ip/search
- **헬스 체크**: http://your-ec2-public-ip/health 