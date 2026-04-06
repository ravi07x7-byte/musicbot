import os
import yaml

languages: dict = {}
languages_present: dict = {}


def get_string(lang: str) -> dict:
    return languages.get(lang, languages.get("en", {}))


# Load English first as base
_en_path = os.path.join(os.path.dirname(__file__), "langs", "en.yml")
with open(_en_path, encoding="utf8") as f:
    languages["en"] = yaml.safe_load(f)
    languages_present["en"] = languages["en"].get("name", "English")

# Load all other languages, falling back to English for missing keys
_langs_dir = os.path.join(os.path.dirname(__file__), "langs")
for _fname in os.listdir(_langs_dir):
    if not _fname.endswith(".yml") or _fname == "en.yml":
        continue
    _lang_code = _fname[:-4]
    try:
        with open(os.path.join(_langs_dir, _fname), encoding="utf8") as f:
            _data = yaml.safe_load(f)
        # Inherit missing keys from English
        merged = dict(languages["en"])
        merged.update(_data)
        languages[_lang_code] = merged
        languages_present[_lang_code] = merged.get("name", _lang_code)
    except Exception as e:
        print(f"[strings] Failed to load {_fname}: {e}")


# Helpers module (for long text blocks used in /help)
class helpers:
    HELP_1 = """<b><u>❖ Admin Module Help:</u></b>

<b>Add <code>c</code> prefix for channel commands.</b>

<b>๏ /pause</b> — Pause current stream
<b>๏ /resume</b> — Resume paused stream
<b>๏ /skip</b> — Skip to next track
<b>๏ /end / /stop</b> — Clear queue and stop
<b>๏ /queue</b> — Show queued tracks
<b>๏ /loop [enable/disable/1-10]</b> — Loop stream
<b>๏ /shuffle</b> — Shuffle queue
<b>๏ /seek [seconds]</b> — Seek forward
<b>๏ /seekback [seconds]</b> — Seek backward
<b>๏ /speed [0.5/0.75/1.0/1.5/2.0]</b> — Change playback speed"""

    HELP_2 = """<b><u>❖ Auth Module Help:</u></b>

Auth users can use admin commands without being group admins.

<b>๏ /auth [user]</b> — Add to auth list
<b>๏ /unauth [user]</b> — Remove from auth list
<b>๏ /authusers</b> — Show auth list"""

    HELP_3 = """<b><u>❖ Blacklist / Block Module Help:</u></b>

<b>๏ /blacklistchat [chat_id]</b> — Blacklist a chat
<b>๏ /whitelistchat [chat_id]</b> — Whitelist a chat
<b>๏ /blacklistedchats</b> — Show blacklisted chats

<b>๏ /ban [user]</b> — Ban user from current group
<b>๏ /unban [user]</b> — Unban user
<b>๏ /dban</b> — Ban all deleted accounts
<b>๏ /sban</b> — Smart scan and selective ban
<b>๏ /block [user]</b> — Block from using bot
<b>๏ /unblock [user]</b> — Unblock user"""

    HELP_4 = """<b><u>❖ Broadcast Module Help:</u></b>

<b>๏ /broadcast [msg]</b> — Broadcast to all served chats

<b>Flags:</b>
<code>-pin</code> — Pin silently
<code>-pinloud</code> — Pin with notification
<code>-user</code> — Broadcast to users
<code>-nobot</code> — Skip bot broadcast"""

    HELP_5 = """<b><u>❖ Ping / Stats Module Help:</u></b>

<b>๏ /ping</b> — Bot ping and system stats
<b>๏ /stats</b> — Global stats and top tracks"""

    HELP_6 = """<b><u>❖ Play Module Help:</u></b>

<b>Prefixes:</b>
<b>c</b> = channel play | <b>v</b> = video | <b>force</b> = force play

<b>๏ /play</b> — Play audio
<b>๏ /vplay</b> — Play video
<b>๏ /cplay</b> — Play in connected channel
<b>๏ /playforce</b> — Force play (skip current)
<b>๏ /autoplay [on/off/category]</b> — Smart autoplay
<b>๏ /channelplay [id/linked/disable]</b> — Connect channel"""

    HELP_7 = """<b><u>❖ Sudo Module Help:</u></b>

<b>๏ /addsudo [user]</b> — Add sudo user
<b>๏ /rmsudo [user]</b> — Remove sudo user
<b>๏ /sudolist</b> — List sudo users
<b>๏ /delallsudo</b> — Remove all sudo users"""

    HELP_8 = """<b><u>❖ Active Voice Chats Module Help:</u></b>

<b>๏ /activevoice</b> — List active voice chats
<b>๏ /activevideo</b> — List active video chats
<b>๏ /autoend [enable/disable]</b> — Auto-end when no listeners"""

    HELP_9 = """<b><u>❖ Start / Settings Module Help:</u></b>

<b>๏ /start</b> — Start the bot
<b>๏ /help</b> — Show this menu
<b>๏ /settings</b> — Group settings
<b>๏ /reload</b> — Refresh admin cache
<b>๏ /reboot</b> — Reboot bot for this chat
<b>๏ /lang</b> — Change language
<b>๏ /playmode</b> — Change play mode

<b>Owner Only:</b>
<b>๏ /setbotname</b> — Rename bot
<b>๏ /setbotbio</b> — Change bio
<b>๏ /setbotphoto</b> — Change profile photo"""
