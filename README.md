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
- Render via **Template** or **URL**

## Installation

Apply to an existing django project:
```
git clone https://github.com/devalfrz/django-image-styles # Download the latest version
mv django-image-styles/image_styles .
rm -r django-image-styles
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
Run migrations and the initial data of the module.
```
$ python manage.py migrate
$ python manage.py loaddata image_styles/image_styles-init.json
```
You are done! :)

## Recommendations

Just to ensure a proper server configuration, if you are prototyping using Django's `runserver`, be sure to add the following lines to your `my_project/urls.py` file as described in the [Django 1.8 documentation](https://docs.djangoproject.com/en/1.8/howto/static-files/):
```
...
from django.conf import settings
...
urlpatterns = [
   ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
It is also recommended to add the `django.core.context_processors.media` context processor to the template settings in the  `my_project/settings.py` file to be able to use the `{{MEDIA_URL}}` tag in your templates:
```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'django.core.context_processors.media',
            ]
        }
    }
]
```
> This is only a recommendation since the Django documentation is not that clear about how to do this and people have many different ways of approaching this.

## Rendering via Templates

At the top of your template:
```
...
{% load image_styles_filters %}
...
```
And now, instead of rendering the original images like so:
```
...
<img src="{{MEDIA_ROOT}}{{image}}">
...
```
Do it like this:
```
...
<img src="{{MEDIA_ROOT}}{{image|style:"Small Thumbnail"}}">
...
```
## Rendering images via URL

To add this feature you need to add the path to the ´my_project/urls.py´ file like so:

```
...
    url(r'^image_styles/', include('image_styles.urls')),
...
```
Now you can use `http://localhost:8000/image_styles/<style id>/<path to your image>` to load images with a URL. This feature is VERY useful when dealing with APIs and trying to retreive the correct styled and sized image to a mobile app.
This can also be used in a template like this:
```
...
<img src="{% url 'render_image' 1 image.name %}">
...
```
Where `1` is the style id and `image` is a `django.models.ImageField` object.

## Default Styles

The module includes 4 simple styles:
- Small Thumbnail - a 100px by 100px thumbnail.
- Gallery - a 1024px by **proportional height** image.
- Page Header - 1024px by 600px image useful for header backgrounds.
- Post Thumbnail - a 250px by 160px thumbnail.

This styles can be edited at any time if you like.

## Creating/Editing your styles

To crate a style you need to follow the next steps:
* If you have your admin interface activated go to `http://localhost:8000/admin/image_styles/style/` and create a new style.
* Then you can add effects by going to `http://localhost:8000/admin/image_styles/` and either add a *Crop*, *Enhance*, *Resize*, *Rotate* or *Scale* effect. The "weight" parameter allows for the effects to be applied on a certian order, the "heavier" the "later" they are applied.
* To call it in your template just add the filter `{% load image_styles_filters %}` and render it as `{{MEDIA_ROOT}}{{image|style:"My Custom Style"}}`.

If the style is modified in any way, it will be resetted and the new images will be re-rendered when needed.

## Limitations

- Since the system has no way of telling if the original images have been deleted or modified, the rendered images can still be shown if the right url is called. The way of preventing this (and the *correct* thing to do) is to rename the file if the image object has changed.
