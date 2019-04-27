# django-image-styles
Simple, fast and easy-to-use tool for pre-rendering images on Django.

## Features
- Renders images and stores them so they don't need to be re-rendered.
- Doesn't modify the original images.
- Completely independend from other models.
- Has the following effects (based on Pillow):
  - Crop
  - Enhance
  - Resize
  - Rotate
  - Scale Proportionally
  - Scale by width or height (Smart Scale)
  - Round Corners
- Render in **Templates** or via **URL**
- Effect Management Utility

## Installation

If you haven't install libjpeg-dev:
```
sudo apt-get install libjpeg-dev
```

Apply to an existing django project:
```
pip install django-image-styles
```
Add to installed apps in your project `settings.py` and the MEDIA settings:
```
INSTALLED_APPS = (
    ...
    image_styles,
    ...
)
...
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
```
Include the _image styles_ path in the ´my_project/urls.py´ file:

```
...
    path('',include('image_styles.urls',namespace='image_styles')),
...
```
Run migrations and the initial data of the module.
```
python manage.py migrate
```
You are done! :)

## Recommendations

Just to ensure a proper server configuration, if you are prototyping using Django's `runserver`, be sure to add the following lines to your `my_project/urls.py` file as described in the [Django 2.2 documentation](https://docs.djangoproject.com/en/2.2/howto/static-files/):
```
...
from django.conf.urls.static import static
from django.urls import include
from django.conf import settings
...
urlpatterns = [
   ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
## Rendering images via Templates

At the top of your template:
```
...
{% load image_styles %}
...

```
### Method 1
```
...
<img src="{{MEDIA_URL}}{{image|style:'small_thumbnail'}}" alt="Image Description">
...
```
### Method 2
```
...
{% render_image image 'small_thumbnail' 'Optional Image Description' %}
...
```
Or you can simply add the ID of the format:
```
...
{% render_image image 1 %}
...
```
## Rendering images via URL

You can use `http://localhost:8000/image_styles/<style id>/<path to your image>` to load images with a URL. This feature is VERY useful when dealing with APIs and trying to retreive the correct styled and sized image to a mobile app.
This can also be used in a template like this:
```
...
<img src="{% url 'image_styles:render_image' 1 image.name %}">
...
```
Where `1` is the style id and `image` is a `django.models.ImageField` object.

## Rendering images via Views

This is useful when outputting images for API resources.

Import the *reverse* function at the top of the `views.py` file.
```
...
from django.urls import reverse
from image_styles.utils import render_image
from django.conf import settings
...
```
Finally you can get the image like so:
```
rendered_image = render_image(1,image.name)
image_url = settings.MEDIA_URL[:-1]+reverse(
    'image_styles:render_image',
    kwargs={
        'style_name':'thumbnail',
        'path':image.name
    }
)
```
Where `1` is the style id and `image` is a `django.models.ImageField` object.

## Manage your styles

To crate a style you need to follow the next steps:
* As shown in the **Rendering images via URL** section, you need to add the `path('image_styles/', include('image_styles.urls',namespace='image_styles')),` path to your root `urls.py` file.
* To access the image styles admin interface simply go to `http://localhost:8000/image_styles/`.

If a style is modified in any way, it will be resetted and the new images will be re-rendered when needed. The admin site is **only available for staff users**.

## Limitations

- Since the system has no way of telling if the original images have been deleted or modified, the rendered images can still be shown if the right url is called. The way of preventing this (and the *correct* thing to do) is to rename the file if the image object has changed.
- Images with no alpha channels may be filled with a black background.
- The latest version of this software will only work with local files, I haven't work on the _bucket_ implementation yet.
