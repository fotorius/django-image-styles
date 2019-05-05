from django.urls import include, re_path,path
from .views import EffectUpdateView,EffectCreateView,EffectCreateInitView
from .views import StyleView,RenderImageView
from .views import ManageImageStylesView

app_name = 'image_styles'

urlpatterns = [
    path('',ManageImageStylesView.as_view(),name='manage_image_styles'),
    path('effect/init/<int:style_id>/',EffectCreateInitView.as_view(),name='effect_create_init'),
    path('effect/<int:style_id>/<slug:effect_name>/',EffectCreateView.as_view(),name='effect_create'),
    path('effect/<int:effect_id>/<slug:effect_name>/update/',EffectUpdateView.as_view(),name='effect_update'),
    path('style/',StyleView.as_view(),name='style_create'),
    path('style/<int:style_id>/',StyleView.as_view(),name='style_update'),
    re_path(r'^(?P<style_name>[\w_-]+)/(?P<path>[^\s/$.?#].*)',RenderImageView.as_view(),name='render_image'),
]
