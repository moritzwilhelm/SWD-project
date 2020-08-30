import random

from django import template

register = template.Library()

colors = [('aqua', 'black'), ('black', 'white'), ('blueviolet', 'white'), ('brown', 'white'), ('darkgreen', 'white'),
          ('lightgrey', 'black'), ('limegreen', 'black'), ('orange', 'black'), ('pink', 'black'), ('red', 'white'),
          ('turquoise', 'black'), ('yellow', 'black')]


@register.simple_tag
def colorful_style():
    style = 'background-color: %s; color: %s'
    color = random.choice(colors)
    return style % (color[0], color[1])
