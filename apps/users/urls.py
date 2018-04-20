from django.conf.urls import url

from apps.users import views

urlpatterns = [
    url(r'^index$', views.index, name='index'),
]