from django.urls import path

from mailing import views


urlpatterns = [
    path("client/create", views.ClientCreateView.as_view()),
    path("client/<pk>", views.ClientView.as_view()),
    path("create", views.MailingCreateView.as_view()),
    path("stat", views.MailingListView.as_view()),
    path("stat/<pk>", views.MailingDetailView.as_view(),)

]
