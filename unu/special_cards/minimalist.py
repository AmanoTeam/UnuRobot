from hydrogram import Client
from hydrogram.types import ChosenInlineResult, InlineKeyboardButton, InlineKeyboardMarkup

from unu.game import Game

inline_keyb = InlineKeyboardMarkup([
    [InlineKeyboardButton("Jogar", switch_inline_query_current_chat="")]
])


async def mirror(c: Client, ir: ChosenInlineResult, game: Game):
    if game.draw < 2:
        await c.send_message(game.chat.id, "Você não pode descartar essa carta agora!")
        return True
    print(game.last_card_2, game.last_card)
    game.players[ir.from_user.id].total_cards += 1
    ncard = ir.result_id.split("-")[2]
    player = game.last_card_2["player"]
    player = game.players[int(player)]
    player.cards.extend(game.deck.draw(game.draw))
    await c.send_message(game.chat.id, f"{player.mention} comprou {game.draw} cartas!")
    game.players[ir.from_user.id].cards.pop(int(ncard))
    await c.send_message(
        game.chat.id,
        f"Próximo: {game.next_player.mention}",
        reply_markup=inline_keyb,
    )
    game.draw = 0
    return True
