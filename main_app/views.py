from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Package, DESTINATIONS
import random

# Create your views here.


def home(request):
    experiences = Package.objects.all().values_list('experiences', flat=True)[0:5]
    return render(request, 'home.html', {'destinations': DESTINATIONS, 'experiences': experiences})

def about(request): 
    return render(request, 'about.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

def packages_index(request):
    dest_query = request.GET.get('destination')
    packages = Package.objects.filter(destination__icontains=dest_query) if dest_query else Package.objects.all()
    exp_query = request.GET.get('experience')
    packages = packages.filter(experiences__icontains=exp_query) if exp_query else packages
    # searched_packages = packages.filter(reqeust.GET())
    
    # packages = Package.objects.all()
    return render(request, 'packages/index.html', {
        'packages': packages
    })