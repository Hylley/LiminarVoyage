import json
from math import ceil
from database import search_for_item


class Player:
    def __init__(self, user):
        with open('storage/database/players.json') as players_data:
            players = json.load(players_data)
            players_data.close()

        self.id = user
        self.player_data = players[user]
        self.name = self.player_data['Info']['Name']

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

                return items, pages
            else:
                return backpack, 1

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
                if inventory[item_id] + qnt > 0:
                    inventory[item_id] += qnt
                else:
                    del inventory[item_id]
            else:
                if qnt > 0:
                    inventory[item_id] = qnt
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

    # Gameplay functions

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


    # def unequip(self, item_id, slot, rest):

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


def player_exists(username):
    with open('storage/database/players.json') as players_data:
        players = json.load(players_data)
        players_data.close()

    return username in players
