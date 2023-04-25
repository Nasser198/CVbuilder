from django.urls import path
from . import views

app_name = "coreapp"
urlpatterns = [
    path('', views.index, name="index"),
    path('email_verify/', views.email_verification, name="email_verify"),
    # path('generate_pdf/', views.generate_pdf, name="generate_pdf"),
    path('generate_word/', views.generate_word, name="generate_word"),

]