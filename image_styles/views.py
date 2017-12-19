from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse

import mimetypes

from .models import *
from .forms import * 
from . import utils as image_styles_utils

def render_image(request,style_name,path):
    # render image
    image = image_styles_utils.render_image(style_name,path)
    content_type = mimetypes.guess_type(image.image.path)
    return HttpResponse(image.image.name,content_type=content_type[0])

@staff_member_required
def manage_image_styles(request):
    ims = []
    for s in Style.objects.all():
        effects = s.get_effects()
        for i in range(len(effects)):
            if type(effects[i]['object']) == type(Crop()):
                effects[i]['form'] = CropForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(Enhance()):
                effects[i]['form'] = EnhanceForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(Resize()):
                effects[i]['form'] = ResizeForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(Rotate()):
                effects[i]['form'] = RotateForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(Scale()):
                effects[i]['form'] = ScaleForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(RoundCorners()):
                effects[i]['form'] = RoundCornersForm(instance=effects[i]['object'])
            elif type(effects[i]['object']) == type(SmartScale()):
                effects[i]['form'] = SmartScaleForm(instance=effects[i]['object'])

        ims.append({
            'style':s,
            'effects':effects,
        })

    c = {
        'styles':ims,
    }
    return render(request,'image_styles/manage_image_styles.html',c)

@staff_member_required
def style(request,style_id=None):
    if request.method == 'POST':
        if style_id is None:
            form = StyleForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse('Style Created!')
        else:
            style = get_object_or_404(Style,pk=style_id)
            form = StyleForm(request.POST,instance=style)
            if form.is_valid():
                if 'delete' in request.POST:
                    style.delete()
                    return HttpResponse('Style Deleted!')
                
                form.save()
                return HttpResponse('Style Saved!')
    else:
        if style_id is None:
            form = StyleForm()
        else:
            form = StyleForm(instance=get_object_or_404(Style,pk=style_id))

    if style_id is not None:
        style = get_object_or_404(Style,pk=style_id)
        action = reverse('style',kwargs={'style_id':style_id})
        button_ok = 'Save'
        title = 'Edit Style: %s' % (style.name)
        delete = 'Delete'
    else:
        action = reverse('style')
        button_ok = 'Create'
        title = 'Create Style'
        delete = None
    c = {
        'form':form,
        'action':action,
        'button_ok': button_ok,
        'title':title,
        'delete':delete
     }
    return render(request,'image_styles/bootstrap_form_modal.html',c)

@staff_member_required
def effect_form(request,effect_id=None):
    if request.method != 'POST':
        style_id = effect_id
        style = get_object_or_404(Style,pk=style_id)
        c = {
            'form':EffectForm(
                initial={'style':style.id}
             ),
             'action':reverse('effect_form'),
             'button_ok':'Create',
             'title':'New effect for %s' % (style.name),
         }
        return render(request,'image_styles/bootstrap_form_modal.html',c)
        
    else:
        if effect_id is None:
            if 'create_effect' in request.POST:
                effect_form = EffectForm(request.POST)
                if effect_form.is_valid():
                    style_id = effect_form.cleaned_data['style']
                    style = get_object_or_404(Style,pk=style_id)
                    if effect_form.cleaned_data['create_effect'] == 'crop':
                        form = CropForm(initial={'style':style,'effect':'crop'})
                    elif effect_form.cleaned_data['create_effect'] == 'enhance':
                        form = EnhanceForm(initial={'style':style,'effect':'enhance'})
                    elif effect_form.cleaned_data['create_effect'] == 'resize':
                        form = ResizeForm(initial={'style':style,'effect':'resize'})
                    elif effect_form.cleaned_data['create_effect'] == 'rotate':
                        form = RotateForm(initial={'style':style,'effect':'rotate'})
                    elif effect_form.cleaned_data['create_effect'] == 'scale':
                        form = ScaleForm(initial={'style':style,'effect':'scale'})
                    elif effect_form.cleaned_data['create_effect'] == 'round-corners':
                        form = RoundCornersForm(initial={'style':style,'effect':'round-corners'})
                    elif effect_form.cleaned_data['create_effect'] == 'smart-scale':
                        form = SmartScaleForm(initial={'style':style,'effect':'smart-scale'})
                    else:
                        raise Http404("Not Found 1")

                c = {
                     'form':form,
                     'action':reverse('effect_form'),
                     'button_ok':'Create',
                     'title':'New effect for %s' % (style.name),
                 }
                return render(request,'image_styles/bootstrap_form_modal.html',c)
            else:
                if request.POST['effect'] == 'crop':
                    form = CropForm(request.POST)
                elif request.POST['effect'] == 'enhance':
                    form = EnhanceForm(request.POST)
                elif request.POST['effect'] == 'resize':
                    form = ResizeForm(request.POST)
                elif request.POST['effect'] == 'rotate':
                    form = RotateForm(request.POST)
                elif request.POST['effect'] == 'scale':
                    form = ScaleForm(request.POST)
                elif request.POST['effect'] == 'round-corners':
                    form = RoundCornersForm(request.POST)
                elif request.POST['effect'] == 'smart-scale':
                    form = SmartScaleForm(request.POST)
                else:
                    raise Http404("Not Found 2")

                if form.is_valid():
                    form.save()
                    return HttpResponse("Effect Created!")
                c = {
                     'form':form,
                     'action':reverse('effect_form'),
                     'button_ok':'Create',
                     'title':'New effect',
                 }
                return render(request,'image_styles/bootstrap_form_modal.html',c)

        else:
            if request.POST['effect'] == 'crop':
                form = CropForm(request.POST,instance=get_object_or_404(Crop,pk=effect_id))
            elif request.POST['effect'] == 'enhance':
                form = EnhanceForm(request.POST,instance=get_object_or_404(Enhance,pk=effect_id))
            elif request.POST['effect'] == 'resize':
                form = ResizeForm(request.POST,instance=get_object_or_404(Resize,pk=effect_id))
            elif request.POST['effect'] == 'rotate':
                form = RotateForm(request.POST,instance=get_object_or_404(Rotate,pk=effect_id))
            elif request.POST['effect'] == 'scale':
                form = ScaleForm(request.POST,instance=get_object_or_404(Scale,pk=effect_id))
            elif request.POST['effect'] == 'round-corners':
                form = RoundCornersForm(request.POST,instance=get_object_or_404(RoundCorners,pk=effect_id))
            elif request.POST['effect'] == 'smart-scale':
                form = SmartScaleForm(request.POST,instance=get_object_or_404(SmartScale,pk=effect_id))
            else:
                raise Http404("Not Found 4")
            if form.is_valid():
                if 'delete' in request.POST:
                    if request.POST['effect'] == 'crop':
                        get_object_or_404(Crop,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'enhance':
                        get_object_or_404(Enhance,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'resize':
                        get_object_or_404(Resize,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'rotate':
                        get_object_or_404(Rotate,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'scale':
                        get_object_or_404(Scale,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'round-corners':
                        get_object_or_404(RoundCorners,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    elif request.POST['effect'] == 'smart-scale':
                        get_object_or_404(SmartScale,pk=effect_id).delete()
                        return HttpResponse('Deleted') 
                    else:
                        raise Http404("Not Found 5")
                
                effect = form.save()

       
            c = {
               'form': form, 
               'action':reverse('effect_form',kwargs={'effect_id':effect_id}),
               'delete':'Delete',
            } 
            return  render(request,'image_styles/generic_form.html',c)

