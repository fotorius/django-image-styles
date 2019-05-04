from django.urls import include, re_path,path
from . import views

app_name = 'image_styles'

urlpatterns = [
    re_path(r'^$',views.manage_image_styles,name="manage_image_styles"),
    path('effect/init/<int:style_id>/',views.EffectCreateInit.as_view(),name='effect_create_init'),
    path('effect/<int:style_id>/<slug:effect_name>/',views.EffectCreate.as_view(),name='effect_create'),
    path('effect/<int:effect_id>/<slug:effect_name>/update/',views.EffectUpdate.as_view(),name='effect_update'),
    path('style/',views.style,name='style_create'),
    path('style/<int:style_id>/',views.style,name='style_update'),
    re_path(r'^(?P<style_name>[\w_-]+)/(?P<path>[^\s/$.?#].*)',views.render_image,name="render_image"),
]
