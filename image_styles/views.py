from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse,reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

import mimetypes

from .models import Style
from .forms import EffectForm,StyleForm 
from .utils import get_effect_form_class,render_image 

class RenderImageView(View):
    def get(self,request,style_name,path):
        image = render_image(style_name,path)
        content_type = mimetypes.guess_type(image.image.path)
        f = open(image.image.path,'rb')
        r = HttpResponse(f,content_type=content_type[0])
        f.close()
        return r


class ModalForm(FormView):
    template_name = 'image_styles/modal_form.html'
    submit_button = _('Save')
    delete_button = ''
    title = _('Create')
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
    title = _('Create Effect')
    submit_button = _('Create')

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

    def get_submit_button(self):
        if self.effect:
            return _('Update')
        return super().get_submit_button()

    def get_title(self):
        if self.effect:
            return _('Update Effect')
        return super().get_title()

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
        return HttpResponse(_('Effect Created!'))
        
    def delete(self,*args,**kwargs):
        if self.effect:
            self.effect.delete()
            return HttpResponse(_('Effect Removed!'))
        return HttpResponse(_('Delete failed!'))

class StyleFormMixin:
    style = None
    form_class = StyleForm

    def dispatch(self,request,*args,**kwargs):
        style_id = self.kwargs.get('style_id')
        if style_id:
            self.style = get_object_or_404(Style,id=style_id)
            self.delete_button = _('Delete')
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

    def get_submit_button(self):
        if self.style:
            return _('Update')
        return super().get_submit_button()

    def get_title(self):
        if self.style:
            return _('Update Style')
        return super().get_title()

    def form_valid(self,form):
        form.save()
        return HttpResponse(_('Style Created!'))
        
    def delete(self,*args,**kwargs):
        if self.style:
            self.style.delete()
            return HttpResponse(_('Style Removed!'))
        return HttpResponse(_('Delete failed!'))


@method_decorator(staff_member_required(),name='dispatch')
class ManageImageStylesView(TemplateView):
    template_name = 'image_styles/home.html'

    def get_image_styles(self):
        ims = []
        for s in Style.objects.all():
            effects = s.get_effects()
            for i in range(len(effects)):
                form = get_effect_form_class(effect_model=effects[i]['object']) 
                if form:
                    effects[i]['form'] = form(instance=effects[i]['object'])
                    effects[i]['action'] = reverse(
                        'image_styles:effect_update',
                        kwargs = {
                            'effect_id':effects[i]['object'].id,
                            'effect_name':effects[i]['object'].get_name()
                        }
                    )
            ims.append({
                'style':s,
                'effects':effects,
            })

        return ims

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['styles'] = self.get_image_styles()
        return context

@method_decorator(staff_member_required(),name='dispatch')
class EffectCreateInitView(ModalForm):
    form_class = EffectForm
    submit_button = _('Next')
    title = _('Select Effect')

    def dispatch(self,request,*args,**kwargs):
        self.style = get_object_or_404(Style,id=self.kwargs.get('style_id'))
        return super().dispatch(request,*args,**kwargs)

    def get_form(self,**kwargs):
        form = super().get_form(**kwargs)
        form.initial['style'] = self.style
        return form

    def get_submit_button(self):
        if self.form_class != EffectForm:
            return _('Create')
        return super().get_submit_button()

    def get_title(self):
        if self.form_class != EffectForm:
            return _('Create Effect')
        return super().get_title()

    def get_action(self):
        if self.action == '.':
            return reverse('image_styles:effect_create_init',kwargs={'style_id':self.style.id})
        return self.action

    def form_valid(self,form):
        effect_name = form.cleaned_data.get('effect')
        self.form_class = get_effect_form_class(effect_name=effect_name)
        self.action = reverse(
            'image_styles:effect_create',
            kwargs={'style_id':self.style.id,'effect_name':effect_name}
        )
        self.request.method = 'GET'
        return super().get(self.request,style_id=self.style.id)

@method_decorator(staff_member_required(),name='dispatch')
class EffectCreateView(EffectFormMixin,ModalForm):
    title = _('Create Effect')
    submit_button = _('Create')

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

