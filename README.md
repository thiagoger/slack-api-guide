# Slack Data Extraction Guide

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![Slack API](https://img.shields.io/badge/Slack-API-4A154B.svg?logo=slack)](https://api.slack.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Pull real data out of Slack with the official API, without losing a weekend to OAuth scopes and 403s.

The first time I scripted against Slack, I burned hours on the same walls everyone hits: which token type, which scopes, why search returns nothing. So I wrote down the path that actually works, end to end, with runnable Python. Follow it and you'll be pulling this in about 15 minutes:

- who's online, away, or on do-not-disturb
- messages from any channel you're in
- user profiles and directory info
- search results across the workspace

No scraping, no hacks. Just the official API, explained like a human would.

---

## Table of Contents

1. [How This Works](#how-this-works)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create a Slack App](#step-1-create-a-slack-app)
4. [Step 2: Configure Permissions](#step-2-configure-permissions)
5. [Step 3: Install and Get Tokens](#step-3-install-and-get-tokens)
6. [Step 4: Set Up Python](#step-4-set-up-python)
7. [Step 5: Run the Scripts](#step-5-run-the-scripts)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## How This Works

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Your Code  │ ──API── │   Slack     │ ──────> │    Data     │
│  (Python)   │  Calls  │   Servers   │         │  (JSON)     │
└─────────────┘         └─────────────┘         └─────────────┘
```

1. You create a "Slack App" (gives you permission to access data)
2. Slack gives you a "token" (like a password)
3. Your Python code uses this token to request data
4. Slack returns the data in JSON format
5. You process/store the data however you want

**Is this allowed?** Yes! Slack provides an official API for this purpose.

---

## Prerequisites

| Item | Why You Need It |
|------|-----------------|
| Slack account | Must be member of the workspace |
| Permission to create apps | Ask your workspace admin if needed |
| Python 3.8+ | To run the scripts |

**Check Python installation:**
```bash
python --version
# Should show: Python 3.x.x
```

---

## Step 1: Create a Slack App

### 1.1 Go to Slack API

Open your browser: **https://api.slack.com/apps**

### 1.2 Click "Create New App"

Click the green **"Create New App"** button.

### 1.3 Choose "From scratch"

Select **"From scratch"** (not "From an app manifest").

### 1.4 Configure your app

- **App Name:** `Data Collector` (or any name)
- **Workspace:** Select your workspace

Click **"Create App"**

---

## Step 2: Configure Permissions

### Understanding Token Types

| Token Type | Prefix | Best For |
|------------|--------|----------|
| **Bot Token** | `xoxb-` | Presence monitoring, user info |
| **User Token** | `xoxp-` | Messages, search, DMs |

### 2.1 Go to OAuth & Permissions

In the left sidebar, click **"OAuth & Permissions"**

### 2.2 Add Bot Token Scopes

Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"** and add:

| Scope | Purpose |
|-------|---------|
| `users:read` | Read user information |
| `users:read.email` | Read user emails |

### 2.3 Add User Token Scopes

Under **"User Token Scopes"**, add the scopes you need:

| Scope | Purpose |
|-------|---------|
| `search:read` | Search messages |
| `channels:history` | Read public channel messages |
| `channels:read` | List public channels |
| `groups:history` | Read private channel messages |
| `im:history` | Read direct messages |
| `users:read` | Read user info |

**Tip:** Start with `search:read`, `channels:history`, `channels:read`, and `users:read`.

---

## Step 3: Install and Get Tokens

### 3.1 Install to Workspace

At the top of "OAuth & Permissions", click **"Install to Workspace"**

### 3.2 Authorize

Review permissions and click **"Allow"**

### 3.3 Copy Your Tokens

You'll see:
- **Bot User OAuth Token:** `xoxb-...`
- **User OAuth Token:** `xoxp-...`

**Copy both tokens and save them securely!**

### 3.4 Create your .env file

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and paste your tokens:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here
```

**NEVER commit .env to git!**

---

## Step 4: Set Up Python

### 4.1 Clone this repository

```bash
git clone https://github.com/thiagoger/slack-data-extraction-guide.git
cd slack-data-extraction-guide
```

### 4.2 Create virtual environment

```bash
python -m venv venv
```

### 4.3 Activate it

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4.4 Install dependencies

```bash
pip install -r requirements.txt
```

### 4.5 Configure users to monitor

Edit `config.py` and add user IDs:

```python
MONITOR_USERS = [
    "U01ABC123DE",  # Get this from Slack
    "U02XYZ456FG",
]
```

**How to find User IDs:**
1. Click on someone's profile in Slack
2. Click "View full profile"
3. Click "..." (more)
4. Click "Copy member ID"

---

## Step 5: Run the Scripts

### Check user presence
```bash
python slack_scraper.py --presence
```

Output:
```
============================================================
  PRESENCE CHECK - 2024-01-15 14:30:00
============================================================

  [ONLINE] John Smith
  [AWAY]   Jane Doe
  [ONLINE] Bob Wilson
```

### List all channels
```bash
python slack_scraper.py --channels
```

### Get messages from a channel
```bash
python slack_scraper.py --messages C01ABC123 --limit 50
```

### Search messages
```bash
python slack_scraper.py --search "quarterly report" --limit 20
```

---

## Troubleshooting

### Error: `missing_scope`

**Problem:** App doesn't have the required permission.

**Solution:**
1. Go to api.slack.com/apps
2. Select your app → OAuth & Permissions
3. Add the missing scope
4. Click **"Reinstall to Workspace"**
5. Copy new tokens to .env

### Error: `invalid_auth`

**Problem:** Token is wrong or expired.

**Solution:**
- Check .env file for typos
- Verify you're using the right token type
- Reinstall app and get fresh tokens

### Error: `channel_not_found`

**Problem:** Wrong channel ID or not a member.

**Solution:**
- Use channel ID (`C01ABC123`), not name (`#general`)
- Make sure you're a member of the channel

### Error: `ratelimited`

**Problem:** Too many requests.

**Solution:**
- Add delays between requests (180+ seconds for presence)
- See rate limits section below

---

## API Reference

### Endpoints

| Endpoint | Token | Description |
|----------|-------|-------------|
| `users.list` | Bot | Get all workspace users |
| `users.info` | Bot | Get one user's details |
| `users.getPresence` | Bot | Get online/away status |
| `conversations.list` | User | List channels |
| `conversations.history` | User | Get channel messages |
| `search.messages` | User | Search messages |

### Rate Limits

| Tier | Limit | Use Case |
|------|-------|----------|
| Tier 1 | 1/sec | Posting messages |
| Tier 2 | 20+/min | Reading data |
| Tier 3 | 50+/min | Heavy reads |

**Safe interval for presence monitoring:** 180 seconds (3 minutes)

### Presence Status Values

| Status | Meaning |
|--------|---------|
| `active` | User is online (green dot) |
| `away` | User inactive 10+ minutes |

---

## Project Structure

```
slack-data-extraction-guide/
├── README.md           # This file
├── .env.example        # Template for tokens
├── .gitignore          # Ignores .env and venv
├── requirements.txt    # Python dependencies
├── config.py           # Configuration
└── slack_scraper.py    # Main script
```

---

## Contributing

Found an issue or want to improve the guide? Open a PR!

## License

MIT License - Use freely for any purpose.

---

**Author:** Thiago (TestBox TSA)
**Based on:** Production system monitoring 39 users
