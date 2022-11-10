# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Colors
RED = "r"
BLUE = "b"
GREEN = "g"
YELLOW = "y"
BLACK = "x"

COLORS = (RED, BLUE, GREEN, YELLOW)

COLOR_ICONS = {RED: "❤️", BLUE: "💙", GREEN: "💚", YELLOW: "💛", BLACK: "⬛️"}

# Values
ZERO = "0"
ONE = "1"
TWO = "2"
THREE = "3"
FOUR = "4"
FIVE = "5"
SIX = "6"
SEVEN = "7"
EIGHT = "8"
NINE = "9"
DRAW_TWO = "draw"
REVERSE = "reverse"
SKIP = "skip"

VALUES = (
    ZERO,
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    DRAW_TWO,
    REVERSE,
    SKIP,
)
WILD_VALUES = (ONE, TWO, THREE, FOUR, FIVE, DRAW_TWO, REVERSE, SKIP)

# Special cards
CHOOSE = "colorchooser"
DRAW_FOUR = "draw_four"

SPECIALS = (CHOOSE, DRAW_FOUR)

STICKERS = {
    "b_0": "CAACAgQAAxkDAAI372NtY-V641fF6HhAA4Vuc6CbI_LeAALZAQACX1eZAAEqnpNt3SpG_ysE",
    "b_1": "CAACAgQAAxkDAAI38GNtY-UvkNQN3h5p5n_dfNbhPV9HAALbAQACX1eZAAHluPl_BVzaDisE",
    "b_2": "CAACAgQAAxkDAAI38WNtY-X4Gvnxt4mofZ-Uv_zmGWHRAALdAQACX1eZAAEFe5JBdpP-cysE",
    "b_3": "CAACAgQAAxkDAAI38mNtY-av7Gm6hUEdRs_mONWGzKoGAALfAQACX1eZAAFQJXWHQ2D7uisE",
    "b_4": "CAACAgQAAxkDAAI382NtY-YXxHbN1MfXSl6FbzwgWq5vAALhAQACX1eZAAHo1SP4devY_ysE",
    "b_5": "CAACAgQAAxkDAAI39GNtY-dNEOn0i1luuPjPOHvqyasxAALjAQACX1eZAALf6g-FruzaKwQ",
    "b_6": "CAACAgQAAxkDAAI39WNtY-df9ew41xXE6ARS3VHDKg0NAALlAQACX1eZAAHwMoU1Nb4OgisE",
    "b_7": "CAACAgQAAxkDAAI39mNtY-ftENXWBUBNqNTomh-NeufNAALnAQACX1eZAAFOBAnoop1fWisE",
    "b_8": "CAACAgQAAxkDAAI392NtY-idvjst_LSKlwP2cEDnS3WpAALpAQACX1eZAAHmKrizqjwJ3isE",
    "b_9": "CAACAgQAAxkDAAI3-GNtY-jEw-hh0ei6OxSl2r4DehmIAALrAQACX1eZAAHvul-ZztVWiisE",
    "b_draw": "CAACAgQAAxkDAAI3-WNtY-nrtJj_c48YtjbPwydARdwJAALtAQACX1eZAAGdURg9n6qvEysE",
    "b_skip": "CAACAgQAAxkDAAI3-mNtY-kVI0dIVd38sOvZrZmtRCv_AALxAQACX1eZAAHAf0ks_Y82JysE",
    "b_reverse": "CAACAgQAAxkDAAI3-2NtY-p4_EUUTVDYKX12SMcKA9IbAALvAQACX1eZAAFjAZc535XzNSsE",
    "g_0": "CAACAgQAAxkDAAI3_GNtY-qvO3V8NwHojOpf8aIpbnYvAAL3AQACX1eZAAH7m-CsNWDzBSsE",
    "g_1": "CAACAgQAAxkDAAI3_WNtY-r28bGOeJGKL7ZtEwUrWXzfAAL5AQACX1eZAAFVNSG--aqs9CsE",
    "g_2": "CAACAgQAAxkDAAI3_mNtY-sjqfdB5nu7iKPFqHRItFerAAL7AQACX1eZAAHDX5Qn7VbSdCsE",
    "g_3": "CAACAgQAAxkDAAI3_2NtY-ueCVLB_KL8Xz0itFJGWNbYAAL9AQACX1eZAAGwUxSSKSNPaisE",
    "g_4": "CAACAgQAAxkDAAI4AAFjbWPsRRrrb0KdkF5SGCO87ni9sAAC_wEAAl9XmQABARICqk9L7OArBA",
    "g_5": "CAACAgQAAxkDAAI4AWNtY-zlRyWdS69Z4bcwBgklRcBEAAIBAgACX1eZAAGN2wN5nVhf3ysE",
    "g_6": "CAACAgQAAxkDAAI4AmNtY-zXK3F2NTz-XaFeDk2rsP7NAAIDAgACX1eZAAFaJA80kw1XfSsE",
    "g_7": "CAACAgQAAxkDAAI4A2NtY-0dqOmBW9-XK_BbtXg0OLRaAAIFAgACX1eZAAGDbLTCiNGLBisE",
    "g_8": "CAACAgQAAxkDAAI4BGNtY-2kF7oUCmvU_AbU9lmudtZqAAIHAgACX1eZAAGnWrRTRZj7gSsE",
    "g_9": "CAACAgQAAxkDAAI4BWNtY-60BpqwiJQ8-p93unknqHi2AAIJAgACX1eZAAHODOPdhwzltysE",
    "g_draw": "CAACAgQAAxkDAAI4BmNtY-53H6EJgbUQSeEpguubOevXAAILAgACX1eZAAFWg06uGplHVysE",
    "g_skip": "CAACAgQAAxkDAAI4B2NtY-5VirooDDZAWu4ENrVBBoFHAAIPAgACX1eZAAHn-hBXxRvYQisE",
    "g_reverse": "CAACAgQAAxkDAAI4CGNtY-_G8b0fBt0N3OBgx9CIwJziAAINAgACX1eZAAFMYqmCS3vfySsE",
    "r_0": "CAACAgQAAxkDAAI4CWNtY-9LOKHb1FqCn3GmqxOYCo_fAAIRAgACX1eZAAHK9atgT_cu_isE",
    "r_1": "CAACAgQAAxkDAAI4CmNtY_Dxb_ivl-VHFRDPgHVOilCVAAITAgACX1eZAAH_6pt2airFESsE",
    "r_2": "CAACAgQAAxkDAAI4C2NtY_B9bP3cd73NvBd-Un8yZTYzAAIVAgACX1eZAAHQrmSSeMDfgCsE",
    "r_3": "CAACAgQAAxkDAAI4DGNtY_Hqk5RPHjNn50jy_ImBPYZLAAIXAgACX1eZAAFeHWWPa-piRysE",
    "r_4": "CAACAgQAAxkDAAI4DWNtY_HqY4wNkPulTWHIY9d2Fep-AAIZAgACX1eZAAE7VUWywkd3KCsE",
    "r_5": "CAACAgQAAxkDAAI4DmNtY_Lb9j5Qi5RVPEaSW3uZWAnlAAIbAgACX1eZAAF1s0b9V-PUJCsE",
    "r_6": "CAACAgQAAxkDAAI4D2NtY_Kklm1t7E0KShmWTbXEwnpNAAIdAgACX1eZAAF8hSz11exIUisE",
    "r_7": "CAACAgQAAxkDAAI4EGNtY_LoR07j-LayjpoVlEPLCCe0AAIfAgACX1eZAAEVnCo1RKSqnCsE",
    "r_8": "CAACAgQAAxkDAAI4EWNtY_OrIOu5PPIUTZ-cn0FBFcT2AAIhAgACX1eZAAEhXezQrbzKOisE",
    "r_9": "CAACAgQAAxkDAAI4EmNtY_PI6uILsPHkkyIDFp4ivFBJAAIjAgACX1eZAAHN4GBkUaxpqisE",
    "r_draw": "CAACAgQAAxkDAAI4E2NtY_SNrUaYiRbAIEi9c_X-veafAAIlAgACX1eZAAGZvG1zNp2cVisE",
    "r_skip": "CAACAgQAAxkDAAI4FGNtY_SrNSCK9k9FO9Xji2fb9LJMAAIpAgACX1eZAAFprUDwYHBu3SsE",
    "r_reverse": "CAACAgQAAxkDAAI4FWNtY_V41t8UX4XtxugfwVMibbqLAAInAgACX1eZAAGay7EvXnoVZisE",
    "y_0": "CAACAgQAAxkDAAI4FmNtY_XYaAevT9wxGiAxI1n6e_spAAIrAgACX1eZAAG1mgAB2D5sIc8rBA",
    "y_1": "CAACAgQAAxkDAAI4F2NtY_aD1zsrQYWtYoeePhDN1bcvAAItAgACX1eZAAHqNCCjuSEQjisE",
    "y_2": "CAACAgQAAxkDAAI4GGNtY_Y9kN6nzxvk8KwX8SnwTntmAAIvAgACX1eZAAH4u547rBAiBCsE",
    "y_3": "CAACAgQAAxkDAAI4GWNtY_dJwM67rmUFcLEtByedoFJdAAIxAgACX1eZAAFBQ00TMrpMeisE",
    "y_4": "CAACAgQAAxkDAAI4GmNtY_d6JUufI61BWnqI4DTVRxMVAAIzAgACX1eZAAF7IOqIuGqyDSsE",
    "y_5": "CAACAgQAAxkDAAI4G2NtY_dxij19aBCA7Tjf5ytWzXgNAAI1AgACX1eZAAHyIiYzI-E-LisE",
    "y_6": "CAACAgQAAxkDAAI4HGNtY_hPQ2iuWWmADOUYR-P-nNVFAAI3AgACX1eZAAH_E8fuZ374hysE",
    "y_7": "CAACAgQAAxkDAAI4HWNtY_jp9tXZ3lpAV83tzDcazcA4AAI5AgACX1eZAAHPK6qSI6Ku_CsE",
    "y_8": "CAACAgQAAxkDAAI4HmNtY_kQwEGUW6F38bBIYXfspzarAAI7AgACX1eZAAHXiL4XwJi0eysE",
    "y_9": "CAACAgQAAxkDAAI4H2NtY_kJ_ofl80XkaVobKpd-IgqQAAI9AgACX1eZAAGG_opl6vQSOCsE",
    "y_draw": "CAACAgQAAxkDAAI4IGNtY_qbKj2mnuJVlTai4F6se8MNAAI_AgACX1eZAAFrjyuhcA2ksysE",
    "y_skip": "CAACAgQAAxkDAAI4IWNtY_rKy-RTeKjfZT0RAYNNreVhAAJDAgACX1eZAAF1m63alvMoxysE",
    "y_reverse": "CAACAgQAAxkDAAI4ImNtY_vaX0rQZ_5ZUeFTpMa2ZQABOwACQQIAAl9XmQABCHpDm7MPbakrBA",
    "draw_four": "CAACAgQAAxkDAAI4I2NtY_vr1Fa4_Q2Y6dxOopNX7sSsAAL1AQACX1eZAAHXOgABZUCgVkkrBA",
    "colorchooser": "CAACAgQAAxkDAAI4JGNtY_vpncCbuHH2xDLokQWxUAXSAALzAQACX1eZAAHI5jbpFQE9bCsE",
    "option_draw": "CAACAgQAAxkDAAI4JWNtY_zry4NT2JAlWjTryYiuec4nAAL4AgACX1eZAAH-TdXSlvEa2ysE",
    "option_pass": "CAACAgQAAxkDAAI4JmNtY_yMlr6rB3UdTikR3zFCk8kVAAL6AgACX1eZAAFuilR5QnD-VysE",
    "option_bluff": "CAACAgQAAxkDAAI4J2NtY_2Dmt5Mi4iZhsUh32OeNVe7AALKAgACX1eZAAHBw478rNqN0CsE",
    "option_info": "CAACAgQAAxkDAAI4KGNtY_3tO0Sxhu5NzF1UA3tdUnklAALEAgACX1eZAAGi2Qy93IIQwisE",
}

STICKERS_GREY = {
    "b_0": "CAACAgQAAxkDAAI4KWNtY_3SM2AGtecbGE8XDjlWvcKxAAJFAgACX1eZAAHwXYFNZhQaIysE",
    "b_1": "CAACAgQAAxkDAAI4KmNtY_7zNsvijvvGZAJmuxcYVgizAAJHAgACX1eZAAF_ZxC64wgdNCsE",
    "b_2": "CAACAgQAAxkDAAI4K2NtY_4z7XEHPzcliqJth5G3ds6vAAJJAgACX1eZAAF-GuNgJ25IAAErBA",
    "b_3": "CAACAgQAAxkDAAI4LGNtY_9ZPE9nPCPJQ0Rjf_zOkTsiAAJLAgACX1eZAAHIJQ71XJ39mCsE",
    "b_4": "CAACAgQAAxkDAAI4LWNtY_--OWOFczobsp10PPj5p9pZAAJNAgACX1eZAAEjmR2mhJ8SsSsE",
    "b_5": "CAACAgQAAxkDAAI4LmNtZAABTkAAAT7kcgxZkdA3rcZmxM0AAk8CAAJfV5kAASN8DC8z_yexKwQ",
    "b_6": "CAACAgQAAxkDAAI4L2NtZAABOSkvi7YF9opHBHILrQukJwACUQIAAl9XmQABv35eqFpp188rBA",
    "b_7": "CAACAgQAAxkDAAI4MGNtZAABcb94kfODfzBiW7R6caIITgACUwIAAl9XmQABv8VaivrtncwrBA",
    "b_8": "CAACAgQAAxkDAAI4MWNtZAEPZcxI8yZZJ7mtvLEhRyQyAAJVAgACX1eZAAF8hUb4bS_NdCsE",
    "b_9": "CAACAgQAAxkDAAI4MmNtZAHG55HKa6LNKc496jAPrUCzAAJXAgACX1eZAAGXAmJ0BKvi1ysE",
    "b_draw": "CAACAgQAAxkDAAI4M2NtZALeN87Xgly5X7j5XK0dfaznAAJZAgACX1eZAAFS-DsDXK7zdisE",
    "b_skip": "CAACAgQAAxkDAAI4NGNtZAJR4ZxfKgABx3HNLp-9w8fNagACXQIAAl9XmQABc7AYk0bGSHorBA",
    "b_reverse": "CAACAgQAAxkDAAI4NWNtZAKP0DU5ZIh-4eID9fwEqWDhAAJbAgACX1eZAAHRLf8w4EEJfysE",
    "g_0": "CAACAgQAAxkDAAI4NmNtZAMTsoTxk-Gzg61XUbgiWmuDAAJjAgACX1eZAAG_c8FzjSBlOCsE",
    "g_1": "CAACAgQAAxkDAAI4N2NtZAOMsFWlo1a6VbET_L4Z33qjAAJlAgACX1eZAAH2R3CHmHduZCsE",
    "g_2": "CAACAgQAAxkDAAI4OGNtZASmomincPijzQaGuhzS4NT3AAJnAgACX1eZAAHB14u8vZ5pjSsE",
    "g_3": "CAACAgQAAxkDAAI4OWNtZATXrH2F0kmklBKkx5-yLbqeAAJpAgACX1eZAAFaZGnJmMcN9CsE",
    "g_4": "CAACAgQAAxkDAAI4OmNtZARrtuTkDtrmFwSWGCMNNyzVAAJrAgACX1eZAAF3KxLEqQq8KysE",
    "g_5": "CAACAgQAAxkDAAI4O2NtZAXsq9mIqylmXkuqblUSZ_s5AAJtAgACX1eZAAGObwogvTEInCsE",
    "g_6": "CAACAgQAAxkDAAI4PGNtZAXYyNLL6UnAXV2J5fcYDSjcAAJvAgACX1eZAAEpOGFMRnLGmSsE",
    "g_7": "CAACAgQAAxkDAAI4PWNtZAYp5RXbOKe2_RQkDLNHRnQsAAJxAgACX1eZAAEe_yu4DVELEisE",
    "g_8": "CAACAgQAAxkDAAI4PmNtZAZuRr1ubCO9SBPYf5uVwxOVAAJzAgACX1eZAAH26plyNxWZuCsE",
    "g_9": "CAACAgQAAxkDAAI4P2NtZAZ-4ux439AfgakLYhj7NkL7AAJ1AgACX1eZAAGrwYoTMk8UPSsE",
    "g_draw": "CAACAgQAAxkDAAI4QGNtZAcDJt3SZBIXhpzxAw-0pCjgAAJ3AgACX1eZAAFnlFIJWhbZIysE",
    "g_skip": "CAACAgQAAxkDAAI4QWNtZAdu6EvL3cTpvKgvVvS5TM8oAAJ7AgACX1eZAAFO5CqgPxquYSsE",
    "g_reverse": "CAACAgQAAxkDAAI4QmNtZAhYEij-J99P6WZprlvTrO1FAAJ5AgACX1eZAAE9cd3JVwlSEisE",
    "r_0": "CAACAgQAAxkDAAI4Q2NtZAhJMx2vsEJ0VqZf4K4vnICEAAJ9AgACX1eZAAEZAg2nRervSCsE",
    "r_1": "CAACAgQAAxkDAAI4RGNtZAggA5W5F360ygp-Kt5511ZGAAJ_AgACX1eZAAFtLPMD6heoDysE",
    "r_2": "CAACAgQAAxkDAAI4RWNtZAneP8mxTRUYpxCIcSZxrRzaAAKBAgACX1eZAAGuvzFU0Su89SsE",
    "r_3": "CAACAgQAAxkDAAI4RmNtZAkm-2Z3z4dgngqsNQKlAAEUIgACgwIAAl9XmQABBRY8MBWexokrBA",
    "r_4": "CAACAgQAAxkDAAI4R2NtZAr32JAr0Q5mSzPrZuPKAAEMAAOFAgACX1eZAAHZFzRnwree-ysE",
    "r_5": "CAACAgQAAxkDAAI4SGNtZAo06aPW8Bt2bEfhuAwYIAihAAKHAgACX1eZAAHsdpjtu9I2ISsE",
    "r_6": "CAACAgQAAxkDAAI4SWNtZArDcMo4iVhDv3V2PkjmODGWAAKJAgACX1eZAAG2D__a-tqZBSsE",
    "r_7": "CAACAgQAAxkDAAI4SmNtZAsNc-unKFxRAUfRgRpIu8zGAAKLAgACX1eZAAGXaAtw5YFztSsE",
    "r_8": "CAACAgQAAxkDAAI4S2NtZAtXBBjw_QmbUnPCqOjcPciqAAKNAgACX1eZAAGkCOaURWQl8CsE",
    "r_9": "CAACAgQAAxkDAAI4TGNtZAxdvNd9s7XbaETEDpraDSB8AAKPAgACX1eZAAH-WS6bmv9CgSsE",
    "r_draw": "CAACAgQAAxkDAAI4TWNtZAz-9sSylYycGwF82_5ceXLOAAKRAgACX1eZAAF2dldgt636fysE",
    "r_skip": "CAACAgQAAxkDAAI4TmNtZAwwZq3xqWgdKCELX9yXNNDHAAKVAgACX1eZAAGedr9LYgVebCsE",
    "r_reverse": "CAACAgQAAxkDAAI4T2NtZA1_h1jpVObJt7ZnGWC0EJu_AAKTAgACX1eZAAECR8T0lu-KmysE",
    "y_0": "CAACAgQAAxkDAAI4UGNtZA3XHBEqHJ4oD2s1vu019fCAAAKXAgACX1eZAALmpUbJzkaKKwQ",
    "y_1": "CAACAgQAAxkDAAI4UWNtZA70oPDw_EYnua3I_yHnoU0HAAKZAgACX1eZAAGB_02-C22PkysE",
    "y_2": "CAACAgQAAxkDAAI4UmNtZA73r_BBydbo0QL4Lrp6zzRgAAKbAgACX1eZAAHVmZUJxJwqmCsE",
    "y_3": "CAACAgQAAxkDAAI4U2NtZA7ITY2cWf3hZhbqbRFA2rznAAKdAgACX1eZAAGnajv8YZQj-ysE",
    "y_4": "CAACAgQAAxkDAAI4VGNtZA_w89jaIqKJT3mJ3jf4sNfqAAKfAgACX1eZAAEmxeENpAa35SsE",
    "y_5": "CAACAgQAAxkDAAI4VWNtZA9pJt03yLW1UVqmabBu03CRAAKhAgACX1eZAAH2evQmPPzx8isE",
    "y_6": "CAACAgQAAxkDAAI4VmNtZBBLaA_cEcY1-cmo4oRl7kFUAAKjAgACX1eZAAGYOfBpuoRg_CsE",
    "y_7": "CAACAgQAAxkDAAI4V2NtZBC1E-0IzKlEqkiFlLtGQ2djAAKlAgACX1eZAAFYxwrVWROuiysE",
    "y_8": "CAACAgQAAxkDAAI4WGNtZBDuCE40_AciHh4BlfOxvd4EAAKnAgACX1eZAAF10j1L6rASCSsE",
    "y_9": "CAACAgQAAxkDAAI4WWNtZBERcGe9cafGmVQMrn--6VyEAAKpAgACX1eZAAGV1nEmuqjoJCsE",
    "y_draw": "CAACAgQAAxkDAAI4WmNtZBHW7Ik5O4gDp80GEnME_8opAAKrAgACX1eZAAGfJ2XK_ooNFisE",
    "y_skip": "CAACAgQAAxkDAAI4W2NtZBLpZ4ilI48Wl42H2--LNZleAAKvAgACX1eZAAEVSSkTcHxJXCsE",
    "y_reverse": "CAACAgQAAxkDAAI4XGNtZBJeXdZLAWEB9hQVadvba2mLAAKtAgACX1eZAAEiP9aakPoiDysE",
    "draw_four": "CAACAgQAAxkDAAI4XWNtZBOEsZAZxOHFAttWBmLf5WSOAAJhAgACX1eZAAHWx9PCWaCqkysE",
    "colorchooser": "CAACAgQAAxkDAAI4XmNtZBPR9vYmNzz7P7Hq24wrLE16AAJfAgACX1eZAAH4WHYrSCRGIisE",
}


class Card:
    """This class represents an UNO card"""

    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def __str__(self):
        return self.special or f"{self.color}_{self.value}"

    def __repr__(self):
        if self.special:
            return f'{COLOR_ICONS.get(self.color, "")}{COLOR_ICONS[BLACK]}{" ".join([s.capitalize() for s in self.special.split("_")])}'

        else:
            return f"{COLOR_ICONS[self.color]}{self.value.capitalize()}"

    def __eq__(self, other):
        """Needed for sorting the cards"""
        return str(self) == str(other)

    def __lt__(self, other):
        """Needed for sorting the cards"""
        return str(self) < str(other)


def from_str(string):
    """Decodes a Card object from a string"""
    if string in SPECIALS:
        return Card(None, None, string)
    color, value = string.split("_")
    return Card(color, value)
