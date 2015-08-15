from django.conf.urls import include, url
from image_styles import views

urlpatterns = [
    url(r'^(?P<style_id>\d+)/(?P<path>[^\s/$.?#].*)',views.render_image,name="render_image"),
]
