from django.conf.urls import include, url
from image_styles import views

urlpatterns = [
    url(r'^(?P<style_name>[\w_-]+)/(?P<path>[^\s/$.?#].*)',views.render_image,name="render_image"),
    url(r'^$',views.manage_image_styles,name="manage_image_styles"),
    url(r'^effect_form(?:/(?P<effect_id>\d+))?/$',views.effect_form,name='effect_form'),
    url(r'^style(?:/(?P<style_id>[\w_-]+))?/$',views.style,name='style'),
]
