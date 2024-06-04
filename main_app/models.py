from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

# Create your models here.

VENDORS = (
    ('V', 'Virgin Galactic'),
    ('S', 'SpaceX'),
    ('B', 'Blue Origin'),
)

class Package(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=250)
    vendor = models.CharField(max_length=1, choices=VENDORS, default=[0][0])
    user = models.ManyToManyField(User)
    available_tickets = models.IntegerField(default=15)
    # images/videos from api
    # reviews model link 1:M
    

    def __str__(self):
        return f'{self.name} ({self.id})'

    # def get_absolute_url(self):
    #     return reverse('detail', kwargs={'package_id': self.id})

class Ticket(models.Model):
    price = models.FloatField(max_length=10)
    date = models.DateField('Departure')
    flight_num = models.IntegerField(default=200)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    