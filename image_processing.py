from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

main_path = 'storage\\images\\graphics\\'


def profile_card(image, name, health, max_health, progress, values, bio, player_equipment_icon):
    default_icons = [
        f'{main_path}profile\\default_icons\\barbute.png',
        f'{main_path}profile\\default_icons\\plastron.png',
        f'{main_path}profile\\default_icons\\gauntlet_0.png',
        f'{main_path}profile\\default_icons\\gauntlet_1.png',
        f'{main_path}profile\\default_icons\\leg-armor.png',
    ]

    level = f'Level: {str(progress[0])}     XP: {str(progress[1][0])}/{str(progress[1][1])}      L$: {str(progress[2])}'

    background = Image.open(main_path + 'profile\\neutral_main.png')

    # Adjust profile

    response = requests.get(image)
    profile_pic = Image.open(BytesIO(response.content)).resize((274, 274))
    profile_pic = add_margin(profile_pic,  99, 1203, 527, 123, (255, 255, 255))

    mask = Image.open(main_path + 'profile\\pic_mask.png').convert('L')
    card = Image.composite(profile_pic, background, mask)

    # Text

    # Adjust basic info text
    name_font = ImageFont.truetype(main_path + '..\\fonts\\seahorse_typeface.otf', 174)
    health_font = ImageFont.truetype(main_path + '..\\fonts\\segara_regular.otf', 17)
    values_font = ImageFont.truetype(main_path + '..\\fonts\\breamcatcher_regular.otf', 50)

    ImageDraw.Draw(card).text((475, 93), name, font=name_font)

    max_rectangle_slider_value = 576
    slider_value = (max_rectangle_slider_value * health)/max_health
    ImageDraw.Draw(card).rectangle((135, 454, 135 + slider_value, 544), fill=(143, 136, 108))

    ImageDraw.Draw(card).text((152, 515), f'{health}/{max_health}', font=health_font)
    ImageDraw.Draw(card).text((152, 564), level, font=health_font)
    
    # Adjust bio
    ImageDraw.Draw(card).text((92, 636), bio, font=health_font)

    # Adjust action values
    ImageDraw.Draw(card).text((1045, 518), str(values[0]), font=values_font)
    ImageDraw.Draw(card).text((1045, 618), str(values[1])+'%', font=values_font)
    ImageDraw.Draw(card).text((1045, 718), str(values[2]), font=values_font)

    # Adjust icons
    icons = []
    icon_size = (51, 51)

    for i in range(len(default_icons)):
        if player_equipment_icon[i]:
            icons.append(Image.open(player_equipment_icon[i]).resize(icon_size, Image.NEAREST))
        else:
            icons.append(Image.open(default_icons[i]).resize(icon_size))

    card.paste(icons[0], (1307, 507), icons[0])
    card.paste(icons[1], (1307, 611), icons[1])
    card.paste(icons[2], (1203, 611), icons[2])
    card.paste(icons[3], (1413, 611), icons[3])
    card.paste(icons[4], (1307, 716), icons[4])

    file = BytesIO()
    card.save(file, 'PNG')
    file.seek(0)

    return file


def inventory_card(items, collums, lines, spacing, items_list, page):
    background = Image.open(f'{main_path}inventory\\inventory_background.png')
    slot_path = f'{main_path}inventory\\inventory_slot.png'

    center = [int(background.size[0]/2), int(background.size[1]/2)]
    slots = []

    slot_size = 79
    item_icon_size = (70, 70)
    quantity_relative_position = (60, 60)
    unit = spacing + slot_size
    pos_y = 241

    quantity_font = ImageFont.truetype(main_path + '..\\fonts\\segara_regular.otf', 30)
    page_view_font = ImageFont.truetype(main_path + '..\\fonts\\breamcatcher_regular.otf', 40)

    ImageDraw.Draw(background).text(
        (739, 817),
        f'Page {page[0]}/{page[1]}',
        font=page_view_font)

    if collums % 2 == 0:  # If number is even.
        for i in range(lines):
            pos_x = (((collums * spacing) + (collums * slot_size)) - unit)/1.5

            for i in range(collums):
                pos_x -= unit

                slot = Image.open(slot_path)
                position = center[0] - int(pos_x), pos_y

                background.paste(slot,
                                 position,
                                 slot)

                slots.append(position)

            pos_y += unit

        for i in range(len(slots)):
            if i < len(items_list):
                item = Image.open(items_list[i][0]).resize(item_icon_size, Image.NEAREST).convert("RGBA")
                position = (int(slots[i][0] + slot_size/18), int(slots[i][1] + slot_size/18))
                background.paste(item, position, item)
                ImageDraw.Draw(background).text((position[0] + quantity_relative_position[0], position[1] + quantity_relative_position[1]), str(items_list[i][1]), font=quantity_font)

    file = BytesIO()
    background.save(file, 'PNG')
    file.seek(0)

    return file

# Utils

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result