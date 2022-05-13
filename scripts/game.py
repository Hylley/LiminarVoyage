from random import randrange, shuffle
from scripts.database import open_read
from scripts.utils import refactor

path = f'storage\\database\\game\\chests.json'


class Chest:
    def __init__(self, sort):
        self.sort = sort

    def get_chest(self):
        return open_read(path)[self.sort.lower()]

    def items(self):
        result = []

        chest = self.get_chest()
        items_list = chest['items'].split()
        shuffle(items_list)
        quantity = chest['quantity']

        items = randrange(quantity, len(items_list))
        quantities = refactor(items, quantity)

        for i in range(len(quantities)):
            result.append([items_list[i], quantities[i]])

        return result