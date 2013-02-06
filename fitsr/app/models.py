from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from os.path import join
from dateutil import parser
from pyfits import getdata

# Create your models here.
class Ccd(models.Model):
    model = models.CharField(max_length=200)
    size_x = models.IntegerField()
    size_y = models.IntegerField()
    size_pixel_x = models.DecimalField(max_digits=5, decimal_places=2)
    size_pixel_y = models.DecimalField(max_digits=5, decimal_places=2)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.model


class Telescope(models.Model):
    model = models.CharField(max_length=200)
    diameter = models.IntegerField()
    focal_length = models.IntegerField()
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.model


class Site(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3)
    altitude = models.IntegerField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Observer(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Object(models.Model):
    name = models.CharField(max_length=200)
    ra = models.DecimalField(max_digits=9, decimal_places=6)
    dec = models.DecimalField(max_digits=9, decimal_places=6)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
       return self.name


class Session(models.Model):
    site = models.ForeignKey(Site)
    observer = models.ForeignKey(Observer)
    object = models.ForeignKey(Object)
    ccd = models.ForeignKey(Ccd)
    telescope = models.ForeignKey(Telescope)
    start_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
       return '%s %s %s (%s)' % (self.observer.code, self.site.code, self.object.name, self.start_date.strftime('%Y%m%d %H:%M'))


class Image(models.Model):
    RAW = 'R'
    DARK = 'D'
    FLAT = 'F'
    BIAS = 'B'
    CALIBRATED = 'C'
    IMAGE_TYPES = (
        (RAW, 'Raw'),
        (DARK, 'Dark'),
        (FLAT, 'Flat'),
        (BIAS, 'Bias'),
        (FLAT, 'Flat'),
        (CALIBRATED, 'Calibrated'),
    )
    FITS = 'FIT'
    CANON = 'CR2'
    IMAGE_FORMATS = (
        (FITS, 'FITS'),
        (CANON, 'Canon Raw'),
    )
    image_file = models.FileField(upload_to='images/%Y%m%d/')
    image_type = models.CharField(max_length=1, choices=IMAGE_TYPES, default=RAW)
    image_format = models.CharField(max_length=3, choices=IMAGE_FORMATS, default=FITS)
    date = models.DateTimeField(blank=True)
    exposure = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    session = models.ForeignKey(Session)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.image_file.url


class ImageMetadata(models.Model):
    BOOLEAN = 'B'
    INTEGER = 'I'
    TEXT = 'T'
    DATE = 'D'
    DECIMAL = '1'
    FLOAT = 'F'
    CHAR = 'C'
    VALUE_TYPES = (
        (BOOLEAN, 'Boolean'),
        (INTEGER, 'Integer'),
        (TEXT, 'Text'),
        (DATE, 'Date'),
        (DECIMAL, 'Decimal'),
        (FLOAT, 'Float'),
        (CHAR, 'Char'),
    )
    image = models.ForeignKey(Image)
    key = models.CharField(max_length=200, db_index=True)
    value_type = models.CharField(max_length=1, choices=VALUE_TYPES, default=TEXT)
    boolean_value = models.NullBooleanField(blank=True)
    integer_value = models.IntegerField(blank=True)
    text_value = models.TextField(blank=True)
    date_value = models.DateTimeField(blank=True)
    decimal_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    float_value = models.FloatField(blank=True)
    char_value = models.CharField(max_length=200, blank=True)
    creation_date = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.key

@receiver(post_save, sender=Image)
def save_image_metadata(sender, **kwargs):
    """ Stores image metadata in table """
    image = kwargs.get('instance', False)
    new = kwargs.get('created', False)
    if (image and new):
        ## TODO: update_fields support in Django 1.5
        ## if ('image_file' in updated_fields):
        ##    # Delete old entries in ImageMetadata
        ##    ImageMetadata.objects.filter(image=image).delete()
        # Read FITS headers and create rows in ImageMetadata
        image_path = join(settings.MEDIA_ROOT, image.image_file.name)
        image_data, header = getdata(image_path, header=True)
        for key in header.keys():
            metadata = ImageMetadata()
            metadata.image = image
            metadata.key = key
            value = header[key]
            if (type(value) == int):
                metadata.integer_value = value
                metadata.value_type = metadata.INTEGER
            elif (type(value) == bool):
                metadata.boolean_value = value
                metadata.value_type = metadata.BOOLEAN
            elif (type(value) == str):
                if (value.startswith('DATE')):
                    # It's a date, convert from string
                    metadata.date_value = parser.pase(value)
                    metadata.value_type = metadata.DATE
                else:
                    metadata.text_value = value
                    metadata.value_type = metadata.TEXT
            elif (type(value) == float):
                metadata.float_value = value
                metadata.value_type = metadata.FLOAT
            metadata.save()
        # Save date and exposure time in Image fields
        exptime = header.get('EXPTIME', False)
        date = header.get('DATE', False)
        if (exptime and date):
            image.exposure = exptime
            image.date = parser.parse(date)
            image.save()

