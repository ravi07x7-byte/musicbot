from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config
from PriyaMusic import app


# ── queue.py ──────────────────────────────────────────────────────────────────
def queue_markup(_, DURATION, CPLAY, videoid, played=None, dur=None):
    base = [InlineKeyboardButton(_["QU_B_1"], callback_data=f"GetQueued {CPLAY}|{videoid}"),
            InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")]
    if DURATION == "Unknown":
        return InlineKeyboardMarkup([[*base]])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_["QU_B_2"].format(played, dur), callback_data="GetTimer")],
        [*base],
    ])


def queue_back_markup(_, CPLAY):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_["BACK_BUTTON"], callback_data=f"queue_back_timer {CPLAY}"),
        InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close"),
    ]])


# ── settings.py ───────────────────────────────────────────────────────────────
def setting_markup(_):
    return [
        [InlineKeyboardButton(_["ST_B_1"], callback_data="AU"),
         InlineKeyboardButton(_["ST_B_3"], callback_data="LG")],
        [InlineKeyboardButton(_["ST_B_2"], callback_data="PM")],
        [InlineKeyboardButton(_["ST_B_4"], callback_data="VM")],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def vote_mode_markup(_, current, mode=None):
    return [
        [InlineKeyboardButton("Voting Mode →", callback_data="VOTEANSWER"),
         InlineKeyboardButton(_["ST_B_5"] if mode else _["ST_B_6"], callback_data="VOMODECHANGE")],
        [InlineKeyboardButton("-2", callback_data="FERRARIUDTI M"),
         InlineKeyboardButton(f"Current: {current}", callback_data="ANSWERVOMODE"),
         InlineKeyboardButton("+2", callback_data="FERRARIUDTI A")],
        [InlineKeyboardButton(_["BACK_BUTTON"], callback_data="settings_helper"),
         InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def auth_users_markup(_, status=None):
    return [
        [InlineKeyboardButton(_["ST_B_7"], callback_data="AUTHANSWER"),
         InlineKeyboardButton(_["ST_B_8"] if status else _["ST_B_9"], callback_data="AUTH")],
        [InlineKeyboardButton(_["ST_B_1"], callback_data="AUTHLIST")],
        [InlineKeyboardButton(_["BACK_BUTTON"], callback_data="settings_helper"),
         InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


def playmode_users_markup(_, Direct=None, Group=None, Playtype=None):
    return [
        [InlineKeyboardButton(_["ST_B_10"], callback_data="SEARCHANSWER"),
         InlineKeyboardButton(_["ST_B_11"] if Direct else _["ST_B_12"], callback_data="MODECHANGE")],
        [InlineKeyboardButton(_["ST_B_13"], callback_data="AUTHANSWER"),
         InlineKeyboardButton(_["ST_B_8"] if Group else _["ST_B_9"], callback_data="CHANNELMODECHANGE")],
        [InlineKeyboardButton(_["ST_B_14"], callback_data="PLAYTYPEANSWER"),
         InlineKeyboardButton(_["ST_B_8"] if Playtype else _["ST_B_9"], callback_data="PLAYTYPECHANGE")],
        [InlineKeyboardButton(_["BACK_BUTTON"], callback_data="settings_helper"),
         InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]


# ── speed.py ──────────────────────────────────────────────────────────────────
def speed_markup(_, chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🕒 0.5x", callback_data=f"SpeedUP {chat_id}|0.5"),
         InlineKeyboardButton("🕓 0.75x", callback_data=f"SpeedUP {chat_id}|0.75")],
        [InlineKeyboardButton(_["P_B_4"], callback_data=f"SpeedUP {chat_id}|1.0")],
        [InlineKeyboardButton("🕤 1.5x", callback_data=f"SpeedUP {chat_id}|1.5"),
         InlineKeyboardButton("🕛 2.0x", callback_data=f"SpeedUP {chat_id}|2.0")],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ])


# ── start.py ──────────────────────────────────────────────────────────────────
def start_panel(_):
    return [
        [InlineKeyboardButton(_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"),
         InlineKeyboardButton(_["S_B_2"], url=config.SUPPORT_CHAT)],
    ]


def private_panel(_):
    return [
        [InlineKeyboardButton(_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true")],
        [InlineKeyboardButton("˹ Support ˼", callback_data="purvi_scb"),
         InlineKeyboardButton("💌 YT API", callback_data="bot_info_data")],
        [InlineKeyboardButton(_["S_B_4"], callback_data="settings_back_helper")],
    ]


# ── stats.py ──────────────────────────────────────────────────────────────────
def stats_buttons(_, is_sudo):
    rows = [
        [InlineKeyboardButton(_["SA_B_2"], callback_data="bot_stats_sudo"),
         InlineKeyboardButton(_["SA_B_3"], callback_data="TopOverall")]
        if is_sudo else
        [InlineKeyboardButton(_["SA_B_1"], callback_data="TopOverall")],
        [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")],
    ]
    return InlineKeyboardMarkup(rows)


def back_stats_buttons(_):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_["BACK_BUTTON"], callback_data="stats_back"),
        InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close"),
    ]])


# ── help.py ───────────────────────────────────────────────────────────────────
def help_pannel(_, START=None):
    close_row = [InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")]
    back_row = [InlineKeyboardButton(_["BACK_BUTTON"], callback_data="settingsback_helper")]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_["H_B_1"], callback_data="help_callback hb1"),
         InlineKeyboardButton(_["H_B_2"], callback_data="help_callback hb2"),
         InlineKeyboardButton(_["H_B_3"], callback_data="help_callback hb3")],
        [InlineKeyboardButton(_["H_B_4"], callback_data="help_callback hb4"),
         InlineKeyboardButton(_["H_B_5"], callback_data="help_callback hb5"),
         InlineKeyboardButton(_["H_B_6"], callback_data="help_callback hb6")],
        [InlineKeyboardButton(_["H_B_7"], callback_data="help_callback hb7"),
         InlineKeyboardButton(_["H_B_8"], callback_data="help_callback hb8"),
         InlineKeyboardButton(_["H_B_9"], callback_data="help_callback hb9")],
        back_row if START else close_row,
    ])


def help_back_markup(_):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_["BACK_BUTTON"], callback_data="settings_back_helper")
    ]])


def private_help_panel(_):
    return [[InlineKeyboardButton(_["S_B_3"], url=f"https://t.me/{app.username}?start=help")]]
