import os
import json


def load_setting(category, setting):
    with open('storage/database/settings.json', 'r') as settings:
        data = json.load(settings)
        settings.close()

    return data[category][setting]


def set_setting(setting, value):
    with open('storage/database/settings.json', 'r') as settings:
        data = json.load(settings)
        data['system'][setting] = value
        settings.close()

    with open('storage/database/settings.json', 'w') as settings:
        json.dump(data, settings, indent=4)
        settings.close()

    settings.close()


def items_list():
    with open('storage/database/items.json', 'r') as items:
        data = json.load(items)
        items.close()

    return data


def search_for_item(item_id):
    if item_id in items_list():
        return items_list()[item_id]
    else:
        return False
