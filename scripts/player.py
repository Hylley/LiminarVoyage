from . import database


class Player:
    def __init__(self, user):
        self.screen_name = user
        db, con = database.connect('player_side.db')

        # Adjusting all player variables from database.

        raw = db.execute(f'SELECT * FROM players WHERE name = ?', [self.screen_name]).fetchone()

        self.player = {
            'id': raw[0],
            'name': raw[1],
            'grenag': raw[2],
            'level': raw[3],
            'exp': raw[4],
            'health': raw[5]
        }

        raw = db.execute(f'SELECT * FROM status WHERE player_id = ?', [self.player['id']]).fetchone()

        self.status = {
            'attack': raw[1],
            'defense': raw[2],
            'magic_power': raw[3]
        }

        raw = db.execute(f'SELECT * FROM internal_data WHERE player_id = ?', [self.player['id']]).fetchone()

        self.internal = {
            'max_health': raw[3],
            'next_level_up_exp': raw[4]
        }

        con.close()

    def api_object(self, api):
        return api.get_user(screen_name=self.screen_name)

    """
        PLAYER STATUS:

            The player status area deals with the player status system. It includes
        health, power values, internal data etc.
    """

    def boost(self, attack=0, defense=0, magic_power=0):
        db, con = database.connect('player_side.db')

        for key, value in {'attack': attack, 'defense': defense, 'magic_power': magic_power}:
            if value != 0:
                current = db.execute(f'SELECT {key} FROM equipment WHERE player_id = ?', [self.player['id']]).fetchone()[0]
                db.execute(f'UPDATE status SET {key} = ? WHERE player_id = ? ', [current + value, self.player['id']])

        con.commit()
        con.close()

    def nerf(self, attack=0, defense=0, magic_power=0):
        self.boost(-attack, -defense, -magic_power)

    """
        PLAYER INVENTORY:
        
            The player inventory area deals with the inventory system as well as the
        equipment logic. Functions that return the inventory, equip an armor equipment,
        add/remove an item, etc. are located here.
    """

    def inventory(self, items_per_page=0):
        """
                The inventory function search for the respective player inventory table in
            'inventory.db' and convert all the data to a more friendly readable dict variable.
        """

        inventory, con = database.connect('inventory.db')

        raw = inventory.execute(f'SELECT * FROM {self.screen_name}').fetchall()
        con.close()
        result = []

        for row in raw:
            result.append(
                {
                    "id": row[0],
                    'quantity': row[1]
                }
            )

        if items_per_page != 0:
            chunks = [result[x:x + items_per_page] for x in range(0, len(result), items_per_page)]
            return chunks

        return result

    def add(self, item_id, quantity, create_if_not_exist=True):
        inventory, con = database.connect('inventory.db')

        if inventory.execute(f'SELECT EXISTS(SELECT * FROM {self.screen_name} WHERE item_id = ? LIMIT 1)', [item_id]).fetchone()[0]:
            current = inventory.execute(f'SELECT quantity FROM {self.screen_name} WHERE item_id = ?', [item_id]).fetchone()[0]

            if current + quantity > 0 and quantity != 0:
                inventory.execute(f'UPDATE {self.screen_name} SET quantity = ? WHERE item_id = ?', [current + quantity, item_id])
            else:
                inventory.execute(f'DELETE FROM {self.screen_name} WHERE item_id = ?', [item_id])

            con.commit()
            con.close()
            return

        if create_if_not_exist:
            inventory.execute(f'INSERT INTO {self.screen_name} VALUES(?, ?)', [item_id, quantity])

        con.commit()
        con.close()

    def subtract(self, item_id, quantity = 0):
        self.add(item_id, -quantity, False)

    def has(self, item_id):
        """
            This functions checks if the player have the informed item id in inventory.
        """

        inventory, con = database.connect('inventory.db')

        result = inventory.execute(f'SELECT EXISTS(SELECT * FROM {self.screen_name} WHERE item_id = ? LIMIT 1)', [item_id]).fetchone()[0]

        con.commit()
        con.close()

        return result

    def equipment(self):
        """
                This function search for the current player armor equipment in 'player_side.db'
            and convert to a more friendly readable dict variable. If no equipped armor is found,
            the default value is 0.
        """

        equipment, con = database.connect('player_side.db')
        raw = equipment.execute(f'SELECT * FROM equipment WHERE player_id = ?', [self.player['id']]).fetchone()
        con.close()

        return {
            'head': raw[1] or 0,
            'torso': raw[2] or 0,
            'hand_1': raw[3] or 0,
            'hand_2': raw[4] or 0,
            'legs': raw[5] or 0,
        }

    def equip(self, armor_id, slot):
        if not self.has(armor_id): return 'The given ID is not present in your inventory.'
        if not database.equipment(armor_id): return 'The given ID is not an valid equippable item.'

        armor = database.equipment(armor_id)

        if not armor[3] == slot: return 'Unable to insert the given item to the respective location.'

        equipment, con = database.connect('player_side.db')

        equipment.execute(f'UPDATE equipment SET ? = ? WHERE player_id = ?', [slot, armor_id, self.screen_name])

        self.boost(
            attack=0,
            defense=0,
            magic_power=0
        )

        self.subtract(armor_id, 1)

        con.commit()
        con.close()

    """
    # Player status modifiers

    def take_damage(self, damage):
        pass

    def heal(self, heal_value):
        pass

    def boost_attributes(self, attack=0, defense=0, magic=0):
        status = self.player_data['Status']

        status['Attack'] += attack
        status['Defense'] += defense
        status['Magic Power'] += magic

        self.update_player_data()

    def nerf_attributes(self, attack=0, deffense=0, magic=0):
        self.boost_attributes(-attack, -deffense, -magic)

    # Equipment system

    def equip(self, item_id, slot, rest):
        item = search_for_item(str(item_id))

        if not str(item):
            return f'[{item_id}] does not exist.'
        elif not self.has_item(item_id):
            return f'You do not have the item [{item_id}] in your inventory or is already equipped.'

        match slot.lower():
            case 'hand':
                hand = int(rest[0])

                if hand > 2 or hand < 1:
                    return f'"Hand {hand}" does not exist.'
                elif self.is_equipped(item_id, f'hand {hand}'):
                    return f'[{item_id}] is already equipped.'
                
                if self.player_data['Inventory']['Equipment'][f'hand {hand}'] != 0:
                    self.unequip(self.player_data['Inventory']['Equipment'][f'hand {hand}'], None, None)

                self.player_data['Inventory']['Equipment'][f'hand {hand}'] = item_id

                if 'Attributes' in item:
                    self.boost_attributes(
                        item['Attributes']['Attack'],
                        item['Attributes']['Defense'],
                        item['Attributes']['Magic Power']
                    )

        self.subtract_item(item_id, 1)
        self.update_player_data()
        return True

    def unequip(self, item_id, slot, complement):
        item_id = int(item_id)

        equipment_slots = self.player_data['Inventory']['Equipment']
        unequipped = False

        if item_id:
            item = search_for_item(str(item_id))

            if not str(item):
                return f'[{item_id}] does not exist.'

            for slot in equipment_slots:
                if equipment_slots[slot] == item_id:
                    self.add_item(item_id)
                    equipment_slots[slot] = ""

                    if 'Attributes' in item:
                        self.nerf_attributes(
                            item['Attributes']['Attack'],
                            item['Attributes']['Defense'],
                            item['Attributes']['Magic Power']
                        )

                    unequipped = True

            if not unequipped:
                return f'[{item_id}] is not equipped.'
        else:
            if slot.lower() in equipment_slots:
                pass
            elif f'{slot} {complement}'.lower() in equipment_slots:
                slot = f'{slot} {complement}'.lower()
            else:
                return f'"{slot}" is not a valid equipment slot.'

            item_id = equipment_slots[slot]
            self.add_item(item_id)
            item = search_for_item(item_id)

            if 'Attributes' in item:
                self.nerf_attributes(
                    item['Attributes']['Attack'],
                    item['Attributes']['Defense'],
                    item['Attributes']['Magic Power']
                )

            equipment_slots[slot] = 0
        self.update_player_data()
        return True

    def is_equipped(self, item_id, slot):
        if self.player_data['Inventory']['Equipment'][slot] == item_id:
            return True
        else:
            return False

    # Internal data manipulation

    def update_player_data(self):
        with open('storage/database/players.json', 'r') as file:
            data = json.load(file)
            data[self.id] = self.player_data
            file.close()

        with open('storage/database/players.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()

    def read_internal_data(self, setting):
        if setting in self.player_data['Internal Data']:
            return self.player_data['Internal Data'][setting]

    def update_internal_data(self, setting, value):
        if setting in self.player_data['Internal Data']:
            with open('storage/database/players.json', 'r') as settings:
                data = json.load(settings)
                data[self.id]['Internal Data'][setting] = str(value)
                settings.close()

            with open('storage/database/players.json', 'w') as settings:
                json.dump(data, settings, indent=4)
                settings.close()

    def read_from_data(self, category, var):
        if category in self.player_data:
            if var in self.player_data[var]:
                return self.player_data[category][var]

    def get_coins(self):
        return self.player_data['Status']['Coins']
"""


def exists(screen_name):
    """
        The 'exists' function check if the player with informed screen name exist.
    """
    db = database.connect('player_side.db')[0]

    result = db.execute('SELECT EXISTS (SELECT 1 FROM players WHERE name= ? LIMIT 1)', [screen_name.lower()]).fetchone()[0]
    db.close()

    return result


"""
def player_exists(username):
    with open('storage/database/players.json') as players_data:
        players = json.load(players_data)
        players_data.close()

    return username in players


def register(user_id):
    with open('storage/database/player_model.json', 'r') as model:
        starter_data = json.load(model)
        model.close()

    with open('storage/database/players.json', 'r') as file:
        players_list = json.load(file)
        file.close()

    players_list[user_id] = starter_data['id']
    players_list[user_id]['Info']['Name'] = user_id

    with open('storage/database/players.json', 'w') as file:
        json.dump(players_list, file, indent=4)
        file.close()
"""
