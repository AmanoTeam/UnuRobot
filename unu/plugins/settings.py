from functools import partial

from hydrogram import Client, filters
from hydrogram.enums import ChatMemberStatus, ChatType
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import games
from unu.card import cards
from unu.db import Chat, User
from unu.locales import get_locale_string, langdict, use_chat_lang, use_user_lang
from unu.utils import filter_sudoers


@Client.on_callback_query(filters.regex("^settings$") & filters.private)
@Client.on_message(filters.command("settings") & filters.private)
@use_chat_lang()
async def settings_pvt(c: Client, m: Message | CallbackQuery, t):
    func = m.reply_text if isinstance(m, Message) else m.edit_message_text

    x = await User.get(id=m.from_user.id)
    keyb = [
        [(t("language"), "info_lang"), (t("lang_flag"), "lang")],
        [(t("status"), "status"), ("✅" if x.placar else "✖️", "ch_status")],
    ]

    if await filter_sudoers(c, m):
        keyb.append([("sudos", "sudos")])

    keyb.append([(t("back"), "start")])

    await func(t("settings"), reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex("^settings$|^mode_") & ~filters.private)
@Client.on_message(filters.command("settings") & ~filters.private)
@use_chat_lang()
async def settings_and_mode(c: Client, m: Message | CallbackQuery, t):
    chat_id = m.chat.id if isinstance(m, Message) else m.message.chat.id
    admin = await c.get_chat_member(chat_id, m.from_user.id)
    print(admin)
    if admin.status == ChatMemberStatus.MEMBER and not await filter_sudoers(c, m):
        await m.reply(t("admin_only"))
        return
    if games.get(chat_id) and games[chat_id].is_started:
        await m.reply(t("game_running"))
        return
    x = (await Chat.get_or_create(id=chat_id))[0]
    if isinstance(m, CallbackQuery) and m.data.startswith("mode_"):
        if m.data == "mode_seven":
            await Chat.get(id=chat_id).update(seven=not x.seven)
        elif m.data == "mode_bluff":
            await Chat.get(id=chat_id).update(bluff=not x.bluff)
        elif m.data == "mode_one_win":
            await Chat.get(id=chat_id).update(one_win=not x.one_win)
        elif m.data == "mode_one_card":
            await Chat.get(id=chat_id).update(one_card=not x.one_card)
        elif m.data == "mode_stack":
            await Chat.get(id=chat_id).update(satack=not x.satack)
        elif m.data == "mode_draw_one":
            await Chat.get(id=chat_id).update(draw_one=not x.draw_one)
        elif m.data == "mode_auto_pin":
            admin = await c.get_chat_member(chat_id, c.me.id)
            print(admin)
            if admin.privileges and admin.privileges.can_pin_messages:
                await Chat.get(id=chat_id).update(auto_pin=not x.auto_pin)
            else:
                await m.answer(t("admin_only"))
                return
        await m.answer("Done!")
        x = await Chat.get(id=chat_id)
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("theme"), callback_data="info_theme"),
            InlineKeyboardButton(t(x.theme), callback_data="theme"),
        ],
        [
            InlineKeyboardButton(t("seven_zero"), callback_data="info_seven"),
            InlineKeyboardButton("✅" if x.seven else "✖️", callback_data="mode_seven"),
        ],
        [
            InlineKeyboardButton(t("sbluff"), callback_data="info_bluff"),
            InlineKeyboardButton("✅" if x.bluff else "✖️", callback_data="mode_bluff"),
        ],
        [
            InlineKeyboardButton(t("one_win"), callback_data="info_one_win"),
            InlineKeyboardButton("✅" if x.one_win else "✖️", callback_data="mode_one_win"),
        ],
        [
            InlineKeyboardButton(t("one_card"), callback_data="info_one_card"),
            InlineKeyboardButton("✅" if x.one_card else "✖️", callback_data="mode_one_card"),
        ],
        [
            InlineKeyboardButton(t("auto_pin"), callback_data="info_auto_pin"),
            InlineKeyboardButton("✅" if x.auto_pin else "✖️", callback_data="mode_auto_pin"),
        ],
        [
            InlineKeyboardButton(t("stack"), callback_data="info_stack"),
            InlineKeyboardButton("✅" if x.satack else "✖️", callback_data="mode_stack"),
        ],
        [
            InlineKeyboardButton(t("draw_one"), callback_data="info_draw_one"),
            InlineKeyboardButton("✅" if x.draw_one else "✖️", callback_data="mode_draw_one"),
        ],
        [
            InlineKeyboardButton(t("language"), callback_data="info_lang"),
            InlineKeyboardButton(t("lang_flag"), callback_data="lang"),
        ],
    ])
    if isinstance(m, Message):
        await m.reply_text(t("settings"), reply_markup=keyb)
    else:
        await m.edit_message_text(t("settings"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^theme"))
@use_chat_lang()
async def theme(c: Client, cq: CallbackQuery, t):
    admin = await c.get_chat_member(cq.message.chat.id, cq.from_user.id)
    if admin.status is ChatMemberStatus.MEMBER and not await filter_sudoers(c, cq):
        await cq.answer(t("admin_only"))
        return
    if " " in cq.data:
        theme = cq.data.split(" ")[1]
        await Chat.get(id=cq.message.chat.id).update(theme=theme)
        keyb = InlineKeyboardMarkup([[InlineKeyboardButton(t("back"), callback_data="theme")]])
        await cq.message.edit_text(t("theme_changed").format(theme=theme), reply_markup=keyb)
    else:
        themes = cards.keys()
        tkeyb = [
            InlineKeyboardButton(text=t(theme), callback_data=f"theme {theme}") for theme in themes
        ]
        keyb = InlineKeyboardMarkup([
            tkeyb,
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ])
        await cq.message.edit_text(t("theme_config"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^lang"))
@use_chat_lang()
async def lang(c: Client, cq: CallbackQuery, t):
    if cq.message.chat.type != ChatType.PRIVATE:
        admin = await c.get_chat_member(cq.message.chat.id, cq.from_user.id)
        if admin.status is ChatMemberStatus.MEMBER and not await filter_sudoers(c, cq):
            await cq.answer(t("admin_only"))
            return
    if "_" in cq.data:
        nt = partial(get_locale_string, cq.data.split("_")[1])
        if cq.message.chat.type == ChatType.PRIVATE:
            await User.get(id=cq.message.chat.id).update(lang=cq.data.split("_")[1])
        else:
            await Chat.get(id=cq.message.chat.id).update(lang=cq.data.split("_")[1])
        keyb = InlineKeyboardMarkup([[InlineKeyboardButton(nt("back"), callback_data="settings")]])
        await cq.message.edit_text(nt("lang_changed"), reply_markup=keyb)
    else:
        keyb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    get_locale_string(lang, "lang_name")
                    + " "
                    + get_locale_string(lang, "lang_flag"),
                    callback_data=f"lang_{lang}",
                )
            ]
            for lang in langdict
        ])
        await cq.message.edit_text(t("choose_lang"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^info_"))
@use_user_lang()
async def info(c: Client, cq: CallbackQuery, t):
    await cq.answer(t(cq.data), show_alert=True)
