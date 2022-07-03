from random import randint
from scripts import image_processing, utils, game


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

    chest = game.Chest('common')

    for item in chest.items():
        player.add_item(item[0], item[1])
        player.update_internal_data('Last Daily Collect Date', current_time)

    return {
        'text': 'Boa meu mano.'
    }


def explore(self, **kwargs):
    kwargs['request_player'].update_internal_data('Is Exploring', 1)
    kwargs['request_player'].update_internal_data('Last Exploring Datetime', kwargs['tweet'].created_at)


def inventory(self, **kwargs):
    player = kwargs['request_player']
    page = 1

    text = kwargs['request_tweet_text'].split()
    if len(text) > 2:
        page = int(text[2])

    inventory = player.inventory(50)
    items, max_pages = inventory[page-1], len(inventory)

    image = self.api.media_upload(
        filename=f'{player.id}_inventory_card',
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
    user = self.api.get_user(screen_name=player.id)

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
        name=player.name,
        health=player.player_data['Status']['Health'],
        max_health=player.player_data['Status']['Max Health'],
        progress=[
            player.player_data['Progression']['Level'],
            [
                player.player_data['Progression']['Experience'],
                player.player_data['Progression']['Next Level Up Experience']
            ],
            player.player_data['Progression']['Coins'],
        ],
        values=[
            player.player_data['Status']['Attack'],
            player.player_data['Status']['Defense'],
            player.player_data['Status']['Magic Power'],
        ],
        bio=bio,
        player_equipment_icon=icons
    )

    image = self.api.media_upload(filename=f'{player.id}_profile_card', file=profile_card)

    return {
        'text': f'{player.name}\'s profile:',
        'images': [image.media_id_string]
    }


def equip(self, **kwargs):
    player = kwargs['request_player']
    text = kwargs['request_tweet_text'].split()

    text.pop(0)
    item_id = int(text[0])
    text.pop(0)
    slot = text[0]
    text.pop(0)

    response = player.equip(item_id, slot, text)

    if response:
        if isinstance(response, str):
            return {
                'text': response
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
    kwargs['request_player'].add_item('11037', 1)

    return {
        'text': "Ok meu brother."
    }


def coins(self, **kwargs):
    return {
        'text': str(kwargs['request_player'].get_coins())
    }