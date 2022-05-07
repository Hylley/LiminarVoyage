from random import randint
import database
import image_processing

from time import sleep


def explore(self, **kwargs):
    kwargs['request_player'].update_internal_data('Is Exploring', 1)
    kwargs['request_player'].update_internal_data('Last Exploring Datetime', kwargs['tweet'].created_at)


def inventory(self, **kwargs):
    player = kwargs['request_player']
    page = 1

    'inventory page 2'
    text = kwargs['request_tweet_text'].split()
    if len(text) > 2:
        text.pop(0)
        text.pop(0)
        page = int(text[0])

    items = []

    inventory, pages = player.inventory(page, 50)

    for key, value in inventory.items():
        items.append([f'storage\\images\\items\\{key}.png', value])

    image = self.api.media_upload(
        filename=f'{player.id}_inventory_card',
        file=image_processing.inventory_card(
            0,
            10,
            5,
            20,
            items,
            [page, pages]
        ))

    self.api.update_status(status=' ', media_ids=[image.media_id_string],
                           in_reply_to_status_id=kwargs['request_tweet_id'],
                           auto_populate_reply_metadata=True)


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

    self.api.update_status(status=' ', media_ids=[image.media_id_string],
                           in_reply_to_status_id=kwargs['request_tweet_id'],
                           auto_populate_reply_metadata=True)


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
            self.api.update_status(status=response,
                                   in_reply_to_status_id=kwargs['request_tweet_id'],
                                   auto_populate_reply_metadata=True)
        else:
            profile(self, **kwargs)


def unequip(self, **kwargs):
    player = kwargs['request_player']
    text = kwargs['request_tweet_text'].split()

    text.pop(0)
    input = text[0]
    text.pop(0)
    complement = text[0]

    if input.isnumeric():
        response = player.unequip(item_id=int(input))
    else:
        response = player.unequip(slot=input, complement=complement)

    if response:
        if isinstance(response, str):
            self.api.update_status(status=response,
                                   in_reply_to_status_id=kwargs['request_tweet_id'],
                                   auto_populate_reply_metadata=True)
        else:
            profile(self, **kwargs)
    # Debug


def roll(self, **kwargs):
    dices = 6

    text = kwargs['request_tweet_text'].split()
    text.pop(0)
    dices = int(text[0])

    rand = randint(1, dices)

    self.api.update_status(status=rand,
                           in_reply_to_status_id=kwargs['request_tweet_id'],
                           auto_populate_reply_metadata=True)


def add_item(self, **kwargs):
    kwargs['request_player'].add_item('11037', 1)


def coins(self, **kwargs):
    coins = kwargs['request_player'].get_coins()
    self.api.update_status(status=coins, in_reply_to_status_id=kwargs['request_tweet_id'],
                           auto_populate_reply_metadata=True)