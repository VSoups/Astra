from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('packages/', views.packages_index, name='index'),
    path('packages/<int:pkg_id>/<str:picked_date>/', views.package_detail, name='package_detail'),
    path('tickets/<int:pkg_id>/add_ticket/', views.add_ticket, name='add_ticket'),
    path('tickets/history/', views.ticket_index, name='ticket_index'),
    path('reviews/<int:pkg_id>/create/', views.ReviewCreate.as_view(), name='reviews_create'),

    path('reviews/', views.ReviewList.as_view(), name='reviews_index'),
    # path('reviews/<pkg_id>/', views.ReviewList.as_view(), name='reviews_index'),

    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='reviews_detail'),
    path('reviews/<int:pk>/update/', views.ReviewUpdate.as_view(), name='reviews_update'),
    path('reviews/<int:pk>/delete/', views.ReviewDelete.as_view(), name='reviews_delete'),
]

