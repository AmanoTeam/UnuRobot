from asyncio import sleep
from json import dump
from pathlib import Path

from hydrogram import Client, filters
from hydrogram.errors import ListenerTimeout, MediaEmpty
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultCachedSticker,
    Message,
)

from config import sudoers
from unu.card import cards
from unu.db import User
from unu.locales import use_user_lang
from unu.utils import filter_sudoers


@Client.on_message(filters.command("sudos") & filters.private & filter_sudoers)
@Client.on_callback_query(filters.regex("^sudos$") & filter_sudoers)
@use_user_lang()
async def start(c: Client, m: Message | CallbackQuery, t):
    func = m.edit_message_text if isinstance(m, CallbackQuery) else m.reply_text
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("tudos"), callback_data="settings_sudos"),
            InlineKeyboardButton(t("theme"), callback_data="settings_sudo_themc"),
        ],
        [
            InlineKeyboardButton(t("back"), callback_data="settings"),
        ],
    ])
    await func(
        t("sudo_menu"),
        reply_markup=keyb,
    )


@Client.on_callback_query(filters.regex("^settings_sudos$") & filter_sudoers)
@use_user_lang()
async def settings_sudos(c: Client, cq: CallbackQuery, t):
    usrs = await c.get_users(sudoers)
    db_usrs = await User.filter(sudo=True)
    usrs += await c.get_users([usr.id for usr in db_usrs])
    text = t("sudoers")
    for usr in usrs:
        text += f"👤 {usr.mention}\n"

    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("add_sudo"), callback_data="settings_sudos_add"),
            InlineKeyboardButton(t("rm_sudo"), callback_data="settings_sudos_remove"),
        ],
        [InlineKeyboardButton(t("back"), callback_data="sudos")],
    ])

    await cq.edit_message_text(text, reply_markup=keyb)


@Client.on_callback_query(filters.regex("^settings_sudos_add$") & filter_sudoers)
@use_user_lang()
async def settings_sudos_add(c: Client, cq: CallbackQuery, t):
    await cq.edit_message_text(t("send_user_id"))
    cmessage = None
    # Wait for the user to send a message with the new emoji
    try:
        while cmessage is None:
            cmessage = await cq.message.chat.listen(filters.text)
            print(cmessage)
    except ListenerTimeout:
        return

    text = cmessage.text
    user = await c.get_users(text)

    if not user:
        await cmessage.reply_text(t("user_not_found"))
        return

    user_db = await User.get_or_create(id=user.id)

    if user_db[0].sudo:
        await cmessage.reply_text(t("user_sudoer").format(user=user.mention))
        return

    user_db[0].sudo = True
    await user_db[0].save()

    await cmessage.reply_text(
        t("user_added").format(user=user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Voltar", callback_data="settings_sudos")]
        ]),
    )


@Client.on_callback_query(filters.regex("^settings_sudos_remove") & filter_sudoers)
@use_user_lang()
async def settings_sudos_remove(c: Client, cq: CallbackQuery, t):
    if cq.data == "settings_sudos_remove":
        db_users = await User.filter(sudo=True)
        users = await c.get_users([usr.id for usr in db_users])
        text = t("select_user")
        keyb = [
            [
                InlineKeyboardButton(
                    user.first_name,
                    callback_data=f"settings_sudos_remove_{user.id}",
                )
            ]
            for user in users
        ]

        keyb.append([InlineKeyboardButton(t("back"), callback_data="settings_sudos")])
        await cq.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyb))
        return

    db_users = await User.filter(sudo=True)
    sudoers = [usr.id for usr in db_users]

    user_id = int(cq.data.split("_")[3])
    user = await c.get_users(user_id)
    if user_id not in sudoers:
        await cq.answer(t("user_not_sudoer").format(user=user.mention))
        return

    await User.get(id=user_id).update(sudo=False)

    await cq.edit_message_text(
        t("user_removed").format(user=user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Voltar", callback_data="settings_sudos")]
        ]),
    )


@Client.on_callback_query(filters.regex("^settings_sudo_themc$") & filter_sudoers)
@use_user_lang()
async def settings_sudo_themc(c: Client, cq: CallbackQuery, t):
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text=theme, callback_data=f"settings_sudo_themc {theme}")
            for theme in cards
        ],
        [
            InlineKeyboardButton(t("add_theme"), callback_data="settings_sudo_themc_new"),
            InlineKeyboardButton(t("theme"), callback_data="sudos"),
        ],
    ])
    await cq.edit_message_text(t("theme_config"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^settings_sudo_themc_new$") & filter_sudoers)
@use_user_lang()
async def settings_themes_new(c: Client, cq: CallbackQuery, t):
    await cq.edit_message_text(t("send_theme_name"))
    cmessage = None
    # Wait for the user to send a message with the new emoji
    try:
        while cmessage is None:
            cmessage = await cq.message.chat.listen(filters.text)
            print(cmessage)
    except ListenerTimeout:
        return

    name = cmessage.text

    ncards = cards["classic"]

    for card in ncards["STICKERS"]:
        await c.send_message(cq.message.chat.id, t("send_sticker"))
        await c.send_sticker(cq.message.chat.id, ncards["STICKERS"][card])

        cmessage = None
        # Wait for the user to send a message with the new emoji
        try:
            while cmessage is None:
                cmessage = await cq.message.chat.listen(filters.sticker)
                ncards["STICKERS"][card] = cmessage.sticker.file_id
        except ListenerTimeout:
            return
    for card in ncards["STICKERS_GREY"]:
        await c.send_message(cq.message.chat.id, t("send_sticker"))
        await c.send_sticker(cq.message.chat.id, ncards["STICKERS_GREY"][card])

        cmessage = None
        # Wait for the user to send a message with the new emoji
        try:
            while cmessage is None:
                cmessage = await cq.message.chat.listen(filters.sticker)
                ncards["STICKERS_GREY"][card] = cmessage.sticker.file_id
        except ListenerTimeout:
            return

    with Path(f"cards/{name}.json").open(mode="w", encoding="locale") as f:
        dump(ncards, f)

    await c.send_message(
        cq.message.chat.id,
        t("theme_added").format(name=name),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Voltar", callback_data="settings_sudo_themc")]
        ]),
    )


@Client.on_callback_query(filters.regex("^settings_sudo_themc ") & filter_sudoers)
@use_user_lang()
async def settings_themes(c: Client, cq: CallbackQuery, t):
    theme = cq.data.split(" ")[1]
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("add_card"), callback_data="settings_sudo_themc_add " + theme),
            InlineKeyboardButton(
                t("update_card"), callback_data="settings_sudo_themc_update " + theme
            ),
            InlineKeyboardButton(
                t("verify_card"), callback_data="settings_sudo_themc_check " + theme
            ),
        ],
        [InlineKeyboardButton("Voltar", callback_data="settings_sudo_themc")],
    ])
    await cq.edit_message_text(t("sudo_theme").format(theme=theme), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^settings_sudo_themc_add ") & filter_sudoers)
@use_user_lang()
async def settings_themes_add(c: Client, cq: CallbackQuery, t):
    theme = cq.data.split(" ")[1]
    await cq.edit_message_text(t("send_card_code"))

    cmessage = None

    try:
        while cmessage is None:
            cmessage = await cq.message.chat.listen(filters.text)
    except ListenerTimeout:
        return

    code = cmessage.text

    await c.send_message(cq.message.chat.id, t("send_colored_card").format(code=code))

    cmessage = None

    try:
        while cmessage is None:
            cmessage = await cq.message.chat.listen(filters.sticker)
    except ListenerTimeout:
        return

    stickerc = cmessage.sticker.file_id

    await c.send_message(cq.message.chat.id, t("send_grey_card").format(code=code))

    cmessage = None

    try:
        while cmessage is None:
            cmessage = await cq.message.chat.listen(filters.sticker)
    except ListenerTimeout:
        return

    stickerg = cmessage.sticker.file_id

    cards[theme]["STICKERS"][code] = stickerc
    cards[theme]["STICKERS_GREY"][code] = stickerg

    with Path(f"cards/{theme}.json").open(mode="w", encoding="locale") as f:
        dump(cards[theme], f)

    await c.send_message(
        cq.message.chat.id,
        t("card_added").format(code=code),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(t("back"), callback_data="settings_sudo_themc")]
        ]),
    )


@Client.on_callback_query(filters.regex("^settings_sudo_themc_update ") & filter_sudoers)
@use_user_lang()
async def settings_themes_update(c: Client, cq: CallbackQuery, t):
    sp = cq.data.split(" ")[1:]
    print(sp)
    theme = sp[0]
    if len(sp) == 1:
        keyb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t("light"),
                    callback_data=f"settings_sudo_themc_update {theme} Light",
                ),
                InlineKeyboardButton(
                    t("dark"),
                    callback_data=f"settings_sudo_themc_update {theme} Dark",
                ),
            ],
        ])
        await cq.edit_message_text(t("theme_config"), reply_markup=keyb)
    if len(sp) == 2:
        keyb = []
        for color in cards[theme]["CARDS"]["COLORS"]:
            keyb.append(
                InlineKeyboardButton(
                    color,
                    callback_data=f"settings_sudo_themc_update {theme} {sp[1]} {color}",
                )
            )
        keyb.append(
            InlineKeyboardButton(
                "SPECIALS",
                callback_data=f"settings_sudo_themc_update {theme} {sp[1]} SPECIALS",
            )
        )
        await cq.edit_message_text(
            "Escolha a cor da carta que deseja atualizar",
            reply_markup=InlineKeyboardMarkup([keyb]),
        )
    elif len(sp) == 3:
        keyb = []
        if sp[2] == "SPECIALS":
            for card in cards[theme]["CARDS"]["SPECIALS"]:
                keyb.append([
                    InlineKeyboardButton(
                        card,
                        callback_data=f"settings_sudo_themc_update {theme} {sp[1]} x {card}",
                    )
                ])
        else:
            for card in cards[theme]["CARDS"]["VALUES"]:
                keyb.append([
                    InlineKeyboardButton(
                        card,
                        callback_data=f"settings_sudo_themc_update {theme} {sp[1]} {sp[2]} {card}",
                    )
                ])
        await cq.edit_message_text(
            "Escolha o valor da carta que deseja atualizar",
            reply_markup=InlineKeyboardMarkup(keyb),
        )
    elif len(sp) == 4:
        await cq.edit_message_text("Envie um sticker para substituir a carta:")
        cardid = sp[2] + "_" + sp[3] if sp[2] != "x" else sp[3]
        cardtm = "STICKERS_GREY" if sp[1] == "Dark" else "STICKERS"
        await c.send_sticker(cq.message.chat.id, cards[theme][cardtm][cardid])

        cmessage = None

        try:
            while cmessage is None:
                cmessage = await cq.message.chat.listen(filters.sticker)
        except ListenerTimeout:
            return

        cards[theme][cardtm][cardid] = cmessage.sticker.file_id

        with Path(f"cards/{theme}.json").open(mode="w", encoding="locale") as f:
            dump(cards[theme], f)

        await c.send_message(
            cq.message.chat.id,
            "Carta atualizada com sucesso!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Voltar", callback_data="settings_sudo_themc")]
            ]),
        )


@Client.on_callback_query(filters.regex("^settings_sudo_themc_check ") & filter_sudoers)
async def settings_themes_check(c: Client, cq: CallbackQuery):
    theme = cq.data.split(" ")[1]
    card_types = ["STICKERS", "STICKERS_GREY"]
    messages = ["Verificando cartas coloridas...", "Verificando cartas cinzas..."]

    for card_type, message in zip(card_types, messages):
        await c.send_message(cq.message.chat.id, message)
        for card in cards[theme][card_type]:
            try:
                m2 = await c.send_sticker(cq.message.chat.id, cards[theme][card_type][card])
                await m2.delete()
                await sleep(0.3)
            except MediaEmpty:
                await c.send_message(
                    cq.message.chat.id,
                    f"Carta {card} não encontrada, mande a carta para substitui-lá",
                )

                while True:
                    try:
                        cmessage = await cq.message.chat.listen(filters.sticker)
                        break
                    except ListenerTimeout:
                        return

                cards[theme][card_type][card] = cmessage.sticker.file_id
                await c.send_message(cq.message.chat.id, f"Carta {card} atualizada com sucesso!")

    with Path(f"cards/{theme}.json").open(mode="w", encoding="locale") as f:
        dump(cards[theme], f)

    await c.send_message(cq.message.chat.id, "Cartas verificadas com sucesso!")


@Client.on_inline_query(filters.regex("^change ") & filter_sudoers)
async def change(c: Client, iq: InlineQuery):
    theme = iq.query.split(" ")[1]
    articles = []
    for card in cards[theme]["STICKERS"]:
        articles.append(
            InlineQueryResultCachedSticker(
                id="sudo" + card, sticker_file_id=cards[theme]["STICKERS"][card]
            )
        )
    for card in cards[theme]["STICKERS_GREY"]:
        articles.append(
            InlineQueryResultCachedSticker(
                id="sudog" + card, sticker_file_id=cards[theme]["STICKERS_GREY"][card]
            )
        )
    return await iq.answer(articles, cache_time=0)
