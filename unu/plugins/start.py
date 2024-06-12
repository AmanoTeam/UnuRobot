from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from unu.db import User
from unu.locales import use_user_lang


@Client.on_message(filters.command("start") & filters.private)
@Client.on_callback_query(filters.regex("^start$"))
@use_user_lang()
async def start(c: Client, m: Message | CallbackQuery, t):
    func = m.edit_message_text if isinstance(m, CallbackQuery) else m.reply_text
    await User.get_or_create(id=m.from_user.id)
    print(m.from_user.id)
    keyb = [[(t("help"), "help"), (t("settings_text"), "settings")]]
    await func(t("start_text"), reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex("^help$"))
@use_user_lang()
async def help(c: Client, cq: CallbackQuery, t):
    keyb = [
        [(t("game_mode"), "help_game")],
        [(t("back"), "start")],
    ]
    await cq.edit_message_text("Ecolha uma opção de ajuda abaixo:", reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex("^help_game$"))
@use_user_lang()
async def help_game(c: Client, cq: CallbackQuery, t):
    text = t("game_mode_text")
    text += "<b>" + t("seven_zero") + "</b>: <i>" + t("info_seven") + "</i>\n\n"
    text += "<b>" + t("sbluff") + "</b>: <i>" + t("info_bluff") + "</i>\n\n"
    text += "<b>" + t("one_win") + "</b>: <i>" + t("info_one_win") + "</i>\n\n"
    text += "<b>" + t("one_card") + "</b>: <i>" + t("info_one_card") + "</i>\n\n"
    keyb = [[(t("back"), "help")]]

    await cq.edit_message_text(text, reply_markup=ikb(keyb))


@Client.on_message(filters.command("status"))
@Client.on_callback_query(filters.regex("^status$"))
async def status(c: Client, m: Message | CallbackQuery):
    user = await User.get_or_create(id=m.from_user.id)
    porcentagem = (user[0].wins / user[0].matches) * 100 if user[0].matches > 0 else 0
    if (await User.get(id=m.from_user.id)).placar:
        text = f"{user[0].matches} partidas jogadas\n{user[0].wins} vezes em primeiro lugas ({porcentagem}%)\n{user[0].cards} cartas jogadas"
    else:
        text = "Ligue para saber suas estatísticas como quantas partidas jogadas, quantas vezes em primeiro lugar e quantas cartas jogadas"
    if isinstance(m, Message):
        await m.reply_text(text)
    else:
        await m.answer(text, show_alert=True)


@Client.on_callback_query(filters.regex("^ch_status$"))
async def ch_status(c: Client, cq: CallbackQuery):
    user = await User.get_or_create(id=cq.from_user.id)
    user = user[0]
    user.placar = not user.placar
    await user.save()
    await cq.answer("Status alterado com sucesso")
