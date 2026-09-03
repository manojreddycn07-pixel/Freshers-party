# PythonAnywhere hosting

1. Create a **Beginner** web app at [PythonAnywhere](https://www.pythonanywhere.com), choosing **Manual configuration** and your Python version.
2. Upload this `Freshers` folder to `/home/YOUR_USERNAME/freshers` using the **Files** tab.
3. Open a PythonAnywhere **Bash console** and run:

```bash
cd ~/freshers
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. In the **Web** tab, edit the WSGI configuration file. Replace its content with the content of `passenger_wsgi.py`, replacing `YOUR_PYTHONANYWHERE_USERNAME` with your username.
5. In the **Web** tab, add these environment variables:

```text
SECRET_KEY=a-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose-a-strong-password
```

6. Click **Reload**. Your website URL appears at the top of the Web tab.

Admin login: `https://YOUR_USERNAME.pythonanywhere.com/admin`

Keep the default `admin123` password only for local testing; change it before publishing.
