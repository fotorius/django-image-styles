from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
import shutil,os
from django.core.exceptions import MultipleObjectsReturned
from ..models import *
from ..utils import style as image_style

register = template.Library()

@register.filter
def style(orig_image,style_name):
    return image_style(orig_image,style_name)

@register.simple_tag
def render_image(orig_image,style_name,alt='image'):
    try:
        src = settings.MEDIA_URL+image_style(orig_image,style_name)
        return mark_safe('<img src="%s"alt="%s">' % (src,alt))
    except IOError:
        pass
    return ''

@register.filter
def valid_image_extension(image):
    """
    Evaluates if the image has a valid "image" extension.
    """
    VALID_EXTENSIONS = ('.jpg','.png','.jpeg')
    name, extension = os.path.splitext(image.name)
    if extension.lower() in VALID_EXTENSIONS:
        return True
    return False

