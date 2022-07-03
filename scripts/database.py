"""
    DATABASE:

    The game database is mainly divided into "player side" data and "game side" data.
This code manages the "game side" data.
"""

import sqlite3
from player import Player

path = '../database'    # All the database relatable files have to be in there.

connection = sqlite3.connect(f'{path}/game_side.db')    # Connect to game side database file.
db = connection.cursor()

player = Player('Hyllley')

"""
    GAME RELATABLE FUNCTIONS:
    
    All the code necessary for the bot to work, as well the internal data are here.
"""


def general_item(item_id):
    """
        The 'general item' function search for a given id item info in both 'weapons' and
        'items' tables. Since all the objects in both tables have a unique and exclusive id,
        there's no conflict problem.

        (Even if it had, the 'items' table will have preference.)
    """

    return db.execute(
        f'SELECT * FROM items WHERE id = {item_id}'
    ).fetchone() or db.execute(
        f'SELECT * FROM weapons WHERE id = {item_id}'
    ).fetchone() or None


"""
    INTERNAL RELATABLE FUNCTIONS:

    All the code related to the operation of the game itself is here.
"""


def private(key):
    """
        The 'private' function access the 'private_data table, where is stored all the bot
        important data.

        If no found, return 'None'.
    """

    return db.execute(
        f'SELECT value FROM private_data WHERE key = ?', [key]
    ).fetchone() or None


db.close()
