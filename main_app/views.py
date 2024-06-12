from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Package, DESTINATIONS, Review, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TicketForm
from django.utils import timezone
import boto3, os, uuid

# Create your views here.


def home(request):
    experiences = Package.objects.all().values_list(
        'experiences', flat=True)[0:5]
    print(request.user)
    return render(request, 'home.html', {
        'destinations': DESTINATIONS,
        'experiences': experiences,
        })


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
    search_query = request.GET.get('search_query')
    if search_query:
        for choice in DESTINATIONS:
            if search_query.lower() in choice[1].lower():
                dest = choice[0]
                break
        if not 'dest' in locals():
            dest = None
        packages = Package.objects.filter(Q(destination=dest) | Q(experiences__icontains=search_query))
        dest_query = None
        exp_query = None
    else:
        dest_query = request.GET.get('destination')
        packages = Package.objects.filter(
            destination__icontains=dest_query) if dest_query else Package.objects.all()
        exp_query = request.GET.get('experience')
        packages = packages.filter(
            experiences__icontains=exp_query) if exp_query else packages
    
    for p in packages:
        p.num_tickets_avail_for_date = p.get_num_tickets_avail_for_date(date)

    return render(request, 'packages/index.html', {
        'packages': packages,
        'date': date,
        'destination': dest_query,
        'experience': exp_query,
        'search_query':search_query,
    })

@login_required
def package_detail(request, pkg_id, picked_date):
    package = Package.objects.get(id=pkg_id)
    date = picked_date
    package.num_tickets_avail_for_date = package.get_num_tickets_avail_for_date(
        date)

    qty_range = range(1, package.num_tickets_avail_for_date + 1)

    return render(request, 'packages/detail.html', {
        'package': package,
        'date': date,
        'num_avail_tickets': package.num_tickets_avail_for_date,
        'qty_range': qty_range,
    })

@login_required
def add_ticket(request, pkg_id):
    form = TicketForm(request.POST)
    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.qty = request.POST.get('qty')
        new_ticket.package = Package.objects.get(id=pkg_id)
        new_ticket.passenger = request.user
        new_ticket.date = request.POST.get('date')
        new_ticket.save()
    return redirect('home')

@login_required
def ticket_index(request):
    today = timezone.now().date()
    user_tickets = request.user.ticket_set.all()
    past_tickets = user_tickets.filter(date__lt=today)
    upcoming_tickets = user_tickets.filter(date__gte=today)
    return render(request, 'packages/ticket_index.html', {
        'past_tickets': past_tickets,
        'upcoming_tickets': upcoming_tickets,
    })


class ReviewsForPackage(LoginRequiredMixin, DetailView):
    model = Package
    template_name = "main_app/review_list.html"


class ReviewDetail(LoginRequiredMixin, DetailView):
    model = Review


class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['content', 'rating']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.package_id = self.kwargs['pkg_id']
        return super().form_valid(form)


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['content', 'rating']


class ReviewDelete(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = '/reviews/'

@login_required
def like_review(request, pkg_id, review_id):
    request.user.liked_reviews.add(review_id)
    return redirect('reviews_index', pk=pkg_id)

@login_required
def unlike_review(request, pkg_id, review_id):
    request.user.liked_reviews.remove(review_id)
    return redirect('reviews_index', pk=pkg_id)

@login_required
def add_photo(request, review_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        # replacing photo name with unique id
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # build the full url string
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            Photo.objects.create(url=url, review_id=review_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('reviews_detail', pk=review_id)