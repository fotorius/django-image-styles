from django import forms

from .models import *

EFFECT_CHOICES = (
  ('crop','Crop'),
  ('enhance','Enhance'),
  ('resize','Resize'),
  ('rotate','Rotate'),
  ('round-corners','Round Corners'),
  ('scale','Scale'),
  ('smart-scale','Smart Scale'),
)

class RoundCornersForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='round-corners',
    )
    class Meta:
        model = RoundCorners
        fields = ['style','radius','weight']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class CropForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='crop',
    )
    class Meta:
        model = Crop
        fields = ['style','height','width','anchor','weight']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class EnhanceForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='enhance',
    )
    class Meta:
        model = Enhance
        fields = ['style','contrast','brightness','color','sharpness','weight']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class ResizeForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='resize',
    )
    class Meta:
        model = Resize
        fields = ['style','height','width','weight']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class RotateForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='rotate',
    )
    class Meta:
        model = Rotate
        fields = ['style','angle','weight']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class ScaleForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='scale',
    )
    class Meta:
        model = Scale
        fields = ['style','height','width','allow_upscale','weight','mode']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }
class SmartScaleForm(forms.ModelForm):
    effect = forms.CharField(
      widget=forms.HiddenInput(),
      initial='smart-scale',
    )
    class Meta:
        model = SmartScale
        fields = ['style','height','width','allow_upscale','weight','mode']
        widgets = {
            'style':forms.HiddenInput,
            'weight':forms.HiddenInput,
        }

class EffectForm(forms.Form):
   create_effect = forms.ChoiceField(choices=EFFECT_CHOICES)
   style = forms.CharField(widget=forms.HiddenInput())
   
class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        exclude = []
