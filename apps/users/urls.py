from django.conf.urls import url

from apps.users import views

urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(), name='register'), #  注册类视图
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='active'), #  激活类视图
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^orders$', views.UserOrderView.as_view(), name='orders'),
    url(r'^address$', views.UserAddressView.as_view(), name='address'),
    url(r'^$', views.UserInfoView.as_view(), name='info'),
]