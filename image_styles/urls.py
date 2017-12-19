from django.urls import include, re_path
from . import views

urlpatterns = [
    re_path(r'^$',views.manage_image_styles,name="manage_image_styles"),
    re_path(r'^effect_form(?:/(?P<effect_id>\d+))?/$',views.effect_form,name='effect_form'),
    re_path(r'^style(?:/(?P<style_id>\d+))?/$',views.style,name='style'),
    re_path(r'^(?P<style_name>[\w_-]+)/(?P<path>[^\s/$.?#].*)',views.render_image,name="render_image"),
]
