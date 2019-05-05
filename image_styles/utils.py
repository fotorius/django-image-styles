from django.conf import settings
from django.http import Http404
import shutil,os,re
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned
from .models import *
from .forms import CropForm,EnhanceForm,ResizeForm,SmartScaleForm
from .forms import RotateForm,ScaleForm,RoundCornersForm

def style(orig_image,style_name):
    try:
        orig_image_name = orig_image.name
    except AttributeError:
        orig_image_name = orig_image
    try:
        style_id = int(style_name)
    except ValueError:
        style_id = None
    try:
        if style_id:
            style = Style.objects.get(id=style_id)
        else:
            style = Style.objects.get(name=style_name)
    except Style.DoesNotExist:
        return orig_image
    try:
        image = ImageStyle.objects.get(name=orig_image_name,style=style)
    except ImageStyle.DoesNotExist:
        image = ImageStyle.objects.create(name=orig_image_name,style=style)
    except MultipleObjectsReturned:
        images = ImageStyle.objects.filter(name=orig_image_name,style=style)
        for i in images:
            i.delete()
        image = ImageStyle.objects.create(name=orig_image_name,style=style)

    return "%s" % (image.image,)

def render_image(style_name,path):
    try:
        if type(style_name) is int:
            style = Style.objects.get(id=style_name)
        else:
            style = Style.objects.get(name=style_name)
    except Style.DoesNotExist:
        raise Http404("Style not found")
    try:
        image = ImageStyle.objects.get(name=path,style=style)
    except ImageStyle.DoesNotExist:
        image = ImageStyle(name=path,style=style)
        image.save()
    except ImageStyle.MultipleObjectsReturned:
        images = ImageStyle.objects.filter(name=path,style=style).order_by('-id')
        image = images.first()
        images.exclude(id=image.id)
        images.delete()

    return image

def get_image(image_name,style_name):
    if not image_name:
        return None
    rendered_image = render_image(style_name,image_name)
    image_url = settings.MEDIA_URL[:-1]+reverse(
        'render_image',
        kwargs={
            'style_name':style_name,
            'path':image_name
        }
    )
    return image_url

def get_effect_form_class(effect_name=None,effect_model=None):
    if effect_model:
        r = re.search(r'models\.(?P<name>\w+)',str(type(effect_model)))
        if r:
            effect_name = r.group('name')
    if effect_name == 'Crop':
        return CropForm 
    elif effect_name == 'Enhance':
        return EnhanceForm 
    elif effect_name == 'Resize':
        return ResizeForm 
    elif effect_name == 'Rotate':
        return RotateForm 
    elif effect_name == 'Scale':
        return ScaleForm 
    elif effect_name == 'RoundCorners':
        return RoundCornersForm 
    elif effect_name == 'SmartScale':
        return SmartScaleForm 
    return None



