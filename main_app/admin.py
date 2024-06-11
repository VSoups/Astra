from django.contrib import admin
from .models import Package, Ticket, Review, Photo

# Register your models here.

admin.site.register(Package)
admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(Photo)
