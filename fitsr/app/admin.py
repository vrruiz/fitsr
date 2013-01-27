from django.contrib import admin
from fitsr.app.models import Ccd, Telescope, Observer, Object, Site, Session, Image, ImageMetadata

admin.site.register(Ccd)
admin.site.register(Telescope)
admin.site.register(Observer)
admin.site.register(Object)
admin.site.register(Site)
admin.site.register(Session)
admin.site.register(Image)
admin.site.register(ImageMetadata)
