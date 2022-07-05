import sqlite3


def connect(file):
    con = sqlite3.connect(f'database/{file}')

    return con.cursor(), con


"""
    GAME RELATABLE FUNCTIONS:
    
    All the code necessary for the bot to work, as well the internal data are here.
"""


def general_item(item_id):
    """
        The 'general item' function search for a given id item info in both 'equipment' and
        'items' tables. Since all the objects in both tables have a unique and exclusive id,
        there's no conflict problem.

        (Even if it had, the 'items' table will have preference.)
    """

    db, con = connect('game_side.db')

    result = db.execute(
        f'SELECT * FROM items WHERE id = {item_id}'
    ).fetchone() or db.execute(
        f'SELECT * FROM equipment WHERE id = {item_id}'
    ).fetchone() or None

    con.close()
    return result


def equipment(armor_id):
    db, con = connect('game_side.db')

    result = db.execute(
        f'SELECT * FROM equipment WHERE id = {armor_id}'
    ).fetchone() or None

    con.close()
    return result

"""
    INTERNAL RELATABLE FUNCTIONS:

    All the code related to the operation of the game itself is here.
"""


def private(key, value=None):
    """
        The 'private' function access the 'private_data table, where is stored all the bot
        important data.

        If the value attribule is filled, then the respective key value of the table will be
        updated. If not, then the function will return the current value. A simple but dinamic
        read/update one-in-the-same function.

        If the key not found, return 'None'.
    """

    db, con = connect('game_side.db')

    if not value:
        result = db.execute(
            f'SELECT value FROM private_data WHERE key = ?', [key]
        ).fetchone()[0] or None

        con.close()
        return result

    try: value = str(value)     # Tries to convert variable to string, if not, then return;
    except: return None

    db.execute(
        f'UPDATE private_data SET value = ? WHERE key = ?', [value, key]
    )
    print('Save:', value)

    con.commit()
    con.close()
