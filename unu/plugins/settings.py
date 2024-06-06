from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery
from hydrogram.enums import ChatType, ChatMemberStatus
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union
from functools import partial
from unu.card import cards
from unu.db import Chat, User
from config import games
from unu.locales import langs, get_locale_string, use_chat_lang, use_user_lang
from hydrogram.helpers import ikb


@Client.on_callback_query(filters.regex("^settings$"))
@Client.on_message(filters.command("settings"))
@use_chat_lang()
async def settings(c: Client, m: Union[Message, CallbackQuery], t):
    if (
        isinstance(m, Message)
        and m.chat.type == ChatType.PRIVATE
        or isinstance(m, CallbackQuery)
        and m.message.chat.type == ChatType.PRIVATE
    ):
        print(m)
        if isinstance(m, Message):
            func = m.reply_text
        else:
            func = m.edit_message_text

        x = await User.get(id=m.from_user.id)
        keyb = [
            [(t("language"), "info_lang"), (t("lang_flag"), "lang")],
            [(t("status"), "status"), ("✅" if x.placar else "✖️", "ch_status")],
        ]

        if await filters.filter_sudoers(c, m):
            keyb.append([("sudos", "sudos")])

        keyb.append([(t("back"), "start")])

        await func(t("settings"), reply_markup=ikb(keyb))
    else:
        chat_id = m.chat.id if isinstance(m, Message) else m.message.chat.id
        admin = await c.get_chat_member(chat_id, m.from_user.id)
        print(admin)
        if admin.status == ChatMemberStatus.MEMBER:
            await m.reply("You need to be an admin to change the settings!")
            return
        if games.get(chat_id) and games[chat_id].is_started:
            await m.reply("You can't change the settings while a game is running!")
            return
        x = (await Chat.get_or_create(id=chat_id))[0]
        keyb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(t("theme"), callback_data="info_theme"),
                    InlineKeyboardButton(t(x.theme), callback_data="theme"),
                ],
                [
                    InlineKeyboardButton(t("seven_zero"), callback_data="info_seven"),
                    InlineKeyboardButton(
                        "✅" if x.seven else "✖️", callback_data="mode_seven"
                    ),
                ],
                [
                    InlineKeyboardButton(t("sbluff"), callback_data="info_bluff"),
                    InlineKeyboardButton(
                        "✅" if x.bluff else "✖️", callback_data="mode_bluff"
                    ),
                ],
                [
                    InlineKeyboardButton(t("one_win"), callback_data="info_one_win"),
                    InlineKeyboardButton(
                        "✅" if x.one_win else "✖️", callback_data="mode_one_win"
                    ),
                ],
                [
                    InlineKeyboardButton(t("one_card"), callback_data="info_one_card"),
                    InlineKeyboardButton(
                        "✅" if x.one_card else "✖️", callback_data="mode_one_card"
                    ),
                ],
                [
                    InlineKeyboardButton(t("language"), callback_data="info_lang"),
                    InlineKeyboardButton(t("lang_flag"), callback_data="lang"),
                ],
            ]
        )
        if isinstance(m, Message):
            await m.reply_text(t("settings"), reply_markup=keyb)
        else:
            await m.edit_message_text(t("settings"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^theme"))
@use_chat_lang()
async def theme(c: Client, cq: CallbackQuery, t):
    if " " in cq.data:
        await Chat.get(id=cq.message.chat.id).update(theme=cq.data.split(" ")[1])
        keyb = InlineKeyboardMarkup(
            [[InlineKeyboardButton(t("back"), callback_data="theme")]]
        )
        await cq.message.edit_text("Theme changed!", reply_markup=keyb)
    else:
        themes = cards.keys()
        tkeyb = [
            InlineKeyboardButton(text=t(theme), callback_data=f"theme {theme}")
            for theme in themes
        ]
        keyb = InlineKeyboardMarkup(
            [tkeyb, [InlineKeyboardButton(text=t("back"), callback_data="settings")]]
        )
        await cq.message.edit_text(t("theme_config"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("mode_"))
@use_chat_lang()
async def mode(c: Client, cq: CallbackQuery, t):
    admin = await c.get_chat_member(cq.message.chat.id, cq.from_user.id)
    if admin.status is ChatMemberStatus.MEMBER:
        await cq.answer("You need to be an admin to change the settings!")
        return
    x = await Chat.get(id=cq.message.chat.id)
    if cq.data == "mode_seven":
        await Chat.get(id=cq.message.chat.id).update(seven=not x.seven)
    elif cq.data == "mode_bluff":
        await Chat.get(id=cq.message.chat.id).update(bluff=not x.bluff)
    elif cq.data == "mode_one_win":
        await Chat.get(id=cq.message.chat.id).update(one_win=not x.one_win)
    elif cq.data == "mode_one_card":
        await Chat.get(id=cq.message.chat.id).update(one_card=not x.one_card)
    await cq.answer("Done!")
    x = await Chat.get(id=cq.message.chat.id)
    keyb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t("theme"), callback_data="info_theme"),
                InlineKeyboardButton(t(x.theme), callback_data="theme"),
            ],
            [
                InlineKeyboardButton(t("seven_zero"), callback_data="info_seven"),
                InlineKeyboardButton(
                    "✅" if x.seven else "✖️", callback_data="mode_seven"
                ),
            ],
            [
                InlineKeyboardButton(t("sbluff"), callback_data="info_bluff"),
                InlineKeyboardButton(
                    "✅" if x.bluff else "✖️", callback_data="mode_bluff"
                ),
            ],
            [
                InlineKeyboardButton(t("one_win"), callback_data="info_one_win"),
                InlineKeyboardButton(
                    "✅" if x.one_win else "✖️", callback_data="mode_one_win"
                ),
            ],
            [
                InlineKeyboardButton(t("one_card"), callback_data="info_one_card"),
                InlineKeyboardButton(
                    "✅" if x.one_card else "✖️", callback_data="mode_one_card"
                ),
            ],
            [
                InlineKeyboardButton(t("language"), callback_data="info_lang"),
                InlineKeyboardButton(t("lang_flag"), callback_data="lang"),
            ],
        ]
    )
    await cq.message.edit_text(t("settings"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^lang"))
@use_chat_lang()
async def lang(c: Client, cq: CallbackQuery, t):
    if cq.message.chat.type != ChatType.PRIVATE:
        admin = await c.get_chat_member(cq.message.chat.id, cq.from_user.id)
        if admin.status is ChatMemberStatus.MEMBER:
            await cq.answer("You need to be an admin to change the theme!")
            return
    if "_" in cq.data:
        nt = partial(get_locale_string, cq.data.split("_")[1])
        if cq.message.chat.type == ChatType.PRIVATE:
            await User.get(id=cq.message.chat.id).update(lang=cq.data.split("_")[1])
        else:
            await Chat.get(id=cq.message.chat.id).update(lang=cq.data.split("_")[1])
        keyb = InlineKeyboardMarkup(
            [[InlineKeyboardButton(nt("back"), callback_data="settings")]]
        )
        await cq.message.edit_text(nt("lang_changed"), reply_markup=keyb)
    else:
        keyb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        get_locale_string(lang, "lang_name"),
                        callback_data=f"lang_{lang}",
                    )
                ]
                for lang in langs
            ]
        )
        await cq.message.edit_text(t("choose_lang"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^info_"))
@use_user_lang()
async def info(c: Client, cq: CallbackQuery, t):
    await cq.answer(t(cq.data), show_alert=True)
