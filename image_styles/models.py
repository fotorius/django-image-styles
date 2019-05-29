from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image,ImageEnhance,ImageDraw # PIL
from django.utils.translation import ugettext_lazy as _
import os,re

def get_upload_file_name(instance,filename):
    return "image_styles/%s/%s" % (instance.style.name,filename)


class StyleMixin:
    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super().save(*args,**kwargs)
        self.style.delete_images()
        return sv
    
    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super().delete(*args,**kwargs)

    def __str__(self):
        return self.style.name  

    def get_name(self):
        """
        Get style name
        """
        name = ''
        r = re.search(r'models\.(?P<name>\w+)',str(type(self)))
        if r:
            name = r.group('name')
        return name

class Style(models.Model):
    name = models.SlugField(_('name'),max_length=127,unique=True)
    
    def delete_images(self):
        ImageStyle.objects.filter(style=self).delete()

    def get_effects(self):
        effects = []
        effect_objects = [Crop,Enhance,Resize,Rotate,Scale,SmartScale,RoundCorners]
        for effect_object in effect_objects:
            es = effect_object.objects.filter(style=self)
            for e in es:
                re_type = re.match(r"<class '\w+.models.(\w+)'>",str(type(e)))
                if len(re_type.groups()) == 1:
                    name = re_type.group(1)
                else:
                    name = ''
                effects.append({
                    'weight':e.weight,
                    'object':e,
                    'name':name,
                 })
        effects = sorted(effects, key=lambda k: k['weight'])
        return effects

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class ImageStyle(models.Model):
    name = models.CharField(_('name'),max_length=511)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    image = models.ImageField(_('image'),upload_to=get_upload_file_name,null=True,blank=True)
    def __str__(self):
        return "%s - %s" % (self.style.name,self.name)

    def apply_effects(self,effects):
        orig = Image.open(os.path.join(settings.MEDIA_ROOT,self.name))
        if orig.mode != 'RGBA':
          orig = orig.convert('RGBA')

        # Fix orientation
        orientation = False
        try:
            exif=dict((ExifTags.TAGS[k], v) for k, v in orig._getexif().items() if k in ExifTags.TAGS)
            if exif.get('Orientation') == 8:
                orig=orig.rotate(90, expand=True)
                orientation = True
            if exif.get('Orientation') == 6:
                orig=orig.rotate(270, expand=True)
                orientation = True
        except AttributeError:
            pass # No EXIF

        # Handle transparency
        if orientation:
            size = orig.size
        else:
            size = orig.size
        im = Image.new('RGBA', orig.size, (0,0,0,0))
        im.paste(orig)

        for effect in effects:
            im = effect['object'].render(im)
        
        try:
            im.save(self.image.path)
        except IOError:
            # Not the most elegant way to handle RGBA jpgs, but works
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])
            im = background
            im.save(self.image.path)

        
    def save(self,*args,**kwargs):
        if self.id is None:
            new_image = get_upload_file_name(self,self.name)
            if not os.path.exists(os.path.dirname(os.path.join(settings.MEDIA_ROOT,new_image))):
                os.makedirs(os.path.dirname(os.path.join(settings.MEDIA_ROOT,new_image)))
            self.image = new_image
        self.apply_effects(self.style.get_effects())
        return super().save(*args,**kwargs)

class Crop(StyleMixin,models.Model):
    ANCHORS = (
        (1,'top-left'),
        (2,'top-center'),
        (3,'top-right'),
        (4,'middle-left'),
        (5,'middle-center'),
        (6,'middle-right'),
        (7,'bottom-left'),
        (8,'bottom-center'),
        (9,'bottom-right'),
    )
    width = models.IntegerField(_('width'))
    height = models.IntegerField(_('height'))
    anchor = models.IntegerField(_('anchor'),choices=ANCHORS,default=5)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im):
        w, h = im.size
        if self.anchor == 1:
            box = (0,0,self.width,self.height)
        elif self.anchor == 2:
            box = ((w/2)-(self.width/2),0,(self.width/2)+(w/2),self.height)
        elif self.anchor == 3:
            box = (w-self.width,0,w,self.height)
        elif self.anchor == 4:
            box = (0,(h/2)-(self.height/2),self.width,(self.height/2)+(h/2))
        elif self.anchor == 5:
            box = ((w/2)-(self.width/2),(h/2)-(self.height/2),(self.width/2)+(w/2),(self.height/2)+(h/2))
        elif self.anchor == 6:
            box = (w-self.width,(h/2)-(self.height/2),w,(self.height/2)+(h/2))
        elif self.anchor == 7:
            box = (0,h-self.height,self.width,h)
        elif self.anchor == 8:
            box = ((w/2)-(self.width/2),h-self.height,(self.width/2)+(w/2),h)
        elif self.anchor == 9:
            box = (w-self.width,h-self.height,w,h)
        return im.crop(box)
        

class Enhance(StyleMixin,models.Model):
    CONTRASTS = zip( range(-100,101), range(-100,101) )
    SHARPNESSES = zip( range(-100,101), range(-100,101) )
    BRIGHTNESSES = zip( range(-100,101), range(-100,101) )
    COLORS = zip( range(-100,101), range(-100,101) )
    contrast = models.IntegerField(_('contrast'),choices=CONTRASTS,default=0)
    brightness = models.IntegerField(_('brightness'),choices=BRIGHTNESSES,default=0)
    color = models.IntegerField(_('color'),choices=COLORS,default=0)
    sharpness = models.IntegerField(_('sharpness'),choices=SHARPNESSES,default=0)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im): 
        if self.color:
            if self.color > 100:
                color = 2
            elif self.color < -100:
                color = 0
            else:
                color = float(self.color+100)/100
            converter = ImageEnhance.Color(im)
            im = converter.enhance(color)
        
        if self.contrast:
            if self.contrast > 100:
                contrast = 2
            elif self.contrast < -100:
                contrast = 0
            else:
                contrast = float(self.contrast+100)/100
            converter = ImageEnhance.Contrast(im)
            im = converter.enhance(contrast)
        
        if self.brightness:
            if self.brightness > 100:
                brightness = 2
            elif self.brightness < -100:
                brightness = 0
            else:
                brightness = float(self.brightness+100)/100
            converter = ImageEnhance.Brightness(im)
            im = converter.enhance(brightness)
        
        if self.sharpness:
            if self.sharpness > 100:
                sharpness = 2
            elif self.sharpness < -100:
                sharpness = 0
            else:
                sharpness = float(self.sharpness+100)/100

            converter = ImageEnhance.Sharpness(im)
            im = converter.enhance(sharpness)

        return im
            

class Resize(StyleMixin,models.Model):
    width = models.IntegerField(_('width'))
    height = models.IntegerField(_('height'))
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im):
        return im.resize((self.width,self.height))
        

class RoundCorners(StyleMixin,models.Model):
    radius = models.IntegerField(_('radius'))
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im):
        circle = Image.new('L', (self.radius * 2, self.radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, self.radius * 2, self.radius * 2), fill=255)
        alpha = Image.new('L', im.size, "white")
        w, h = im.size
        alpha.paste(circle.crop((0, 0, self.radius, self.radius)), (0, 0))
        alpha.paste(circle.crop((0, self.radius, self.radius, self.radius * 2)), (0, h - self.radius))
        alpha.paste(circle.crop((self.radius, 0, self.radius * 2, self.radius)), (w - self.radius, 0))
        alpha.paste(circle.crop((self.radius, self.radius, self.radius * 2, self.radius * 2)), (w - self.radius, h - self.radius))
        im.putalpha(alpha)
        return im

class Rotate(StyleMixin,models.Model):
    ANGLES = zip( range(90,360,90), range(90,360,90) )
    angle = models.IntegerField(_('angle'),choices=ANGLES,default=0)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im):
        return im.rotate(-self.angle)

class Scale(StyleMixin,models.Model):
    MODES = (
        (Image.NEAREST,'Nearest'),
        (Image.ANTIALIAS,'Antialias'),
        (Image.BILINEAR,'Bilinear'),
        (Image.BICUBIC,'Bicubic'),
    )
    mode = models.PositiveSmallIntegerField(_('mode'),choices=MODES,default=1)
    width = models.IntegerField(_('width'),blank=True,null=True)
    height = models.IntegerField(_('height'),blank=True,null=True)
    allow_upscale = models.BooleanField(_('allow_upscale'),default=True)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)

    def render(self,im):
        w, h = im.size
        if self.height is None:
            width = self.width
            height = int(float(h)/w*width)
        elif self.width is None:
            height = self.height
            width = int(float(w)/h*height)
        else:
            height = self.height
            width = self.width

        if self.allow_upscale:
            im = im.resize((width,height),self.mode)
        else:
            if w > width and h > height:
                im = im.resize((width,height),self.mode)
        return im


class SmartScale(StyleMixin,models.Model):
    MODES = (
        (Image.NEAREST,'Nearest'),
        (Image.ANTIALIAS,'Antialias'),
        (Image.BILINEAR,'Bilinear'),
        (Image.BICUBIC,'Bicubic'),
    )
    mode = models.PositiveSmallIntegerField(_('mode'),choices=MODES,default=1)
    width = models.IntegerField(_('width'))
    height = models.IntegerField(_('height'))
    allow_upscale = models.BooleanField(_('allow_upscale'),default=True)
    largest = models.BooleanField(_('largest'),help_text=('Constraint by largest dimension.'),default=True)
    style = models.ForeignKey(Style,verbose_name=_('style'),on_delete=models.CASCADE)
    weight = models.IntegerField(_('weight'),default=0)


    def render(self,im):
        w, h = im.size
        im_prop = float(h)/float(w)
        scale_prop = self.width/self.height

        if self.largest:
            if im_prop > scale_prop:
                width = self.width
                height = int(float(h)/w*width)
            else:
                height = self.height
                width = int(float(w)/h*height)
        else:
            if im_prop < scale_prop:
                width = self.width
                height = int(float(h)/w*width)
            else:
                height = self.height
                width = int(float(w)/h*height)

        if self.allow_upscale:
            im = im.resize((width,height),self.mode)
        else:
            if w > width and h > height:
                im = im.resize((width,height),self.mode)
        return im
