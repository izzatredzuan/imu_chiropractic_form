# Chiropractic Form System

A Django web application for managing Chiropractic Forms.

---

# Prerequisites

Before running this project, ensure the following software is installed:

- Git
- Python 3.11+ (or the version required by the project)
- MySQL Server 8.x
- Docker Desktop _(optional, for running MySQL using Docker)_

---

# 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

---

# 2. Create a Python Virtual Environment

## Windows (PowerShell / Git Bash)

```bash
python -m venv venv
```

Activate the virtual environment:

### PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Command Prompt

```cmd
venv\Scripts\activate.bat
```

### Git Bash

```bash
source venv/Scripts/activate
```

---

## Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Python Dependencies

Upgrade pip first:

```bash
python -m pip install --upgrade pip
```

Install all required packages:

```bash
pip install -r requirements.txt
```

---

# 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
# Django
SECRET_KEY=your-secret-key
SALT_KEY=your-salt-key

# Database
DB_NAME=chiropractic_form_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Azure API
AZURE_FUNCTION_KEY=your-function-key
AZURE_BASE_URL=https://your-api-url

# Email
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=your_email@example.com
```

> Never commit your `.env` file to Git.
> Please request the `.env` file from your colleague
> All settings config are stored in the o

---

# 5. Install MySQL

## Option A — Native Installation (Windows)

1. Download MySQL Community Server.
2. Install MySQL Server 8.x.
3. During installation:
   - Create a root password.
   - Leave the default port as **3306**.

4. Verify installation:

```bash
mysql -u root -p
```

Create the application database:

```sql
CREATE DATABASE chiropractic_form_db;
```

Exit MySQL:

```sql
EXIT;
```

---

## Option B — Native Installation (Ubuntu / Debian)

Install MySQL:

```bash
sudo apt update
sudo apt install mysql-server
```

Secure the installation:

```bash
sudo mysql_secure_installation
```

Login:

```bash
sudo mysql
```

Create database:

```sql
CREATE DATABASE chiropractic_form_db;
```

Create a user (optional):

```sql
CREATE USER 'django'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON chiropractic_form_db.* TO 'django'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

# 6. Run MySQL Using Docker (Recommended)

If you prefer not to install MySQL directly, Docker can be used.

## Pull MySQL Image

```bash
docker pull mysql:8.0
```

## Start MySQL Container

```bash
docker run -d \
  --name chiropractic-mysql \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=chiropractic_form_db \
  -p 3306:3306 \
  mysql:8.0
```

For Windows PowerShell:

```powershell
docker run -d `
  --name chiropractic-mysql `
  -e MYSQL_ROOT_PASSWORD=your_password `
  -e MYSQL_DATABASE=chiropractic_form_db `
  -p 3306:3306 `
  mysql:8.0
```

Verify the container is running:

```bash
docker ps
```

Stop the container:

```bash
docker stop chiropractic-mysql
```

Start it again:

```bash
docker start chiropractic-mysql
```

---

# 7. Apply Database Migrations

```bash
python manage.py migrate
```

---

# 8. Upload the Latest Static and Media

In project directory copy the latest media and static folder
<project-directory>/static
<project-directory>/media

# 9. Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator account.
Once created the application will auto generate a profile for the admin as well
You will receive the log in the terminal e.g.:

```
Admin profile created: username=admin member_id=Admin001
```

---

# 10. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```
http://127.0.0.1:8000/
```

Admin portal:

```
http://127.0.0.1:8000/admin/
```

---

# Common Commands

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Deactivate Virtual Environment

```bash
deactivate
```

---

## Install New Package

```bash
pip install package_name
pip freeze > requirements.txt
```

---

## Make Model Changes

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Project Structure

```
project/
│
├── app/
├── project/
├── requirements.txt
├── manage.py
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# Troubleshooting

### MySQL Connection Error

- Verify MySQL is running.
- Ensure port **3306** is available.
- Check your `.env` credentials.
- Confirm the database `chiropractic_form_db` exists.

---

### Missing Python Packages

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

---

### Virtual Environment Not Activated

If your terminal does not show `(venv)`, activate the virtual environment before running Django commands.
