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

DESTINATIONS = (
    ('Mo', 'Moon'),
    ('Ma', 'Mars'),
    ('Pl', 'Pluto'),
    ('Is', 'International Space Station'),
    ('Ne', 'Neptune'),
)


class Package(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)   # volume/bulk discount here
    destination = models.CharField(
        max_length=2, choices=DESTINATIONS, default=[0][0])
    experiences = models.TextField(max_length=1000)
    # package <-> experience
    vendor = models.CharField(max_length=1, choices=VENDORS, default=[0][0])
    # not to create additional joined table (User.ticket_set_all.all())
    users = models.ManyToManyField(User, through="Ticket")  # lazy
    # do count package.ticket_set_all.count
    max_tickets = models.IntegerField(default=15)
    # images/videos from api
    # reviews model link 1:M
    # tracking ticket number for certain date, no dates on the ticket model
    # search result => all tickets available for that selected date
    # date on the ticket detail page (Jim), user enter destination in search, output package in the view (max_ticket sold out rendering after compute)
    # date (query param > route param)

    def __str__(self):
        return f'{self.name} ({self.id})'

    # def get_absolute_url(self):
    #     return reverse('detail', kwargs={'package_id': self.id})


class Ticket(models.Model):
    # individual discounted price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField('Departure Date')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    # request.user.ticket_set.all => ticket.package.<attribute>


# review - user
# package  - ticket (via user )
