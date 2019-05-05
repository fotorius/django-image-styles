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
- Render in **Templates**
- Effect Management Utility

## Installation

If you haven't install libjpeg-dev:
```
sudo apt-get install libjpeg-dev
```

Install into the current evnironment:
```
pip install git+https://github.com/devalfrz/django-image-styles
# pip install django-image-styles # PyPi implementation currently not working properly
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
    path('image_styles/',include('image_styles.urls',namespace='image_styles')),
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

<img src="{{MEDIA_URL}}{{image|style:'small_thumbnail'}}" alt="Image Description">
...
```

## Manage your styles

To crate a style you need to follow the next steps:
* To access the image styles admin interface you need to add the `path('image_styles/', include('image_styles.urls',namespace='image_styles')),` path to your root `urls.py` file, then simply go to `http://localhost:8000/image_styles/`.

If a style is modified in any way, it will be resetted and the new images will be re-rendered when needed. The admin site is **only available for staff users**.

## Limitations

- Since the system has no way of telling if the original images have been deleted or modified, the rendered images can still be shown if the right url is called. The way of preventing this (and the *correct* thing to do) is to rename the file if the image object has changed.
- Images with no alpha channels may be filled with a black background.
- The latest version of this software will only work with local files, I haven't work on the _bucket_ implementation yet.
