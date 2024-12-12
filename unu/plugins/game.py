import importlib
import re

from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.errors import ListenerTimeout
from hydrogram.types import (
    CallbackQuery,
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
    Message,
)

from config import games, minimum_players, player_game
from unu.card import COLORS, cards
from unu.db import Chat, User
from unu.game import Game
from unu.locales import use_lang
from unu.utils import filter_sudoers


@Client.on_message(filters.command("new"))
@Client.on_message(filters.command("new_dev") & filter_sudoers)
@use_lang()
async def new_game(c: Client, m: Message, ut, ct):
    chat = await Chat.get_or_create(id=m.chat.id)
    if m.chat.id in games or m.chat.type == ChatType.PRIVATE or player_game.get(m.from_user.id):
        return await m.reply_text(
            ut("game_existis")
            if m.chat.id in games
            else ut("only_group")
            if m.chat.type == ChatType.PRIVATE
            else ut("already_in_game") + str(player_game.get(m.from_user.id).chat.title)
        )

    game = Game(m.chat, (await Chat.get(id=m.chat.id)).theme)
    if m.command[0] == "new_dev":
        game.is_dev = True
    game.players[m.from_user.id] = m.from_user
    games[m.chat.id] = game
    player_game[m.from_user.id] = game
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(ct("join"), callback_data="join_game"),
            InlineKeyboardButton(ct("leave"), callback_data="leave_game"),
        ],
        [InlineKeyboardButton(ct("start_game"), callback_data="start_game")],
    ])
    text = ct("game_started")
    if game.is_dev:
        text += ct("dev_mode")
    game.message = await m.reply_text(text, reply_markup=keyb)
    if chat[0].auto_pin:
        await game.message.pin()
    return None


@Client.on_message(filters.command("add_card"))
@use_lang()
async def add_card(c: Client, m: Message, ut, ct):
    # /add_card <player_or_none> <card>
    game: Game = games.get(m.chat.id)
    if not game:
        return await m.reply_text(ut("no_game") if not game else ut("not_allowed"))
    elif not game.is_dev:
        return await m.reply_text(ut("not_allowed"))
    text = m.text.split(" ", 1)
    text = text[1].split(" ", 1)
    if len(text) != 1:
        playerid = await c.get_users(text[0])
        if not playerid:
            return await m.reply_text(ut("invalid_player"))
        playerid = playerid.id
        card = text[1].split("_", 1)
    else:
        playerid = m.from_user.id
        card = text[0].split("_", 1)
    if playerid not in game.players:
        return await m.reply_text(ut("player_not_in_game"))
    if len(card) != 2:
        return await m.reply_text(ut("invalid_card"))
    game.players[playerid].cards.append(tuple(card))

    theme = (await Chat.get(id=m.chat.id)).theme
    color_icons = cards[theme]["CARDS"]["COLOR_ICONS"]
    values_icons = cards[theme]["CARDS"]["VALUES_ICONS"]

    return await m.reply_text(
        ct("card_added").format(code=f"{color_icons[card[0]]}{values_icons[card[1]]}")
    )


@Client.on_message(filters.command("remove_card"))
@use_lang()
async def remove_card(c: Client, m: Message, ut, ct):
    # /remove_card <player_or_none> <card>
    game: Game = games.get(m.chat.id)
    if not game:
        return await m.reply_text(ut("no_game") if not game else ut("not_allowed"))
    elif not game.is_dev:
        return await m.reply_text(ut("not_allowed"))
    text = m.text.split(" ", 1)
    text = text[1].split(" ", 1)
    if len(text) != 1:
        playerid = await c.get_users(text[0])
        if not playerid:
            return await m.reply_text(ut("invalid_player"))
        playerid = playerid.id
        card = text[1].split("_", 1)
    else:
        playerid = m.from_user.id
        card = text[0].split("_", 1)
    if playerid not in game.players:
        return await m.reply_text(ut("player_not_in_game"))
    if len(card) != 2:
        return await m.reply_text(ut("invalid_card"))
    print(tuple(card))
    print(game.players[playerid].cards)
    game.players[playerid].cards.remove(tuple(card))
    game.deck.cards.append(tuple(card))

    theme = (await Chat.get(id=m.chat.id)).theme
    color_icons = cards[theme]["CARDS"]["COLOR_ICONS"]
    values_icons = cards[theme]["CARDS"]["VALUES_ICONS"]

    return await m.reply_text(
        ct("card_removed").format(code=f"{color_icons[card[0]]}{values_icons[card[1]]}")
    )


@Client.on_message(filters.command("join"))
@Client.on_callback_query(filters.regex("^join_game$"))
@use_lang()
async def join_game(c: Client, m: Message | CallbackQuery, ut, ct):
    func = m.answer if isinstance(m, CallbackQuery) else m.reply_text
    game: Game = games.get(m.chat.id if isinstance(m, Message) else m.message.chat.id)
    if not game or m.from_user.id in game.players or player_game.get(m.from_user.id):
        return await func(
            ut("no_game")
            if not game
            else ut("already_joined")
            if m.from_user.id in game.players
            else ut("already_in_game") + str(player_game.get(m.from_user.id).chat.title)
        )
    if game.closed:
        return await func(ct("lobby_closed"))

    game.players[m.from_user.id] = m.from_user
    player_game[m.from_user.id] = game
    await func(ut("joined_game"))
    if isinstance(m, CallbackQuery):
        await c.send_message(
            m.message.chat.id, ct("player_joined").format(name=m.from_user.mention)
        )

    if game.is_started:
        game.players[m.from_user.id].cards = game.deck.draw(7)
        game.players[m.from_user.id].total_cards = 0
        return None
    return None


@Client.on_callback_query(filters.regex("^leave_game$"))
@Client.on_message(filters.command("leave"))
@use_lang()
async def leave_game(c: Client, m: Message | CallbackQuery, ut, ct):
    func = m.answer if isinstance(m, CallbackQuery) else m.reply_text
    game: Game = games.get(m.chat.id if isinstance(m, Message) else m.message.chat.id)
    if not game or m.from_user.id not in game.players:
        return await func(ut("no_game") if not game else ut("no_joinned"))

    if game.is_started and game.next_player.id == m.from_user.id:
        inline_keyb = InlineKeyboardMarkup([
            [InlineKeyboardButton(ct("play"), switch_inline_query_current_chat="")]
        ])
        game.next()
        await c.send_message(
            game.chat.id,
            ct("next").format(name=game.next_player.mention),
            reply_markup=inline_keyb,
        )
    del game.players[m.from_user.id]
    del player_game[m.from_user.id]
    chat_id = m.chat.id if isinstance(m, Message) else m.message.chat.id

    if len(game.players) < minimum_players:
        for player in game.players:
            player_game.pop(player)
        games.pop(m.chat.id if isinstance(m, Message) else m.message.chat.id)
        if isinstance(m, CallbackQuery):
            await c.send_message(
                chat_id=chat_id,
                text=ct("player_left").format(name=m.from_user.mention) + ", " + ct("game_over"),
            )
            game.stop()
            await game.message.edit_text(ut("game_over"))
            if (await Chat.get(id=chat_id)).auto_pin:
                await game.message.unpin()
        return await func(ut("game_over"))
    if isinstance(m, CallbackQuery):
        await c.send_message(
            chat_id=chat_id, text=ct("player_left").format(name=m.from_user.mention)
        )
    return await func(ut("left_game"))


@Client.on_message(filters.command("close"))
@Client.on_callback_query(filters.regex("^close_game$"))
@use_lang()
async def close_game(c: Client, m: Message | CallbackQuery, ut, ct):
    if isinstance(m, CallbackQuery):
        func = m.answer
        chat = m.message.chat
    else:
        func = m.reply_text
        chat = m.chat
    game = games.get(chat.id)
    if not game:
        return await func(ut("no_game") if not game else ut("not_allowed"))

    game.closed = True
    if isinstance(m, CallbackQuery):
        keyb = InlineKeyboardMarkup([
            [InlineKeyboardButton(ct("open"), callback_data="open_game")]
        ])
        await m.message.edit_reply_markup(keyb)
    return await func(ct("lobby_closed"))


@Client.on_message(filters.command("open"))
@Client.on_callback_query(filters.regex("^open_game$"))
@use_lang()
async def open_game(c: Client, m: Message, ut, ct):
    if isinstance(m, CallbackQuery):
        func = m.answer
        chat = m.message.chat
    else:
        func = m.reply_text
        chat = m.chat
    game = games.get(chat.id)
    if not game:
        return await func(ut("no_game") if not game else ut("not_allowed"))

    game.closed = False
    if isinstance(m, CallbackQuery):
        keyb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(ct("join"), callback_data="join_game"),
                InlineKeyboardButton(ct("leave"), callback_data="leave_game"),
            ],
            [
                InlineKeyboardButton(ct("close_lobby"), callback_data="close_game"),
            ],
        ])
        await m.message.edit_reply_markup(keyb)
    return await func(ct("lobby_opened"))


@Client.on_message(filters.command("kill"))
@use_lang()
async def kill_game(c: Client, m: Message, ut, ct):
    game: Game = games.get(m.chat.id)
    if not game:
        return await m.reply_text(ut("no_game") if not game else ut("not_allowed"))

    games.pop(m.chat.id)
    for player in game.players:
        player_game.pop(player)
    game.stop()
    await game.message.edit_text(ct("game_over"))
    if (await Chat.get(id=m.chat.id)).auto_pin:
        await game.message.unpin()
    return await m.reply_text(ct("game_over"))


@Client.on_message(filters.command("start") & ~filters.private)
@Client.on_callback_query(filters.regex("^start_game$"))
@use_lang()
async def start_game(c: Client, m: Message | CallbackQuery, ut, ct):
    if isinstance(m, CallbackQuery):
        func = m.answer
        chat_id = m.message.chat.id
    else:
        func = m.reply_text
        chat_id = m.chat.id
    config = await Chat.get(id=chat_id)
    theme = config.theme
    game: Game = games.get(chat_id)
    if not game:
        return await func(ut("no_game") if not game else ut("not_allowed"))

    if len(game.players) < minimum_players:
        return await func(ut("minimum_players").format(minimum_players))

    game.start()
    game.deck.shuffle()
    for player in game.players.values():
        player.cards = game.deck.draw(7)
        player.total_cards = 0
    keyb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(ct("join"), callback_data="join_game"),
            InlineKeyboardButton(ct("leave"), callback_data="leave_game"),
        ],
        [
            InlineKeyboardButton(ct("close_lobby"), callback_data="close_game"),
        ],
    ])
    await c.send_message(chat_id=chat_id, text=ct("game_started"))
    await game.message.edit_text(ct("game_started"), reply_markup=keyb)
    pcard = next(
        (
            lcard
            for lcard in game.deck.cards
            if lcard[1] not in cards[config.theme]["CARDS"]["SPECIALS"]
        ),
        None,
    )
    game.deck.cards.remove(pcard)
    game.deck.cards.append(pcard)
    if pcard[1] == "draw":
        game.draw += 2
    await c.send_sticker(
        chat_id=chat_id, sticker=cards[theme]["STICKERS"][f"{pcard[0]}_{pcard[1]}"]
    )
    game.last_card = pcard
    game.next_player = next(iter(game.players.values()))
    inline_keyb = InlineKeyboardMarkup([
        [InlineKeyboardButton(ct("play"), switch_inline_query_current_chat="")]
    ])
    return await c.send_message(
        chat_id,
        ct("next").format(name=game.next_player.mention),
        reply_markup=inline_keyb,
    )


@Client.on_inline_query(group=3)
@use_lang()
async def inline_query(c: Client, m: InlineQuery, ut, ct):
    game: Game = player_game.get(m.from_user.id)
    if not game:
        articles = [
            InlineQueryResultArticle(
                id="none",
                title=ut("no_game"),
                input_message_content=InputTextMessageContent(ut("no_game_text")),
            )
        ]
        return await m.answer(articles, cache_time=0)

    config = await Chat.get(id=game.chat.id)
    theme = config.theme
    color_icons = cards[theme]["CARDS"]["COLOR_ICONS"]
    values_icons = cards[theme]["CARDS"]["VALUES_ICONS"]

    info_text = ut("info_text").format(
        current_player=game.next_player.mention,
        last_card=color_icons[game.last_card[0]] + values_icons[game.last_card[1]],
    )
    for fplayer in game.players:
        info_text += ut("info_text2").format(
            player=game.players[fplayer].mention, cards=len(game.players[fplayer].cards)
        )

    if game.chosen == "color" and game.next_player.id == m.from_user.id:
        pre = ""
        if game.last_card[1] in cards[theme]["CARDS"]["THEME_CARDS"]:
            pre = f"{game.last_card[1]}-"
        articles = [
            InlineQueryResultArticle(
                id=pre + color,
                title=color_icons[color],
                input_message_content=InputTextMessageContent(
                    ct("colorchoosed").format(color=color_icons[color])
                ),
            )
            for color in COLORS
        ]
        if len(game.players[m.from_user.id].cards) != 0:
            text_cards = ""
            for card in game.players[m.from_user.id].cards:
                text_cards += f"{color_icons[card[0]]}{values_icons[card[1]]}, "

            articles.append(
                InlineQueryResultArticle(
                    id="info-",
                    title=text_cards,
                    input_message_content=InputTextMessageContent(info_text),
                )
            )
        await m.answer(articles, cache_time=0)
        return None
    if game.chosen == "player" and game.next_player.id == m.from_user.id:
        players = list(game.players.keys())
        if len(players) != 1:
            players.remove(m.from_user.id)
        articles = []
        pre = ""
        if game.last_card[1] in cards[theme]["CARDS"]["THEME_CARDS"]:
            pre = f"{game.last_card[1]}-"
        for player in players:
            if len(players) == 1 or player != m.from_user.id:
                articles.append(
                    InlineQueryResultArticle(
                        id=pre + str(player),
                        title=game.players[player].first_name,
                        input_message_content=InputTextMessageContent(
                            game.players[player].mention
                        ),
                    )
                )
        await m.answer(articles, cache_time=0)
        return None

    if not game or m.from_user.id != game.next_player.id:
        articles = []
        for num, pcard in enumerate(game.players[m.from_user.id].cards):
            sticker_type = pcard[1] if pcard[0] == "x" else f"{pcard[0]}_{pcard[1]}"
            articles += [
                InlineQueryResultCachedSticker(
                    id=f"info-{num}",
                    sticker_file_id=cards[theme]["STICKERS_GREY"][sticker_type],
                    input_message_content=InputTextMessageContent(info_text),
                )
            ]

        return await m.answer(articles, cache_time=0, is_gallery=True)

    gcards = game.players[m.from_user.id].cards
    lcard = game.last_card if game.draw < 2 else ("p", "draw")
    xcard = f"{lcard[0]}_{lcard[1]}"
    sticker_id = "option_pass" if game.drawed else "option_draw"
    sticker_text = (
        ut("pass")
        if game.drawed
        else ut("buy").format(number=1)
        if game.draw == 0
        else ut("buy").format(number=game.draw)
    )
    articles = [
        InlineQueryResultCachedSticker(
            id=sticker_id,
            sticker_file_id=cards[theme]["STICKERS"][sticker_id],
            input_message_content=InputTextMessageContent(sticker_text),
        )
    ]
    print(game.bluff)
    if game.bluff and (await Chat.get(id=game.chat.id)).bluff:
        articles.append(
            InlineQueryResultCachedSticker(
                id="option_bluff",
                sticker_file_id=cards[theme]["STICKERS"]["option_bluff"],
                input_message_content=InputTextMessageContent(ut("bluff")),
            )
        )

    for num, pcard in enumerate(gcards):
        sticker_type = pcard[1] if pcard[0] == "x" else f"{pcard[0]}_{pcard[1]}"
        stack = ("draw" in str(pcard[1]) and game.draw >= 2) and not (
            await Chat.get(id=game.chat.id)
        ).satack
        if (
            (
                pcard[1] in cards[theme]["CARDS"]["SPECIALS_INFO"]
                and re.search(cards[theme]["CARDS"]["SPECIALS_INFO"][pcard[1]][1], string=xcard)
                and not stack
            )
            or (pcard[0] == lcard[0] or pcard[1] == lcard[1])
            and not stack
        ):
            articles.append(
                InlineQueryResultCachedSticker(
                    id=f"{pcard[0]}-{pcard[1]}-{num}",
                    sticker_file_id=cards[theme]["STICKERS"][sticker_type],
                )
            )
        else:
            articles.append(
                InlineQueryResultCachedSticker(
                    id=f"info-{num}",
                    sticker_file_id=cards[theme]["STICKERS_GREY"][sticker_type],
                    input_message_content=InputTextMessageContent(info_text),
                )
            )

    await m.answer(articles, cache_time=0, is_gallery=True)
    return None


@Client.on_chosen_inline_result(group=1)
@use_lang()
async def choosen(c: Client, ir: ChosenInlineResult, ut, ct):
    game: Game = player_game.get(ir.from_user.id)
    if not game and game.next_player.id != ir.from_user.id:
        return None

    config = await Chat.get(id=game.chat.id)
    pcard = ir.result_id.split("-")[:2]
    ncard = ir.result_id.split("-")[2] if len(ir.result_id.split("-")) > 2 else None
    lcard = game.last_card if game.draw <= 1 else ("y", "draw")
    inline_keyb = InlineKeyboardMarkup([
        [InlineKeyboardButton(ct("play"), switch_inline_query_current_chat="")]
    ])
    if pcard[0] == "info":
        return None
    print(pcard)
    print(lcard)
    config = await Chat.get(id=game.chat.id)
    theme = config.theme
    if game.chosen == "color":
        game.last_card = (ir.result_id, game.last_card[1])
        game.chosen = None
        if not await verify_cards(game, c, ir, game.players[ir.from_user.id], ut, ct):
            if game.last_card[1] == "buycolor":
                game.chosen = "player"
                return await c.send_message(
                    game.chat.id,
                    ct("playerchoose").format(name=game.next_player.mention),
                    reply_markup=inline_keyb,
                )
            elif not (theme == "nomercy" and game.last_card[1] == "draw_four"):
                game.next()
            return await c.send_message(
                game.chat.id,
                ct("next").format(name=game.next_player.mention),
                reply_markup=inline_keyb,
            )
    elif game.chosen == "player" and lcard[1] == "7":
        game.players[ir.from_user.id].cards, game.players[int(pcard[0])].cards = (
            game.players[int(pcard[0])].cards,
            game.players[ir.from_user.id].cards,
        )
        game.chosen = None
        await c.send_message(
            game.chat.id,
            ct("cards_swapped").format(
                name1=game.next_player.mention,
                name2=game.players[int(pcard[0])].mention,
            ),
        )
        game.next()
        pcard.append("player")
        await verify_cards(game, c, ir, game.players[int(pcard[0])], ut, ct)
        await verify_cards(game, c, ir, game.players[ir.from_user.id], ut, ct)
        return await c.send_message(
            game.chat.id,
            ct("next").format(name=game.next_player.mention),
            reply_markup=inline_keyb,
        )
    elif game.chosen == "player" and lcard[1] == "buycolor":
        # o player escolhido irá comprar cartas até que a carta seja da cor escolhida
        game.chosen = None
        player = game.players[int(pcard[0])]
        buy = 0
        ncards = []
        while True:
            card = game.deck.draw(1)[0]
            player.cards.extend([card])
            ncards.append(card)
            buy += 1
            if card[0] == game.last_card[0]:
                break

        config = await Chat.get(id=game.chat.id)
        theme = config.theme

        color_icons = cards[theme]["CARDS"]["COLOR_ICONS"]
        values_icons = cards[theme]["CARDS"]["VALUES_ICONS"]
        await c.send_message(
            game.chat.id,
            ct("pbought").format(name=player.mention, number=len(ncards))
            + f"\n{', '.join([f'{color_icons[card[0]]}{values_icons[card[1]]}' for card in ncards])}",
        )
    elif pcard[0] == "option_draw":
        buy = game.draw if game.draw > 0 else 1
        config = await Chat.get(id=game.chat.id)
        print(config.draw_one, buy)
        if not config.draw_one and buy == 1:
            # comprar até a ultima carta comprada pode ser jogada
            while True:
                card = game.deck.draw(1)[0]
                print(card)
                game.players[ir.from_user.id].cards.extend([card])
                if (
                    card[1] == lcard[1]
                    or card[0] == lcard[0]
                    or ("draw" in card[1] and "draw" in lcard[1])
                ):
                    break
                buy += 1
        else:
            game.players[ir.from_user.id].cards.extend(game.deck.draw(buy))
        await c.send_message(game.chat.id, ct("bought").format(number=buy))
        if len(game.players) != 1 and game.draw == 0:
            game.drawed = True
            return await c.send_message(
                game.chat.id,
                ct("next").format(name=game.next_player.mention),
                reply_markup=inline_keyb,
            )
        game.draw = 0
    elif pcard[0] == "option_pass":
        game.draw = 0
    elif pcard[0] == "option_bluff":
        game.bluff = False
        lplayer = game.players[game.last_card_2["player"]]
        bcard = game.last_card_2["card"]
        if any(bcard[0] in tupla or bcard[1] in tupla for tupla in lplayer.cards):
            lplayer.cards.extend(game.deck.draw(game.draw))
            await c.send_message(
                game.chat.id,
                ct("bluffed").format(name=lplayer.mention, draw=game.draw),
            )
            game.draw = 0
            if not await verify_cards(game, c, ir, lplayer, ut, ct):
                await c.send_message(
                    game.chat.id,
                    ct("next").format(name=game.next_player.mention),
                    reply_markup=inline_keyb,
                )
            return None
        game.players[ir.from_user.id].cards.extend(game.deck.draw(game.draw + 2))
        await c.send_message(
            game.chat.id,
            ct("not_bluffed").format(
                name1=lplayer.mention,
                name2=ir.from_user.mention,
                draw=game.draw + 2,
            ),
        )
        game.draw = 0
        game.next()
        if not (await verify_cards(game, c, ir, game.players[ir.from_user.id], ut, ct)):
            await c.send_message(
                game.chat.id,
                ct("next").format(name=game.next_player.mention),
                reply_markup=inline_keyb,
            )
        return None
    elif pcard[0] == "x" and pcard[1] in {
        "colorchooser",
        "draw_four",
        "draw_six",
        "draw_ten",
        "buycolor",
    }:
        game.players[ir.from_user.id].total_cards += 1
        if pcard[1] == "draw_four":
            if theme == "nomercy":
                # aqui ele inverte a lista de jogadores mas mantem o jogador atual
                game.players = {k: game.players[k] for k in reversed(list(game.players.keys()))}
            game.bluff = True
            game.draw += 4
        elif pcard[1] == "draw_six":
            game.bluff = True
            game.draw += 6
        elif pcard[1] == "draw_ten":
            game.bluff = True
            game.draw += 10
        game.last_card_2 = {"card": game.last_card, "player": ir.from_user.id}
        game.last_card = game.players[ir.from_user.id].cards.pop(int(ncard))
        game.deck.cards.append(game.last_card)
        game.chosen = "color"
        return await c.send_message(
            game.chat.id,
            ct("colorchoose").format(name=game.next_player.mention),
            reply_markup=inline_keyb,
        )
    elif pcard[0] in cards[config.theme]["CARDS"]["THEME_CARDS"] or (
        pcard[1] and pcard[1] in cards[config.theme]["CARDS"]["THEME_CARDS"]
    ):
        game.deck.cards.append(game.last_card)
        module = importlib.import_module(f"unu.special_cards.{config.theme}")
        function = getattr(
            module,
            pcard[1] if pcard[1] in cards[config.theme]["CARDS"]["THEME_CARDS"] else pcard[0],
        )
        ret = await function(c, ir, game)
        if ret:
            return None
    elif pcard[0] != "x" and (
        pcard[1] == lcard[1] or pcard[0] == lcard[0] or ("draw" in lcard[1] and "draw" in pcard[1])
    ):
        game.players[ir.from_user.id].total_cards += 1
        game.draw += 2 if pcard[1] == "draw" else +4 if pcard[1] == "draw_four" else 0
        game.last_card_2 = {"card": game.last_card, "player": ir.from_user.id}
        game.last_card = game.players[ir.from_user.id].cards.pop(int(ncard))
        game.deck.cards.append(game.last_card)
        if pcard[1] == "reverse":
            game.players = {k: game.players[k] for k in reversed(list(game.players.keys()))}
            game.next() if len(game.players) == 2 else None
        elif pcard[1] == "skip":
            game.next()
        elif pcard[1] == "discart_all":
            # Aqui irá descartar todas as cartas do jogador que seja da mesma cor que o da carta jogada
            dcards = []
            for card in game.players[ir.from_user.id].cards[:]:
                if card[0] == game.last_card[0]:
                    dcards.append(card)
                    game.players[ir.from_user.id].cards.remove(card)
                    game.deck.cards.append(card)

            color_icons = cards[theme]["CARDS"]["COLOR_ICONS"]
            values_icons = cards[theme]["CARDS"]["VALUES_ICONS"]
            await c.send_message(
                game.chat.id,
                ct("discarted_all").format(name=ir.from_user.mention, count=len(dcards))
                + f"\n{', '.join([f'{color_icons[card[0]]}{values_icons[card[1]]}' for card in dcards])}",
            )
        elif pcard[1] == "skipall":
            await c.send_message(game.chat.id, ct("skip_all").format(name=ir.from_user.mention))
            if games.get(game.chat.id) and not await verify_cards(
                game, c, ir, ir.from_user, ut, ct
            ):
                return await c.send_message(
                    game.chat.id,
                    ct("next").format(name=game.next_player.mention),
                    reply_markup=inline_keyb,
                )
        elif ((await Chat.get(id=game.chat.id)).seven) and (pcard[1] == "7" or pcard[1] == "0"):
            if pcard[1] == "7":
                if len(game.players) == 1:
                    await c.send_message(game.chat.id, ct("not_swapped"))
                else:
                    game.chosen = "player"
                    game.last_card_2 = {
                        "card": game.last_card,
                        "player": ir.from_user.id,
                    }
                    return await c.send_message(
                        game.chat.id,
                        ct("playerchoose").format(name=game.next_player.mention),
                        reply_markup=inline_keyb,
                    )
            else:
                # Aqui irá trocar as cartas dos jogadores na ordem do jogo
                gcards = {}
                for a, i in enumerate(game.players):
                    gcards[a] = game.players[i].cards

                for a, i in enumerate(game.players, start=1):
                    if a in gcards:
                        game.players[i].cards = gcards[a]
                    else:
                        game.players[i].cards = gcards[0]
                    await verify_cards(game, c, ir, game.players[i], ut, ct)

                await c.send_message(game.chat.id, ct("swapped"))
    else:
        return await c.send_message(game.chat.id, ct("invalid_card"))

    if games.get(game.chat.id) and not await verify_cards(game, c, ir, ir.from_user, ut, ct):
        game.next()
        return await c.send_message(
            game.chat.id,
            ct("next").format(name=game.next_player.mention),
            reply_markup=inline_keyb,
        )
    return None


async def verify_cards(game: Game, c: Client, ir, user: User, ut, ct):
    inline_keyb = InlineKeyboardMarkup([
        [InlineKeyboardButton(ct("play"), switch_inline_query_current_chat="")]
    ])
    if len(game.players[user.id].cards) == 1:
        if not (await Chat.get(id=game.chat.id)).one_card:
            await c.send_message(game.chat.id, ct("said_uno").format(name=user.mention))
        else:
            await c.send_message(
                game.chat.id,
                ut("say_uno").format(name=user.mention),
            )
            uno = False
            while True:
                try:
                    cmessage = await game.chat.listen(filters.text, timeout=5)
                    if (cmessage and cmessage.text) and "uno" in cmessage.text.lower():
                        uno = True
                        break
                except ListenerTimeout:
                    break
            if uno and cmessage.from_user.id == user.id:
                await c.send_message(game.chat.id, ct("said_uno").format(name=user.mention))
            else:
                game.players[user.id].cards.extend(game.deck.draw(2))
                await c.send_message(
                    game.chat.id,
                    ct("not_said_uno").format(name=user.mention),
                )

    elif len(game.players[user.id].cards) == 0:
        string = ct("won_first") if game.winner else ct("won")

        await c.send_message(game.chat.id, string.format(name=user.mention))
        if game.winner:
            game.winner = False
            if not game.is_dev:
                db_user = await User.get_or_none(id=user.id)
                if db_user and db_user.placar:
                    db_user.wins += 1
                    await db_user.save()
        if (await Chat.get(id=game.chat.id)).one_win and len(game.players) > 2:
            if not game.is_dev:
                db_user = await User.get_or_none(id=user.id)
                if db_user and db_user.placar:
                    db_user.matches += 1
                    db_user.cards += game.players[user.id].total_cards
                    await db_user.save()
            game.next()
            game.players.pop(user.id)
            player_game.pop(user.id)
            await c.send_message(game.chat.id, ct("continuing").format(count=len(game.players)))
            await c.send_message(
                game.chat.id,
                ct("next").format(name=game.next_player.mention),
                reply_markup=inline_keyb,
            )
        else:
            games.pop(game.chat.id)
            for player in game.players:
                db_user = await User.get_or_none(id=player)
                if db_user and db_user.placar:
                    db_user.matches += 1
                    db_user.cards += game.players[player].total_cards
                    await db_user.save()
                player_game.pop(player)
            await c.send_message(game.chat.id, ct("game_over"))
            game.stop()
            await game.message.edit_text(ct("game_over"))
            if (await Chat.get(id=game.chat.id)).auto_pin:
                await game.message.unpin()
        return True
    elif (await Chat.get(id=game.chat.id)).theme == "nomercy" and len(
        game.players[user.id].cards
    ) >= 25:
        # ao ter 25 cartas ou mais o jogador é eliminado
        await c.send_message(
            game.chat.id,
            ct("too_many_cards").format(name=user.mention),
        )
        game.next()
        game.players.pop(user.id)
        player_game.pop(user.id)
        # agora ele verifica se o tem minimum_players jogadores ou mais, caso contrário o jogo acaba
        if len(game.players) < minimum_players:
            for player in game.players:
                player_game.pop(player)
            games.pop(game.chat.id)
            await c.send_message(game.chat.id, ct("game_over"))
            game.stop()
            await game.message.edit_text(ct("game_over"))
            if (await Chat.get(id=game.chat.id)).auto_pin:
                await game.message.unpin()
        else:
            await c.send_message(
                game.chat.id,
                ct("next").format(name=game.next_player.mention),
                reply_markup=inline_keyb,
            )
        return True
    return False
