from django import template
from django.conf import settings
import shutil,os
from ..models import *

register = template.Library()

@register.filter
def style(orig_image,style_name):
    try:
        style = Style.objects.get(name=style_name)
    except Style.DoesNotExist:
        return orig_image
    try:
        image = ImageStyle.objects.get(name=orig_image.name,style=style)
    except ImageStyle.DoesNotExist:
        image = ImageStyle(name=orig_image.name,style=style)
        image.save()
    return "%s" % (image.image,)
