# 🚀 AutoBackupTool

**AutoBackupTool** is your all-in-one Python desktop app for effortless, secure, and stylish folder backups to Google Drive.

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python Version">
  
  <img src="https://img.shields.io/badge/GUI-tkinter-darkblue" alt="tkinter GUI">
</div>

---

## 🌟 Why AutoBackupTool?

- 🔒 **Strong Encryption:** Your data is protected with `cryptography.Fernet`
- 🗓️ **Flexible Scheduling:** Backup once, daily, or weekly—set it and forget it!
- 🖤 **Modern Dark Mode:** Clean, intuitive GUI with progress bars
- ☁️ **Google Drive Integration:** Upload, restore, and manage backups with ease
- 🔄 **One-Click Restore:** Recover and decrypt your files anytime

---

## ✨ Features

- 📦 Compresses & encrypts folders before upload
- ☁️ Uploads encrypted files to your Google Drive
- 🕒 Schedule or run backups manually
- 🔄 Restore tool for easy recovery & decryption
- 🌑 Sleek dark mode interface

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Eraiyanbupeterfrancis/AutoBackupTool.git
cd AutoBackupTool
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```
Or manually:
```bash
pip install cryptography pydrive2 python-dotenv schedule
```

---

## ⚙️ Google Drive API Setup

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Go to **APIs & Services > Library** and enable **Google Drive API**
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth client ID**
6. Choose **Desktop app**
7. Download `client_secrets.json` and place it in your project folder

> **Tip:** If in testing mode, add your Google account as a test user under **OAuth consent screen**.

---

## 🔐 Configuration

Create a `backup.env` file:

```env
ENCRYPTION_KEY=YOUR_ENCRYPTION_KEY_HERE
CLIENT_SECRETS_FILE=client_secrets.json
```

**Generate an encryption key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

> ⚠️ **Never commit `backup.env` or `client_secrets.json` to GitHub!**

---

## 🛡️ Security First

- All backups are encrypted before upload
- Only you (with credentials + key) can decrypt
- Google Drive access is limited to your app’s OAuth scope

---

## 💻 How to Use

```bash
python backup_gui.py
```

- Select a folder → choose schedule → start backup
- Use **Restore Backup** to recover and decrypt

---

## 🏗️ Build a Standalone EXE

```bash
pyinstaller --name AutoBackupTool --onefile --windowed --icon=autobackuptool.ico backup_gui.py
```
Or:
```bash
pyinstaller AutoBackupTool.spec
```

---

## 📌 .gitignore Example

```
backup.env
client_secrets.json
mycreds.txt
*.enc
*.zip
dist/
build/
__pycache__/
```

---

## 🙌 Credits

- GUI: `tkinter`, `ttk`
- Encryption: `cryptography`
- Cloud: `pydrive2`
- Scheduler: `schedule`
- Env management: `python-dotenv`

---


---

<div align="center">
  <b>⭐ Star this repo if you find it useful!</b>
