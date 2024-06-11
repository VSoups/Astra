from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Package, DESTINATIONS, Review
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TicketForm
from django.utils import timezone

# Create your views here.


def home(request):
    experiences = Package.objects.all().values_list(
        'experiences', flat=True)[0:5]
    print(request.user)
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
    date = request.GET.get('date')
    dest_query = request.GET.get('destination')
    packages = Package.objects.filter(
        destination__icontains=dest_query) if dest_query else Package.objects.all()
    exp_query = request.GET.get('experience')
    packages = packages.filter(
        experiences__icontains=exp_query) if exp_query else packages
    # searched_packages = packages.filter(reqeust.GET())

    # add num_tickets_avail_for_date attribute to each package
    for p in packages:

        p.num_tickets_avail_for_date = p.get_num_tickets_avail_for_date(date)
        print(f'{p.name}: {p.num_tickets_avail_for_date}')

    '''
        tickets_for_date = [package.ticket_set.filter(
            date=date, package=package) for package in packages]
        print(f'ticket amount: {tickets_for_date[1]}')

        def purchased_qty():
            # total_ticket = 0
            for ticket in tickets_for_date:
                for tk in ticket:
                    # print(t)
                    print(f'what ticket looks like: {tk}')
                # total_ticket += ticket.qty
            return

        # purchased_qty = functools.reduce(lambda total, ticket: total + ticket.qty, ticket_amount)
        # print(f'total tickets added: : {purchased_qty}')
        print(f'total tickets added: : {purchased_qty()}')
    '''

    # packages = Package.objects.all()
    return render(request, 'packages/index.html', {
        'packages': packages,
        'date': date
    })


def package_detail(request, pkg_id, picked_date):
    package = Package.objects.get(id=pkg_id)
    # date = request.GET.get('date')
    date = picked_date
    # print(f'pakage detail date: {date}')
    # ticket_list = package.ticket_set.all()

    '''
        def purchased_tickets():
            total_ticket_qty = 0
            for ticket in ticket_list:
                total_ticket_qty += ticket.qty
            return total_ticket_qty
        # print(f"Ticket total: {purchased_tickets()}")
    '''

    package.num_tickets_avail_for_date = package.get_num_tickets_avail_for_date(
        date)

    # num_avail_tickets = package.max_tickets - purchased_tickets()
    # package.max_tickets = num_avail_tickets

    qty_range = range(1, package.num_tickets_avail_for_date + 1)
    # print(f'selection option number range: {list(qty_range)}')

    return render(request, 'packages/detail.html', {
        'package': package,
        'date': date,
        'num_avail_tickets': package.num_tickets_avail_for_date,
        'qty_range': qty_range,
    })


def add_ticket(request, pkg_id):
    form = TicketForm(request.POST)
    # date = request.GET.get('date')
    # print(f'form before if: {form}')
    # print(f'form date before if: {date}')
    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.qty = request.POST.get('qty')
        new_ticket.package = Package.objects.get(id=pkg_id)
        new_ticket.passenger = request.user
        new_ticket.date = request.POST.get('date')
        new_ticket.save()
    return redirect('home')


def ticket_index(request):
    # today = date.today()
    today = timezone.now().date()
    print(today)
    user_tickets = request.user.ticket_set.all()
    past_tickets = user_tickets.filter(date__lt=today)
    print(past_tickets)
    upcoming_tickets = user_tickets.filter(date__gte=today)
    print(upcoming_tickets)
    return render(request, 'packages/ticket_index.html', {
        'past_tickets': past_tickets,
        'upcoming_tickets': upcoming_tickets,
    })


class ReviewList(LoginRequiredMixin, ListView):
    model = Review
    # template_name = "main_app/review_list.html"

    # def get_queryset(self):
    #     self.package = get_object_or_404(Package, name=self.kwargs["pkg_id"])
    #     return Review.objects.filter(package=self.package)


class ReviewDetail(LoginRequiredMixin, DetailView):
    model = Review


class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['content', 'rating']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.package_id = self.kwargs['pkg_id']
        # form.instance.package_id = self.request.package
        return super().form_valid(form)


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['content', 'rating']


class ReviewDelete(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = '/reviews/'


def like_review(request, review_id):
    request.user.liked_reviews.add(review_id)
    return redirect('detail', review_id=review_id)
