from . import database


class Player:
    def __init__(self, user):
        self.screen_name = user
        db = database.connect('player_side.db')

        # Adjusting all player variables from database.

        player_raw = db.execute(f'SELECT * FROM players WHERE name = ?', [self.screen_name]).fetchone()

        self.player = {
            'id': player_raw[0],
            'name': player_raw[1],
            'grenag': player_raw[2],
            'level': player_raw[3],
            'exp': player_raw[4],
            'health': player_raw[5]
        }

        status_raw = db.execute(f'SELECT * FROM status WHERE player_id = ?', [self.player['id']]).fetchone()

        self.status = {
            'max_health': status_raw[1],
            'attack': status_raw[2],
            'defense': status_raw[3],
            'magic_power': status_raw[4]
        }

    def inventory(self, items_per_page=0):
        inventory = database.connect('inventory.db')

        raw = inventory.execute(f'SELECT * FROM {self.screen_name}').fetchall()
        inventory.close()
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

    """
    def api_object(self, api):
        return api.get_user(screen_name=self.id)

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

    # Inventory manipulation

    def inventory(self, page=1, items_per_page=0):
        backpack = self.player_data['Inventory']['Backpack']
        keys = list(backpack)

        if items_per_page == 0:
            return backpack, 1

        pages = int(ceil(len(backpack)/items_per_page))

        if pages == 1:
            return backpack, 1

        else:
            if items_per_page < len(backpack):
                current_index = items_per_page * (page - 1)
                end_index = current_index + items_per_page

                items = {}

                while current_index < end_index:
                    if current_index < len(backpack):
                        items[keys[current_index]] = backpack[keys[current_index]]

                    current_index += 1

                return [items, pages]
            else:
                return [backpack, 1]

    def equipment(self):
        return self.player_data['Inventory']['Equipment']

    def add_item(self, item_id, qnt=1):
        item_id = str(item_id)
        inventory, pages = self.inventory()

        with open('storage/database/items.json', 'r') as file:
            items = json.load(file)
            file.close()

        if item_id in items:
            if item_id in inventory:
                if inventory[item_id]['qnt'] + qnt > 0:
                    inventory[item_id]['qnt'] += qnt
                else:
                    del inventory[item_id]
            else:
                if qnt > 0:
                    inventory[item_id] = {'qnt': qnt}
                else:
                    pass

            self.update_player_data()

    def subtract_item(self, item_id, qnt):
        self.add_item(item_id, -qnt)

    def remove_item(self):
        pass

    def has_item(self, item_id):
        inventory, pages = self.inventory()
        return str(item_id) in inventory

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
    db = database.connect('player_side.db')

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
