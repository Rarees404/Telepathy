# 🔐 Telepathy

> **Anonymous. Encrypted. Ephemeral.**
> A real-time, end-to-end encrypted chat platform built with Django and browser-native RSA/AES cryptography.

---

## 📖 Overview

**Telepathy** is a secure, anonymous chat application where **privacy is guaranteed by design**. Messages are encrypted entirely on the client side using the Web Crypto API before they ever reach the server — meaning the server **never sees plaintext**. Even if the database were compromised, no readable message content would be exposed.

Two parties join a chat room via a shared 4-digit PIN. Once both connect, they exchange messages secured by **hybrid RSA + AES-GCM encryption** and verified with **RSA-PSS digital signatures**. Every encryption step is visible to the user in real-time through a send progress modal and per-message verification badges.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔑 **Client-Side Key Generation** | Two RSA-2048 key pairs (encryption + signing) are generated in the browser at registration; private keys never leave the client |
| 🔒 **Hybrid Encryption** | AES-256-GCM encrypts the message body; RSA-OAEP wraps the AES key for both sender and receiver |
| ✍️ **Digital Signatures** | Every message is signed with RSA-PSS — the receiver sees a clickable ✓ Verified badge with full crypto details |
| 📊 **Send Progress Modal** | A 6-step animated progress bar shows each encryption operation in real-time when sending a message |
| 💾 **Encrypted-at-Rest** | Only ciphertext is stored in the database — decryption happens exclusively in the browser |
| 📌 **PIN-Based Chat Rooms** | No email required; create or join a room using a 4-digit PIN |
| 🛡️ **Two-Factor Authentication** | Optional TOTP 2FA via QR code and authenticator app (e.g. Google Authenticator) |
| 🚫 **Ephemeral History** | Message history is automatically deleted when a user leaves the chat |
| 🔐 **Token + Session Auth** | DRF Token authentication for API calls; Django sessions for page access; server-side logout invalidates tokens |
| 🎨 **Premium UI** | Dark glassmorphism theme with animated gradients, floating particles, and smooth transitions |

---

## 🏗️ Architecture

```
pentour/
├── chat/                       # Main Django application
│   ├── models.py               # User, Chat, Message models
│   ├── views.py                # REST API views (register, login, send/get messages, etc.)
│   ├── serializers.py          # DRF serializers for User and Message
│   ├── admin.py                # Django admin registrations
│   ├── urls.py                 # URL routing for the chat app
│   └── templates/
│       ├── index.html          # Landing page (glassmorphism hero + particles)
│       ├── auth.html           # Register + Login (crypto log panel)
│       ├── usermenu.html       # Dashboard (create/join chat, PIN modal)
│       ├── chatbox.html        # Chat interface (send modal, verification badges)
│       └── chat/
│           └── 2fa_setup.html  # TOTP two-factor authentication setup
├── pc/                         # Django project configuration
│   ├── settings.py             # App settings (env-driven secrets, DB, security)
│   ├── urls.py                 # Root URL configuration
│   └── asgi.py                 # ASGI entrypoint
├── manage.py
└── requirements.txt
```

### Encryption Flow

```
SENDER (Browser A)                          SERVER                    RECEIVER (Browser B)
──────────────────                          ──────                    ────────────────────
1. Generate random AES-256 key
2. Encrypt message with AES-GCM
3. Wrap AES key with Receiver's            Stores ONLY:
   RSA-OAEP public key              ───►   • AES-GCM ciphertext
4. Wrap AES key with own                    • Wrapped keys (2x)
   RSA-OAEP public key                     • Nonce, tag, signature
5. Sign plaintext with RSA-PSS
6. POST all fields to API
                                                                     7. GET encrypted messages
                                                                     8. Unwrap AES key (RSA-OAEP)
                                                                     9. Decrypt message (AES-GCM)
                                                                    10. Verify signature (RSA-PSS)
                                                                    11. Display ✓ Verified badge
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.1, Django REST Framework |
| **Database** | PostgreSQL (UUID-indexed messages) |
| **Client Crypto** | Web Crypto API (RSA-OAEP, RSA-PSS, AES-256-GCM) |
| **Server Crypto** | `cryptography` library (PEM key validation) |
| **2FA** | `pyotp` (TOTP) + `qrcode` |
| **Frontend** | Vanilla HTML/CSS/JS with glassmorphism design system |

---

## 🚀 Quick Start

> **Prerequisites:** Python 3.10+, PostgreSQL 13+, Git

### 1. Clone & enter the project

```bash
git clone https://github.com/Rarees404/pentour.git
cd pentour
```

### 2. Install & start PostgreSQL

#### macOS (Homebrew)
```bash
brew install postgresql@17
brew services start postgresql@17
```

#### Linux/Ubuntu
```bash
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

#### Windows
Download from [postgresql.org/download](https://www.postgresql.org/download/).

### 3. Create the database

```bash
# Open a PostgreSQL shell
psql -d postgres           # macOS/Linux
psql -U postgres            # Windows
```

Then run:

```sql
CREATE ROLE myproject_user
  WITH LOGIN PASSWORD 'mysecretpassword'
  CREATEDB CREATEROLE INHERIT;

CREATE DATABASE my_database
  OWNER = myproject_user
  ENCODING = 'UTF8'
  TEMPLATE = template0;

\q
```

> **Tip (macOS):** If `psql` asks for a password and you don't know it, change `/opt/homebrew/var/postgresql@17/pg_hba.conf` — replace `md5` or `scram-sha-256` with `trust` in all local lines, then run `brew services restart postgresql@17`.

### 4. Set up Python environment & install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Apply migrations & start the server

```bash
python manage.py migrate
python manage.py runserver
```

Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🧪 Testing the E2E Encryption

> ⚠️ **Important:** You MUST use **two different browsers** (e.g. Chrome + Firefox, or two separate incognito/private windows). Each browser needs its own `localStorage` to store separate user keys and tokens.

### Step-by-step

1. **Browser A** → `http://127.0.0.1:8000/chat/` → Register as `alice` → Login → **Create Chat** → note the 4-digit PIN
2. **Browser B** → `http://127.0.0.1:8000/chat/` → Register as `bob` → Login → **Join Chat** → enter Alice's PIN
3. Both browsers show "Waiting for partner…" briefly, then the chat opens
4. **Send a message** — a progress modal appears showing all 6 encryption steps in real-time:
   - Generating AES-256 session key
   - Encrypting message (AES-256-GCM)
   - Wrapping key for partner (RSA-OAEP)
   - Wrapping key for self (RSA-OAEP)
   - Signing message (RSA-PSS)
   - Sending encrypted payload
5. **Receiver** sees the message with a **✓ Verified** badge — click it to see the individual crypto verification steps (key unwrap, decrypt, signature verify)

---

## 🌐 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/chat/register/` | Create account + upload both public keys | None |
| `POST` | `/chat/login/` | Authenticate and receive a DRF token | None |
| `POST` | `/chat/logout/` | Invalidate token and clear server session | Token |
| `GET` | `/chat/usermenu/` | User dashboard | Session |
| `POST` | `/chat/create-chat/` | Generate a new 4-digit chat PIN | Token |
| `POST` | `/chat/join-chat/` | Join an existing chat by PIN | Token |
| `GET` | `/chat/check-chat/` | Verify chat room exists and participants | Token |
| `POST` | `/chat/send-message/<chat_id>/` | Send an encrypted message | Token |
| `GET` | `/chat/get-messages/<chat_id>/` | Retrieve encrypted messages | Token |
| `GET` | `/chat/get-public-key/<user_id>/` | Fetch user's encryption + signing public keys | Token |
| `POST` | `/chat/upload-public-key/` | Upload/update caller's public keys | Token |
| `POST` | `/chat/leave-chat/` | Leave chat (deletes message history) | Token |
| `GET/POST` | `/chat/2fa/setup/` | Set up TOTP two-factor authentication | Session |

---

## 🗄️ Data Models

### `User` (extends `AbstractUser`)
| Field | Type | Description |
|-------|------|-------------|
| `totp_secret` | `CharField` | TOTP secret for 2FA (never exposed via API) |
| `is_2fa_enabled` | `BooleanField` | Whether 2FA is active |
| `public_key` | `TextField` | RSA-OAEP public key for encryption (PEM) |
| `signing_public_key` | `TextField` | RSA-PSS public key for signature verification (PEM) |

### `Chat`
| Field | Type | Description |
|-------|------|-------------|
| `pin` | `CharField(4)` | Unique 4-digit room code |
| `user1` | `FK(User)` | Chat creator |
| `user2` | `FK(User)` | Chat joiner |
| `is_active` | `BooleanField` | Whether the room is active |

### `Message`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUIDField` | UUID primary key |
| `sender` / `receiver` | `FK(User)` | Message parties |
| `encrypted_text` | `TextField` | AES-GCM ciphertext (Base64) |
| `encrypted_symmetric_key` | `TextField` | AES key wrapped with receiver's RSA public key |
| `sender_encrypted_symmetric_key` | `TextField` | AES key wrapped with sender's own RSA public key |
| `aes_nonce` / `aes_tag` | `TextField` | AES-GCM IV and authentication tag |
| `signature` | `TextField` | RSA-PSS digital signature (Base64) |

---

## 🔧 Environment Variables (Production)

When deploying to production, set these environment variables instead of editing source code:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Insecure dev fallback |
| `DJANGO_DEBUG` | Set to `false` for production | `true` |
| `DJANGO_SECURE` | Set to `true` to enable HTTPS-only cookies, HSTS | `false` |
| `DB_NAME` | PostgreSQL database name | `my_database` |
| `DB_USER` | PostgreSQL user | `myproject_user` |
| `DB_PASSWORD` | PostgreSQL password | `mysecretpassword` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

---

## 🤝 Contributing

Contributions are welcome! Please read [ContributorGuide.md](./ContributorGuide.md) for details on the project structure, where to place static files, and Git workflow conventions.

---

## 📬 Contact

For bugs, questions, or setup issues:

📧 **r.boghean@student.maastrichuniversity.nl**

---

## 📄 License

This project is for academic use. Please contact the author before using it in production or redistributing.
