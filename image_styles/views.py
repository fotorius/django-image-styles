from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse,reverse_lazy
from django.views import View
from django.views.generic.edit import FormView


import mimetypes

from .models import *
from .forms import * 
from . import utils as image_styles_utils
from .utils import get_effect_form_class 

def render_image(request,style_name,path):
    # render image
    image = image_styles_utils.render_image(style_name,path)
    content_type = mimetypes.guess_type(image.image.path)
    return HttpResponse(image.image.name,content_type=content_type[0])

class ModalForm(FormView):
    template_name = 'image_styles/bootstrap_form_modal.html'
    submit_button = 'Save'
    delete_button = ''
    title = 'Create'
    action = '.'

    def get_action(self):
        return self.action

    def get_submit_button(self):
        return self.submit_button

    def get_delete_button(self):
        return self.delete_button

    def get_title(self):
        return self.title

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.get_action()
        context['submit_button'] = self.get_submit_button()
        context['delete_button'] = self.get_delete_button()
        context['title'] = self.get_title()
        return context

class EffectFormMixin:
    effect = None
    style = None

    def dispatch(self,request,*args,**kwargs):
        self.effect_name = self.kwargs.get('effect_name')
        style_id = self.kwargs.get('style_id')
        if style_id:
            self.style = get_object_or_404(Style,id=style_id)
        effect_id = self.kwargs.get('effect_id')
        if effect_id and self.effect_name:
            from image_styles import models
            self.effect = get_object_or_404(getattr(models,self.effect_name),id=effect_id)
        return super().dispatch(request,*args,**kwargs)

    def get_form_class(self):
        form_class = get_effect_form_class(self.effect_name)
        if form_class:
            return form_class
        raise Http404("Not Found")

    def get_form_kwargs(self,*args,**kwargs):
        data = super().get_form_kwargs(*args,**kwargs)
        if self.effect:
            data['instance'] = self.effect
        return data

    def get_action(self):
        if self.style:
            return reverse(
                'image_styles:effect_create',
                kwargs={'style_id':self.style.id,'effect_name':self.effect_name}
            )
        return reverse(
            'image_styles:effect_update',
            kwargs={'effect':self.effect.id,'effect_name':self.effect_name}
        )

    def form_valid(self,form):
        form.save()
        return HttpResponse("Effect Created!")
        
    def delete(self,*args,**kwargs):
        if self.effect:
            self.effect.delete()
            return HttpResponse("Effect Removed!")
        return HttpResponse("Delete failed!")

class StyleFormMixin:
    style = None
    form_class = StyleForm

    def dispatch(self,request,*args,**kwargs):
        style_id = self.kwargs.get('style_id')
        if style_id:
            self.style = get_object_or_404(Style,id=style_id)
            self.delete_button = 'Delete'
        return super().dispatch(request,*args,**kwargs)

    def get_form_kwargs(self,*args,**kwargs):
        data = super().get_form_kwargs(*args,**kwargs)
        if self.style:
            data['instance'] = self.style
        return data

    def get_action(self):
        if self.style:
            return reverse(
                'image_styles:style_update',
                kwargs={'style_id':self.style.id}
            )
        return reverse('image_styles:style_create')

    def form_valid(self,form):
        form.save()
        return HttpResponse("Style Created!")
        
    def delete(self,*args,**kwargs):
        if self.style:
            self.style.delete()
            return HttpResponse("Style Removed!")
        return HttpResponse("Delete failed!")


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
    if request.method == 'DELETE' and style_id:
        style = get_object_or_404(Style,pk=style_id)
        style.delete()
        return HttpResponse('Style Deleted!')
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
                
                form.save()
                return HttpResponse('Style Saved!')
    else:
        if style_id is None:
            form = StyleForm()
        else:
            form = StyleForm(instance=get_object_or_404(Style,pk=style_id))

    if style_id is not None:
        style = get_object_or_404(Style,pk=style_id)
        action = reverse('image_styles:style_update',kwargs={'style_id':style_id})
        submit_button = 'Save'
        title = 'Edit Style: %s' % (style.name)
        delete = 'Delete'
    else:
        action = reverse('image_styles:style_create')
        submit_button = 'Create'
        title = 'Create Style'
        delete = None
    c = {
        'form':form,
        'action':action,
        'submit_button': submit_button,
        'title':title,
        'delete_button':delete
     }
    return render(request,'image_styles/bootstrap_form_modal.html',c)

@method_decorator(staff_member_required(),name='dispatch')
class EffectCreateInitView(ModalForm):
    form_class = EffectForm
    submit_button = 'Create'

    def dispatch(self,request,*args,**kwargs):
        self.style = get_object_or_404(Style,id=self.kwargs.get('style_id'))
        return super().dispatch(request,*args,**kwargs)

    def get_form(self,**kwargs):
        form = super().get_form(**kwargs)
        form.initial['style'] = self.style
        return form

    def get_action(self):
        if self.action == '.':
            return reverse('image_styles:effect_create_init',kwargs={'style_id':self.style.id})
        return self.action

    def form_valid(self,form):
        effect_name = form.cleaned_data.get('effect')
        self.form_class = get_effect_form_class(effect_name)
        self.action = reverse(
            'image_styles:effect_create',
            kwargs={'style_id':self.style.id,'effect_name':effect_name}
        )
        self.request.method = 'GET'
        return super().get(self.request,style_id=self.style.id)

@method_decorator(staff_member_required(),name='dispatch')
class EffectCreateView(EffectFormMixin,ModalForm):
    def get_form(self,**kwargs):
        form = super().get_form(**kwargs)
        form.initial['style'] = self.style
        return form

@method_decorator(staff_member_required(),name='dispatch')
class EffectUpdateView(EffectFormMixin,ModalForm):
    pass

@method_decorator(staff_member_required(),name='dispatch')
class StyleView(StyleFormMixin,ModalForm):
    pass

