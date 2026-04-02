# Deploy on EC2 with Docker + Nginx

## 1) Prepare EC2 (Ubuntu)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker
```

## 2) Clone project

```bash
git clone <your_repo_url>
cd bagProject
```

## 3) Configure env

```bash
cp .env.example .env
```

Edit `.env`:
- set strong `SECRET_KEY`
- set your domain in `ALLOWED_HOSTS`
- for HTTPS add domain to `CSRF_TRUSTED_ORIGINS` (example: `https://sumki_by_zhama.com`)
- set Postgres values (`DB_*`)
- if using Cloudinary, set `CLOUDINARY_URL`

## 4) Run project

```bash
docker compose up -d --build
```

## 5) Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## 6) Open site

- App: `http://<EC2_PUBLIC_IP>`
- Admin: `http://<EC2_PUBLIC_IP>/admin/`

## 7) Useful commands

```bash
docker compose logs -f
docker compose restart
docker compose down
```
