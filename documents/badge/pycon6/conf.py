# -*- coding: UTF-8 -*-
import sys
import string
from PIL import Image, ImageFont

PAGE_MARGIN = 5

_fonts = {
    'unicode': 'Arial_Unicode.ttf',
    'attendee': 'ProximaNova-Semibold.otf',
    'staff': 'ProximaNova-Bold.otf',
}

PY_LOGO = {
    'all': 'pitoncino.png'
}


def tickets(tickets):
    groups = {
        'staff_fronte': {
            'image': Image.open('staff.png').convert('RGBA'),
            'attendees': []
        },
        'staff_retro': {
            'image': Image.open('staff.png').convert('RGBA'),
            'attendees': [],
            'mirror_x': True,
        },
        'day_fronte': {
            'image': Image.open('day-fronte.png').convert('RGBA'),
            'attendees': [],
        },
        'day_retro': {
            'image': Image.open('day-retro.png').convert('RGBA'),
            'attendees': [],
            'mirror_x': True,
        },
    }

    for t in tickets:
        if t.get('staff'):
            g = 'staff'
        else:
            g = 'day'
        groups[g + '_fronte']['attendees'].append(t)
        groups[g + '_retro']['attendees'].append(t)

    for v in groups.values():
        v['attendees'].sort(key=lambda x: x['name'].lower())

    return groups


def ticket(image, ticket, utils):
    image = image.copy()
    if not ticket:
        return image

    first_name, last_name = utils['split_name'](ticket['name'])
    tagline = ticket.get('tagline', '').strip()
    group = utils['ticket_group'](ticket)

    first_name = string.capwords(first_name)
    last_name = string.capwords(last_name)

    d = lambda **kw: utils['draw_info'](image, max_width=image.size[0]-200, **kw)
    if group.startswith('staff'):
        font_name = utils['open_font'](_fonts['staff'], points=33)
        font_tagline = utils['open_font'](_fonts['unicode'], points=13)

        d(pos=(144, 550), text=first_name, font=font_name, color=(0, 0, 0))
        d(pos=(144, 688), text=last_name, font=font_name, color=(0, 0, 0))
        d(pos=(144, 784), text=tagline, font=font_tagline, color=(0, 0, 0))

        logo_x = 590
        logo_y = 970
    else:
        font_name = utils['open_font'](_fonts['attendee'], points=26)
        font_tagline = utils['open_font'](_fonts['unicode'], points=15)
        if len(first_name) > 15:
            font_first_name = utils['open_font'](_fonts['attendee'], points=20)
        else:
            font_first_name = font_name
        if len(last_name) > 15:
            font_last_name = utils['open_font'](_fonts['attendee'], points=20)
        else:
            font_last_name = font_name

        d(pos=(142, 552), text=first_name, font=font_first_name, color=(255, 255, 255))
        d(pos=(142, 660), text=last_name, font=font_last_name, color=(255, 255, 255))

        if tagline:
            lines, tag_y = d(pos=(142, 768), text=tagline, font=font_tagline, color='#e2023b')
            logo_y = tag_y + 80
        else:
            logo_y = 768

        logo_x = 142

    if ticket['badge_image']:
        img = utils['open_auxiliary_image'](ticket['badge_image'], mm=5)
    else:
        img = utils['open_auxiliary_image'](PY_LOGO['all'], mm=5)
    for ix in range(ticket.get('experience', 0)):
        image.paste(img, (logo_x + (img.size[0] + 20) * ix, logo_y - img.size[1] / 2), img)

    return image
