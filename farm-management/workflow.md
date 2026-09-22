# Farm Management Platform Workflow

This guide explains how to install, configure, run, and use the Farm Management Platform locally on Windows.

## 1. Prerequisites

Install the following before starting:

- Python 3.11 or newer
- Git
- Visual Studio Code (recommended)
- Docker Desktop (optional)

The project uses SQLite automatically when `DATABASE_URL` is empty. PostgreSQL can be configured for shared or production environments.

## 2. Get the project

Open PowerShell and clone the repository:

```powershell
git clone https://github.com/Aritra-Karan47/farm-management.git
cd farm-management
```

If the project is already downloaded, open the folder that contains `manage.py`:

```powershell
cd C:\Users\ASUS\Desktop\farm-management\farm-management
```

## 3. Create and activate a virtual environment

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run PowerShell as the current user and then retry:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure environment variables

Create a local `.env` file from the example file:

```powershell
Copy-Item .env.example .env
```

For local development, the default values are sufficient. Important settings include:

- `DJANGO_SETTINGS_MODULE=config.settings.development`
- `DEBUG=True`
- An appropriate `SECRET_KEY`
- An empty `DATABASE_URL` to use `db.sqlite3`
- Empty Supabase variables to store uploaded files in the local `media/` directory

Never commit `.env` or real credentials to Git.

## 6. Create the database

Run migrations from the directory containing `manage.py`:

```powershell
python manage.py makemigrations
python manage.py migrate
```

The `migrate` command creates Django’s tables, including the custom user table named `accounts_user`.

If the login page reports `no such table: accounts_user`, the database migrations have not been applied to the database currently being used. Run the two migration commands again and confirm that `DATABASE_URL` points to the intended database.

For a new local database, create an administrator account:

```powershell
python manage.py createsuperuser
```

Follow the prompts for username, email, and password.

## 7. Start the development server

```powershell
python manage.py runserver
```

Open these URLs in a browser:

- Application: <http://127.0.0.1:8000/>
- Login: <http://127.0.0.1:8000/accounts/login/>
- Dashboard: <http://127.0.0.1:8000/dashboard/>
- Animals: <http://127.0.0.1:8000/animals/>
- Reports: <http://127.0.0.1:8000/reports/>
- Administration: <http://127.0.0.1:8000/admin/>

The root URL redirects to the dashboard. Unauthenticated users are redirected to the login page.

## 8. Basic user workflow

1. Open the application URL.
2. Sign in using the account created with `createsuperuser` or another valid account.
3. Review the dashboard.
4. Use the Animals area to view animal records and profiles.
5. Use Reports to view available farm summaries.
6. Use the Admin area to manage users and registered data when administrator permissions are required.
7. Use the password-change page when you need to update your password:
   <http://127.0.0.1:8000/accounts/password-change/>
8. Use the logout option when finished.

## 9. Common development commands

Check the project configuration:

```powershell
python manage.py check
```

Run the test suite:

```powershell
python manage.py test
```

Create migrations after changing models:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Collect static files when preparing a deployment:

```powershell
python manage.py collectstatic
```

## 10. Optional Docker workflow

Ensure Docker Desktop is running, then create `.env` as described above and run:

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8000/> after the container starts. The compose service runs database migrations before starting the web server and stores uploaded media in a Docker volume.

Stop the containers with:

```powershell
docker compose down
```

## 11. Database and file storage

- With no `DATABASE_URL`, data is stored in the local `db.sqlite3` file.
- With `DATABASE_URL`, Django uses the configured PostgreSQL database.
- With no Supabase settings, uploaded files are stored under `media/`.
- Supabase storage can be enabled by setting `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and `SUPABASE_BUCKET` in `.env`.

Back up the database and media files before deleting or recreating them.

## 12. Troubleshooting

### `no such table: accounts_user`

Activate the correct virtual environment, confirm that you are in the folder containing `manage.py`, and run:

```powershell
python manage.py migrate
```

If using PostgreSQL, verify `DATABASE_URL`. If it is set, Django will use PostgreSQL instead of SQLite.

### `ModuleNotFoundError` or missing packages

Activate `venv` and reinstall dependencies:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port 8000 is already in use

Start the server on another port:

```powershell
python manage.py runserver 8001
```

Then open <http://127.0.0.1:8001/>.

### Changes are not visible

Confirm that the development server is running from the project directory, refresh the browser, and run migrations after model changes.

## 13. Development contribution workflow

1. Create a feature branch.
2. Activate the virtual environment.
3. Install or update dependencies.
4. Make the code change.
5. Run `python manage.py check` and `python manage.py test`.
6. Create and apply migrations if models changed.
7. Review the change in the browser.
8. Commit the change and push the branch.
9. Pull remote changes before pushing if Git reports `fetch first`.

Do not commit `venv/`, `.env`, `db.sqlite3`, `media/`, or generated `staticfiles/` files.
