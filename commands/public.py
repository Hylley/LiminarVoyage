from random import randint
from scripts import image_processing, utils


def daily(self, **kwargs):
    player = kwargs['request_player']
    tweet = kwargs['tweet']

    current_time = tweet.created_at.replace(tzinfo=None)
    last_register = utils.string_to_date(player.read_internal_data('Last Daily Collect Date'), '')

    print(current_time)
    print(last_register)

    if last_register:
        if (current_time - last_register).days < 1:
            return ['You\'ve already collected your daily chest.']


def inventory(self, **kwargs):
    player = kwargs['request_player']
    page = utils.find_int(kwargs['request_tweet_text'], 0) or 1

    inventory = player.inventory(50)
    items, max_pages = inventory[page-1], len(inventory)

    image = self.api.media_upload(
        filename=f'{player.screen_name}_inventory_card',
        file=image_processing.inventory_card(
            10,
            5,
            20,
            items,
            [page, max_pages]
        ))
    
    return {
        'text': ' ',
        'images': [image.media_id_string]
    }


def profile(self, **kwargs):
    # Player dataa

    player = kwargs['request_player']
    user = self.api.get_user(screen_name=player.screen_name)

    bio = user.description
    image_url = user.profile_image_url_https.replace('_normal', '')

    # Icons

    equipment = player.equipment()
    icons = []
    for key, value in equipment.items():
        if value != 0:
            icons.append(f'storage\\images\\items\\{value}.png')
        else:
            icons.append(None)

    # Card call

    profile_card = image_processing.profile_card(
        image=image_url,
        name=player.player['name'],
        health=player.player['health'],
        max_health=player.internal['max_health'],
        progress=[
            player.player['level'],
            [
                player.player['exp'],
                player.internal['next_level_up_exp']
            ],
            player.player['grenag']
        ],
        values=[
            player.status['attack'],
            player.status['defense'],
            player.status['magic_power']
        ],
        bio=bio,
        player_equipment_icon=icons
    )

    image = self.api.media_upload(filename=f'{player.screen_name}_profile_card', file=profile_card)

    return {
        'text': f'{player.player["name"]}\'s profile:',
        'images': [image.media_id_string]
    }


def equip(self, **kwargs):
    player = kwargs['request_player']
    text = kwargs['request_tweet_text']

    item_id = utils.find_int(text, 0)

    slots = {'head': 1, 'torso': 2, 'hand_1': 0, 'hand_2': 0, 'legs': 3}
    slot = False
    for key, value in slots:
        if key in text:
            slot = value

    if not slot:
        return {
            'text': 'No valid slots provided.',
            'images': None
        }

    response = player.equip(item_id, slot)

    if response:
        if isinstance(response, str):
            return {
                'text': response,
                'images': None
            }
        else:
            return profile(self, **kwargs)


def unequip(self, **kwargs):
    player = kwargs['request_player']
    text = kwargs['request_tweet_text'].split()

    text.pop(0)
    input = text[0]
    text.pop(0)
    complement = text[0]

    response = player.unequip(slot=input, complement=complement)

    if response:
        if isinstance(response, str):
            return {
                'text': response
            }
        else:
            return profile(self, **kwargs)
    else:
        return None


def map(self, **kwargs):
    player = kwargs['request_player']
    text = kwargs['request_tweet_text']
    info = False

    if 'info' in text:
        info = True

    image = self.api.media_upload(filename=f'{player.id}_map_card_sol', file=image_processing.map_card(info))

    return {
        'text': ' ',
        'images': [image.media_id_string]
    }

# Debug


def roll(self, **kwargs):
    dices = 6

    text = kwargs['request_tweet_text'].split()
    text.pop(0)

    if utils.index(text, 0) and text[0].isnumeric():
        dices = int(text[0])

    return {
        'text': str(randint(1, dices))
    }


def add_item(self, **kwargs):
    kwargs['request_player'].add(11037, 1)
    return {
        'text': "Status: added 11037 of instance 1;",
        'images': None
    }


def remove_item(self, **kwargs):
    kwargs['request_player'].subtract(11037, 1)
    return {
        'text': "Status: subtracted 11037 of instance 1;",
        'images': None
    }