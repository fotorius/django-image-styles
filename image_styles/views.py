from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import Http404

import mimetypes

from models import *

def render_image(request,style_id,path):
    try:
        style = Style.objects.get(id=style_id)
    except Style.DoesNotExist:
        return Http404("Style not found")
    try:
        image = ImageStyle.objects.get(name=path,style=style)
    except ImageStyle.DoesNotExist:
        image = ImageStyle(name=path,style=style)
        image.save()
    content_type = mimetypes.guess_type(image.image.path)
    return HttpResponse(image.image,content_type=content_type[0])
