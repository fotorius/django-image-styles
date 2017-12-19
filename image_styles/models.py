from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image,ImageEnhance,ImageDraw # PIL
import os,re

def get_upload_file_name(instance,filename):
    return "image_styles/%s/%s" % (instance.style.name,filename)


class Style(models.Model):
    name = models.SlugField(max_length=127,unique=True)
    
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
        return '%d: %s' % (self.id,self.name)

    class Meta:
        ordering = ['id']

class ImageStyle(models.Model):
    name = models.CharField(max_length=511)
    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_file_name,null=True,blank=True)
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
            if type(effect['object']) is Crop:
                w, h = im.size
                if effect['object'].anchor == 1:
                    box = (0,0,effect['object'].width,effect['object'].height)
                elif effect['object'].anchor == 2:
                    box = ((w/2)-(effect['object'].width/2),0,(effect['object'].width/2)+(w/2),effect['object'].height)
                elif effect['object'].anchor == 3:
                    box = (w-effect['object'].width,0,w,effect['object'].height)
                elif effect['object'].anchor == 4:
                    box = (0,(h/2)-(effect['object'].height/2),effect['object'].width,(effect['object'].height/2)+(h/2))
                elif effect['object'].anchor == 5:
                    box = ((w/2)-(effect['object'].width/2),(h/2)-(effect['object'].height/2),(effect['object'].width/2)+(w/2),(effect['object'].height/2)+(h/2))
                elif effect['object'].anchor == 6:
                    box = (w-effect['object'].width,(h/2)-(effect['object'].height/2),w,(effect['object'].height/2)+(h/2))
                elif effect['object'].anchor == 7:
                    box = (0,h-effect['object'].height,effect['object'].width,h)
                elif effect['object'].anchor == 8:
                    box = ((w/2)-(effect['object'].width/2),h-effect['object'].height,(effect['object'].width/2)+(w/2),h)
                elif effect['object'].anchor == 9:
                    box = (w-effect['object'].width,h-effect['object'].height,w,h)
                im = im.crop(box)
            elif type(effect['object']) is Enhance:
                
                if effect['object'].color > 100:
                    color = 2
                elif effect['object'].color < -100:
                    color = 0
                else:
                    color = float(effect['object'].color+100)/100
                converter = ImageEnhance.Color(im)
                im = converter.enhance(color)
                
                if effect['object'].contrast > 100:
                    contrast = 2
                elif effect['object'].contrast < -100:
                    contrast = 0
                else:
                    contrast = float(effect['object'].contrast+100)/100
                converter = ImageEnhance.Contrast(im)
                im = converter.enhance(contrast)
                
                if effect['object'].brightness > 100:
                    brightness = 2
                elif effect['object'].brightness < -100:
                    brightness = 0
                else:
                    brightness = float(effect['object'].brightness+100)/100
                converter = ImageEnhance.Brightness(im)
                im = converter.enhance(brightness)
                
                if effect['object'].sharpness > 100:
                    sharpness = 2
                elif effect['object'].sharpness < -100:
                    sharpness = 0
                else:
                    sharpness = float(effect['object'].sharpness+100)/100
               
                converter = ImageEnhance.Sharpness(im)
                im = converter.enhance(sharpness)
                    

            elif type(effect['object']) is Resize:
                im = im.resize((effect['object'].width,effect['object'].height))
            elif type(effect['object']) is Rotate:
                im = im.rotate(-effect['object'].angle)
            elif type(effect['object']) is Scale:
                w, h = im.size
                if effect['object'].height is None:
                    width = effect['object'].width
                    height = int(float(h)/w*width)
                elif effect['object'].width is None:
                    height = effect['object'].height
                    width = int(float(w)/h*height)
                else:
                    height = effect['object'].height
                    width = effect['object'].width

                if effect['object'].allow_upscale:
                    im = im.resize((width,height),effect['object'].mode)
                else:
                    if w > width and h > height:
                        im = im.resize((width,height),effect['object'].mode)
            elif type(effect['object']) is SmartScale:
                w, h = im.size
                im_prop = float(h)/float(w)

                if im_prop > 1.0:
                    width = effect['object'].width
                    height = int(float(h)/w*width)
                else:
                    height = effect['object'].height
                    width = int(float(w)/h*height)

                if effect['object'].allow_upscale:
                    im = im.resize((width,height),effect['object'].mode)
                else:
                    if w > width and h > height:
                        im = im.resize((width,height),effect['object'].mode)
            elif type(effect['object']) is RoundCorners:
                circle = Image.new('L', (effect['object'].radius * 2, effect['object'].radius * 2), 0)
                draw = ImageDraw.Draw(circle)
                draw.ellipse((0, 0, effect['object'].radius * 2, effect['object'].radius * 2), fill=255)
                alpha = Image.new('L', im.size, "white")
                w, h = im.size
                alpha.paste(circle.crop((0, 0, effect['object'].radius, effect['object'].radius)), (0, 0))
                alpha.paste(circle.crop((0, effect['object'].radius, effect['object'].radius, effect['object'].radius * 2)), (0, h - effect['object'].radius))
                alpha.paste(circle.crop((effect['object'].radius, 0, effect['object'].radius * 2, effect['object'].radius)), (w - effect['object'].radius, 0))
                alpha.paste(circle.crop((effect['object'].radius, effect['object'].radius, effect['object'].radius * 2, effect['object'].radius * 2)), (w - effect['object'].radius, h - effect['object'].radius))
                im.putalpha(alpha)
        
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
        return super(ImageStyle,self).save(*args,**kwargs)

class Crop(models.Model):
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
    width = models.IntegerField()
    height = models.IntegerField()
    anchor = models.IntegerField(choices=ANCHORS,default=5)
    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)
    
    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1] 
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(Crop,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv
    
    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(Crop,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name                


class Enhance(models.Model):
    CONTRASTS = zip( range(-100,101), range(-100,101) )
    SHARPNESSES = zip( range(-100,101), range(-100,101) )
    BRIGHTNESSES = zip( range(-100,101), range(-100,101) )
    COLORS = zip( range(-100,101), range(-100,101) )
    contrast = models.IntegerField(choices=CONTRASTS,default=0)
    brightness = models.IntegerField(choices=BRIGHTNESSES,default=0)
    color = models.IntegerField(choices=COLORS,default=0)
    sharpness = models.IntegerField(choices=SHARPNESSES,default=0)

    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)
    
    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(Enhance,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv
    
    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(Enhance,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  

class Resize(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()

    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(Resize,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv
    
    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(Resize,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  

class RoundCorners(models.Model):
    radius = models.IntegerField()
    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(RoundCorners,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv
    
    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(RoundCorners,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  

class Rotate(models.Model):
    ANGLES = zip( range(90,360,90), range(90,360,90) )
    angle = models.IntegerField(choices=ANGLES,default=0)

    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(Rotate,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv

    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(Rotate,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  

class Scale(models.Model):
    MODES = (
        (Image.NEAREST,'Nearest'),
        (Image.ANTIALIAS,'Antialias'),
        (Image.BILINEAR,'Bilinear'),
        (Image.BICUBIC,'Bicubic'),
    )
    mode = models.PositiveSmallIntegerField(choices=MODES,default=1)
    width = models.IntegerField(blank=True,null=True)
    height = models.IntegerField(blank=True,null=True)
    allow_upscale = models.BooleanField(default=True)

    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(Scale,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv

    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(Scale,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  



class SmartScale(models.Model):
    MODES = (
        (Image.NEAREST,'Nearest'),
        (Image.ANTIALIAS,'Antialias'),
        (Image.BILINEAR,'Bilinear'),
        (Image.BICUBIC,'Bicubic'),
    )
    mode = models.PositiveSmallIntegerField(choices=MODES,default=1)
    width = models.IntegerField()
    height = models.IntegerField()
    allow_upscale = models.BooleanField(default=True)

    style = models.ForeignKey(Style,on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)

    def save(self,*args,**kwargs):
        if not self.id and self.weight == 0:
            es = self.style.get_effects()[::-1]
            if len(es) is not 0:
                self.weight = es[0]['weight']+1
        sv = super(SmartScale,self).save(*args,**kwargs)
        self.style.delete_images()
        return sv

    def delete(self,*args,**kwargs):
        self.style.delete_images()
        super(SmartScale,self).delete(*args,**kwargs)

    def __unicode__(self):
        return self.style.name  

