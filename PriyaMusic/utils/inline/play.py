import math
from pyrogram.types import InlineKeyboardButton
from PriyaMusic.utils.formatters import time_to_seconds


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")],
    ]


def stream_markup_timer(_, chat_id, played, dur):
    pct = (time_to_seconds(played) / (time_to_seconds(dur) or 1)) * 100
    n = math.floor(pct)
    bars = [
        (0, 10, "◉—————————"), (10, 20, "—◉————————"), (20, 30, "——◉———————"),
        (30, 40, "———◉——————"), (40, 50, "————◉—————"), (50, 60, "—————◉————"),
        (60, 70, "——————◉———"), (70, 80, "———————◉——"), (80, 95, "————————◉—"),
    ]
    bar = "—————————◉"
    for lo, hi, b in bars:
        if lo < n <= hi:
            bar = b
            break
    return [
        [InlineKeyboardButton(f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            InlineKeyboardButton("▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton("II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton("↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton("‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton("▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def stream_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton("▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton("II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton("↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton("‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton("▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def aq_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton("▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton("II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton("↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton("‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton("▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(_["P_B_1"], callback_data=f"ALPHAPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"),
            InlineKeyboardButton(_["P_B_2"], callback_data=f"ALPHAPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"),
        ],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [InlineKeyboardButton(_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}")],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    q = query[:20]
    return [
        [
            InlineKeyboardButton(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton("◁", callback_data=f"slider B|{query_type}|{q}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data=f"forceclose {q}|{user_id}"),
            InlineKeyboardButton("▷", callback_data=f"slider F|{query_type}|{q}|{user_id}|{channel}|{fplay}"),
        ],
    ]
