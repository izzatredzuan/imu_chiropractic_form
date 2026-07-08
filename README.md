# Chiropractic Form System

A Django web application for managing Chiropractic Forms.

This document explains how to deploy the application on a **clean testing server from scratch** using Docker.

The setup assumes:

* A new server with no Docker installed.
* The application will run inside Docker containers.
* Test users need access from external machines.
* This environment is for testing purposes only.

---

# 1. Server Requirements

Recommended server:

* Ubuntu 22.04 / Ubuntu 24.04

Minimum requirements:

* 2 CPU cores
* 4GB RAM
* 20GB storage

Required:

* Internet access
* SSH access
* Firewall access to application port

---

# 2. Install Required Server Packages

Update the server:

```bash
sudo apt update
sudo apt upgrade -y
```

Install required tools:

```bash
sudo apt install -y git curl nano
```

Verify Git installation:

```bash
git --version
```

---

# 3. Install Docker

Install Docker Engine:

```bash
curl -fsSL https://get.docker.com -o install-docker.sh

sudo sh install-docker.sh
```

Enable Docker service:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Install Docker Compose plugin:

```bash
sudo apt install docker-compose-plugin -y
```

Verify Docker installation:

```bash
docker --version

docker compose version
```

Optional: allow the current user to run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
```

Log out and log in again after running this command.

---

# 4. Clone the Repository

This project is hosted on Gitea. The recommended method is to use SSH authentication.

## Configure Git Identity

Before cloning, configure your Git username and email. These details will be attached to your Git commits.

Configure Git username:

```bash
git config --global user.name "Your Name"
```

Example:

```bash
git config --global user.name "John Doe"
```

Configure Git email:

Use the same email associated with your Gitea account.

```bash
git config --global user.email "your_email@example.com"
```

Example:

```bash
git config --global user.email "john.doe@imu.edu.my"
```

Verify Git configuration:

```bash
git config --global --list
```

Example output:

```text
user.name=John Doe
user.email=john.doe@imu.edu.my
```

---

## Configure SSH Access for Gitea

SSH allows the server to securely access the repository.

### 1. Check for an existing SSH key

```bash
ls ~/.ssh
```

If you already have:

```text
id_ed25519
id_ed25519.pub
```

you can skip to **Step 3**.

---

### 2. Generate an SSH key

Generate a new Ed25519 SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

When prompted:

```text
Enter file in which to save the key (/home/username/.ssh/id_ed25519):
```

Press **Enter** to use the default location.

For the passphrase:

* Press **Enter** to leave it empty, or
* Enter a passphrase for additional security.

---

### 3. Start SSH agent

```bash
eval "$(ssh-agent -s)"
```

---

### 4. Add SSH key

```bash
ssh-add ~/.ssh/id_ed25519
```

---

### 5. Copy public key

Display your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output.

---

### 6. Add SSH key to Gitea

1. Log in to Gitea.
2. Open your profile settings.
3. Navigate to:

```text
Settings → SSH / GPG Keys
```

4. Click:

```text
Add Key
```

5. Enter a title (example: `Test Server`).
6. Paste the public key.
7. Save.

---

### 7. Test SSH connection

Run:

```bash
ssh -T git@gitea.imu.edu.my
```

If asked to confirm the host:

```text
yes
```

A successful connection confirms SSH authentication is working.

---

## Clone the Repository

Clone the project using the SSH repository URL:

```bash
git clone git@gitea.imu.edu.my:<username>/<repository>.git
```

Example:

```bash
git clone git@gitea.imu.edu.my:IzzatRedzuan/IMU-Student-Assessment-Application.git
```

Enter the project directory:

```bash
cd <repository-folder>
```

Example:

```bash
cd IMU-Student-Assessment-Application
```

The project files should now be available on the server.

---

# 5. Configure Environment Variables

Create the `.env` file in the project root:

```bash
nano .env
```

Example:

```env
# Django
SECRET_KEY=your-secret-key
SALT_KEY=your-salt-key

# Database
DB_NAME=imu_assessment_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=3306

# Azure API
AZURE_FUNCTION_KEY=your-function-key
AZURE_BASE_URL=https://your-api-url

# Email
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=your_email@example.com
```

Important:

* Never commit `.env` into Git.
* Request the latest `.env` file from the development team.
* Store environment-specific settings inside `.env`.

---

# 6. Configure Django Allowed Hosts

External testers need permission to access the website.

Open Django settings:

Example:

```bash
nano project/settings.py
```

Find:

```python
ALLOWED_HOSTS = []
```

Update:

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "your-server-ip",
    "*",
]
```

Example:

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "192.168.1.100",
    "*",
]
```

> Warning:
>
> Using `"*"` allows all hosts and should only be used for temporary testing.
> Do not use this configuration for production.

---

# 7. Create Docker Configuration Files

If Docker files do not exist, create them manually.

## Create Dockerfile

From the project root:

```bash
nano Dockerfile
```

Add:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Save:

```text
CTRL + O
ENTER
CTRL + X
```

---

## Create docker-compose.yml

Create the file:

```bash
nano docker-compose.yml
```

Add:

```yaml
services:
  web:
    build: .
    container_name: chiropractic-web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: mysql:8
    container_name: chiropractic-db
    restart: always
    environment:
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

Save:

```text
CTRL + O
ENTER
CTRL + X
```

# 8. Build Docker Images

Build the application containers:

```bash
docker compose build
```

This creates:

* Django application image
* MySQL container configuration

---

# 9. Start Application (Important: Start Database First)

For a fresh server, do not start all containers together immediately.

MySQL requires time to initialize before Django can connect.

Start the database container first:

```bash
docker compose up -d db
```

Check MySQL startup logs:

```bash
docker compose logs -f db
```

Wait until you see:

```text
ready for connections
```

Example:

```text
MySQL Server: ready for connections
port: 3306
```

Exit the log view:

```text
CTRL + C
```

---

# 10. Start Django Web Container

After MySQL is ready, start Django:

```bash
docker compose up -d web
```

Check running containers:

```bash
docker compose ps
```

Expected output:

```text
NAME                  SERVICE   STATUS
chiropractic-db       db        running
chiropractic-web      web       running
```

View Django logs:

```bash
docker compose logs -f web
```

Expected:

```text
Starting development server at http://0.0.0.0:8000/
```

---

# Why Start Database First?

MySQL requires time to initialize during the first startup.

Starting both containers together may cause Django to start before MySQL is ready, resulting in:

```text
django.db.utils.OperationalError:
Can't connect to server on 'db'
```

If this happens:

### 1. Stop only the Django container

```bash
docker compose stop web
```

### 2. Confirm MySQL is ready

```bash
docker compose logs db
```

### 3. Start Django again

```bash
docker compose start web
```

---

# 11. Access Application

From the server:

```text
http://127.0.0.1:8000/
```

From tester computers:

```text
http://your-server-ip:8000/
```

Django administration panel:

```text
http://your-server-ip:8000/admin/
```

---

# 12. Apply Database Migration

Run Django migrations:

```bash
docker compose exec web python manage.py migrate
```

This creates the required database tables.

---

# 13. Collect Static Files

Collect Django static files:

```bash
docker compose exec web python manage.py collectstatic
```

Confirm when prompted.

---

# 14. Create Administrator Account

Create a Django administrator account:

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts:

```text
Username:
Email:
Password:
```

The account can then be used to access:

```text
http://your-server-ip:8000/admin/
```

---

# 15. Django Management Commands

Run Django commands inside the Docker container.

## Create migrations

```bash
docker compose exec web python manage.py makemigrations
```

---

## Apply migrations

```bash
docker compose exec web python manage.py migrate
```

---

## Open Django shell

```bash
docker compose exec web python manage.py shell
```

---

## Collect static files

```bash
docker compose exec web python manage.py collectstatic
```

# 16. View Logs

View logs from all containers:

```bash id="9p5r3a"
docker compose logs -f
```

View Django logs only:

```bash id="g6q0q8"
docker compose logs -f web
```

View MySQL logs only:

```bash id="r8j5hj"
docker compose logs -f db
```

---

# 17. Stop Application

Stop all containers:

```bash id="8w4h6e"
docker compose down
```

Remove containers and database volume:

```bash id="u7n3fh"
docker compose down -v
```

> Warning:
>
> This deletes all MySQL data stored inside Docker volumes.

---

# 18. Restart Application

Start containers:

```bash id="z8m9dy"
docker compose start
```

Stop containers:

```bash id="m4h8p2"
docker compose stop
```

Restart containers:

```bash id="x6g2vp"
docker compose restart
```

---

# 19. Rebuild Application

Rebuild the application after changing:

* Dockerfile
* requirements.txt
* Docker configuration files

Run:

```bash id="1m2x5r"
docker compose down

docker compose build

docker compose up -d
```

For a clean rebuild without using cache:

```bash id="d6p8x4"
docker compose build --no-cache
```

---

# 20. Database Access

Connect to MySQL:

```bash id="n5q7fz"
docker compose exec db mysql -u root -p
```

Create database manually:

```sql id="c8v1mz"
CREATE DATABASE imu_assessment_db;
```

Exit MySQL:

```sql id="s4k2pf"
EXIT;
```

---

# 21. Project Structure

The expected project structure:

```text id="p7w3kx"
project/
│
├── app/
├── project/
├── requirements.txt
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# Troubleshooting

## Docker Not Installed

Check Docker installation:

```bash id="q9k3lw"
docker --version

docker compose version
```

If Docker is missing, repeat the Docker installation section.

---

## Container Not Starting

Check container status:

```bash id="r4m8ds"
docker compose ps
```

View logs:

```bash id="x3v7na"
docker compose logs
```

---

## MySQL Connection Error

Verify database settings in `.env`:

```env id="k8z2qt"
DB_HOST=db
DB_PORT=3306
```

Check database container status:

```bash id="w6n4hs"
docker compose ps
```

Check MySQL logs:

```bash id="c7m2jx"
docker compose logs db
```

---

## Cannot Access Website From Another Computer

Check the following:

---

### 1. Django Allowed Hosts

Verify:

```python id="t5w8py"
ALLOWED_HOSTS = ["*"]
```

> Only use `"*"` for testing environments.

---

### 2. Docker Port Mapping

Confirm `docker-compose.yml` contains:

```yaml id="v3r8qh"
ports:
  - "8000:8000"
```

---

### 3. Firewall Configuration

Check firewall status:

```bash id="j9h2nk"
sudo ufw status
```

Allow application port:

```bash id="b7c4mz"
sudo ufw allow 8000/tcp
```

---

### 4. Test Connection

From another computer, open:

```text id="x8m4dv"
http://your-server-ip:8000
```

---

## Dependency Changes

After adding or updating Python packages:

Update requirements:

```bash id="p5v7nc"
pip freeze > requirements.txt
```

Rebuild containers:

```bash id="z6y8mt"
docker compose build

docker compose up -d
```

---

# Development Notes

* This deployment is intended for testing only.
* Do not expose this configuration directly to the public internet.
* Do not use `ALLOWED_HOSTS=["*"]` in production.
* Run Django management commands inside Docker containers.
* Do not install MySQL directly on the server.
* Keep Docker configuration files under version control.
* Keep `.env` files private and never commit them to Git.
* Use proper production configuration before deploying publicly.
