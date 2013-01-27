from django.db import models

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
    altitude = models.IntegerField(null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
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
    session = models.ForeignKey(Session)
    creation_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.image_file.url


class ImageMetadata(models.Model):
    image = models.ForeignKey(Image)
    key = models.CharField(max_length=200, db_index=True)
    value_type = models.CharField(max_length=200)
    boolean_value = models.NullBooleanField(null=True)
    integer_value = models.IntegerField(null=True)
    text_value = models.TextField(null=True)
    date_value = models.DateTimeField(null=True)
    decimal_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    char_value = models.CharField(max_length=200, null=True)
    creation_date = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.key + ' ' + self.image.image_file.url

