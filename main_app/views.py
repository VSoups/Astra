from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Package, DESTINATIONS, Ticket
from django.views.generic.edit import CreateView
from .forms import TicketForm
import random, functools

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

def package_detail(request, pkg_id):
    package = Package.objects.get(id=pkg_id)
    date = request.GET.get('date')
    ticket_list = package.ticket_set.all()
    def purchased_tickets():
      total_ticket_qty = 0
      for ticket in ticket_list:
        total_ticket_qty += ticket.qty
      return total_ticket_qty
    # print(f"Ticket total: {purchased_tickets()}")
    if date:
       num_avail_tickets = package.max_tickets - purchased_tickets()
      #  package.max_tickets = num_avail_tickets
    else:
       num_avail_tickets = 0
    qty_range = range(1, num_avail_tickets + 1)

    return render(request, 'packages/detail.html', {
       'package': package,
       'date': date,
       'num_avail_tickets': num_avail_tickets,
       'qty_range': qty_range,
    })

def add_ticket(request, pkg_id):
  # amt tickets purchased - from max tickets avail from pkg association.
  form = TicketForm(request.POST)
  print("Hello 1")
  print(form)
  if form.is_valid():
    new_ticket = form.save(commit=False)
    new_ticket.qty = request.POST.get('qty')
    new_ticket.package_id = pkg_id
    new_ticket.user_id = request.User
    print("Hello 2")
    print(f"New Ticket Object: {new_ticket}")
    new_ticket.save() 
  return redirect('home')