# 🎵 PriyaMusic

A feature-rich, secure, production-ready Telegram Music Bot built with Python, Pyrogram and PyTgCalls.

---

## ✨ Features

- **Multi-platform** — YouTube, Spotify, Apple Music, SoundCloud, Resso, Telegram files
- **Smart Autoplay** — Detects song category (pop, bollywood, lofi, rock, etc.) and keeps playing similar songs for up to 5 hours of idle time
- **Smart Ban System** — `/sban` scans the group and lets you choose to ban deleted accounts, real accounts, or select specific users
- **Full Group Management** — ban, unban, gban, dban, auth users, blacklist chats
- **Security Layer** — Intrusion detection: any unauthorized `/eval` or `/sh` attempt instantly alerts the owner with a pinned log
- **Bot Customisation** — Owner can rename the bot, change bio and photo via commands
- **Multi-assistant** — Up to 5 assistant accounts
- **Deploy anywhere** — Heroku, Railway, VPS

---

## 🚀 Deploy

### Heroku
[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20On%20Heroku-green?style=for-the-badge&logo=heroku)](https://dashboard.heroku.com/new?template=https://github.com/yourusername/PriyaMusic)

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### VPS / Local
```bash
# Install dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install python3-pip ffmpeg git -y

# Clone and setup
git clone https://github.com/yourusername/PriyaMusic
cd PriyaMusic

# Install Python requirements
pip3 install -U pip
pip3 install -r requirements.txt

# Configure environment
cp sample.env .env
nano .env   # Fill in your values

# Run
bash start
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | From https://my.telegram.org |
| `API_HASH` | ✅ | From https://my.telegram.org |
| `BOT_TOKEN` | ✅ | From @BotFather |
| `MONGO_DB_URI` | ✅ | From https://cloud.mongodb.com |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `STRING_SESSION` | ✅ | Pyrogram v2 string session |
| `LOGGER_ID` | ✅ | Log group/channel ID |
| `STRING_SESSION2-5` | ❌ | Extra assistant sessions |
| `HEROKU_APP_NAME` | ❌ | For Heroku deploy |
| `HEROKU_API_KEY` | ❌ | For Heroku deploy |
| `SPOTIFY_CLIENT_ID` | ❌ | For Spotify support |
| `SPOTIFY_CLIENT_SECRET` | ❌ | For Spotify support |
| `BOT_NAME` | ❌ | Custom bot display name |
| `AUTOPLAY_IDLE_MINUTES` | ❌ | Default: 300 (5 hours) |

---

## 📜 Commands

### Music
| Command | Description |
|---|---|
| `/play` | Play audio |
| `/vplay` | Play video |
| `/cplay` | Play in linked channel |
| `/playforce` | Force play (skip current) |
| `/pause` | Pause stream |
| `/resume` | Resume stream |
| `/skip` | Skip track |
| `/end` / `/stop` | Stop and clear queue |
| `/loop [enable/disable/1-10]` | Loop stream |
| `/shuffle` | Shuffle queue |
| `/seek [seconds]` | Seek forward |
| `/seekback [seconds]` | Seek backward |
| `/speed` | Change playback speed |
| `/queue` | Show queue |
| `/autoplay [on/off/category]` | Smart autoplay |

### Group Management
| Command | Description |
|---|---|
| `/ban` | Ban user |
| `/unban` | Unban user |
| `/dban` | Ban all deleted accounts |
| `/sban` | Smart scan and selective ban |
| `/gban` | Global ban across all chats |
| `/ungban` | Remove global ban |
| `/auth` | Add auth user |
| `/unauth` | Remove auth user |
| `/blacklistchat` | Blacklist a chat |

### Owner Only
| Command | Description |
|---|---|
| `/setbotname` | Rename the bot |
| `/setbotbio` | Change bot bio |
| `/setbotphoto` | Change bot photo |
| `/eval` | Execute Python code |
| `/sh` | Execute shell command |
| `/addsudo` | Add sudo user |
| `/delsudo` | Remove sudo user |
| `/broadcast` | Broadcast to all chats |
| `/update` | Pull latest updates |
| `/restart` | Restart the bot |

---

## 🔐 Security

- All `/eval` and `/sh` attempts by non-owners are **instantly logged to the owner DM + log channel (pinned)**
- Suspicious messages containing code patterns are flagged
- Smart ban system requires confirmation before banning real accounts
- Sensitive credentials never exposed in any command output

---

## 📞 Support

- Channel: https://t.me/yourchannel
- Group: https://t.me/yoursupport
