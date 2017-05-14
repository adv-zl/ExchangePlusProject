"""ExchangePlusProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^home/', views.home, name = 'home'),
    url(r'^index/', views.index, name = 'index'),
    url(r'^wiki/', views.wiki, name = 'wiki'),
    url(r'^login/', views.login, name = 'login'),
    url(r'^logout/', views.logout, name = 'logout'),
    url(r'^view-cashbox/(?P<id>[0-9]+)/$', views.view_cashbox, name = 'view'),
    url(r'^edit-cashbox/(?P<id>[0-9]+)/$', views.edit_cashbox, name = 'edit'),
    url(r'^create-cashbox/', views.create, name = 'create'),
    url(r'^private/', views.private, name = 'private'),
    url(r'financial-statement/', views.cashbox_info_by_date, name = 'statement'),
]
