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
