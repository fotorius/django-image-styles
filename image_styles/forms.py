from django import forms

from .models import *

EFFECT_CHOICES = (
  ('Crop','Crop'),
  ('Enhance','Enhance'),
  ('Resize','Resize'),
  ('Rotate','Rotate'),
  ('RoundCorners','Round Corners'),
  ('Scale','Scale'),
  ('SmartScale','Smart Scale'),
)

class EffectMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['style'].widget = forms.HiddenInput()
        self.fields['weight'].widget = forms.HiddenInput()

class RoundCornersForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = RoundCorners
        fields = '__all__'

class CropForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = Crop
        fields = '__all__'

class EnhanceForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = Enhance
        fields = '__all__'

class ResizeForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = Resize
        fields = '__all__'

class RotateForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = Rotate
        fields = '__all__'

class ScaleForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = Scale
        fields = '__all__'

class SmartScaleForm(EffectMixin,forms.ModelForm):
    class Meta:
        model = SmartScale
        fields = '__all__'

class EffectForm(forms.Form):
   effect = forms.ChoiceField(choices=EFFECT_CHOICES)
   style = forms.ModelChoiceField(queryset=Style.objects.all(),widget=forms.HiddenInput())
   
class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        exclude = []
