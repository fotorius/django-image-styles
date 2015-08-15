from django.contrib import admin
from image_styles.models import *

admin.site.register(Style)
admin.site.register(Crop)
admin.site.register(Enhance)
admin.site.register(Resize)
admin.site.register(Scale)
admin.site.register(Rotate)
