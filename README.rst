Unu
===

A Telegram bot for playing the UNO cards game

Description
-----------
.. raw:: html

   <style>
       .rounded {
           border-radius: 50%;
           width: 100px;
           height: 100px;
       }
   </style>

.. image:: https://rianfc.github.io/imgs/unurobot.png
   :align: right
   :scale: 25%
   :class: rounded

Unu is a Telegram bot that allows users to play the famous UNO card game directly in the chat. The bot manages the game, distributes the cards, and enforces the rules, providing a fun and interactive experience.

----------------------------

Features
--------

- Creation of game rooms
- Automatic card distribution
- Turn management
- Enforcement of UNO game rules
- Support for Telegram commands to interact with the bot

How to use
----------

- Add the bot t.me/unurobot to your Telegram chat
- Create a game room with the command `/new`
- Wait for other players to join the room via the button or the command `/join`
- Start the game with the command `/start` or via the button
- Have fun playing UNO!
- If you want to customize the game such as cards and rules, use the command `/settings`

How to run the bot locally
--------------------------
- Clone the repository using the command `git clone https://github.com/AmanoTeam/UnuRobot.git`
- Create a virtual environment with the command `python -m venv venv`
- Activate the virtual environment with the command `source venv/bin/activate`
- Install the dependencies with the command `pip install .`
- Copy the `config-example.py` file to `config.py` and edit the environment variables
- Run the bot with the command `python -m unu`

Contributions
-------------
Contributions are welcome! Feel free to open an issue or submit a pull request.

License
-------
This project is licensed under the MIT license. See the LICENSE file for more information.
