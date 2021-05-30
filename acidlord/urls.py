from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('store', views.store, name='store'),
    path('card', views.card, name='card'),
    path('orders', views.orders, name='orders'),
    path('agro', views.agro, name='agro'),
    path('vac', views.vac, name='vac'),
    path('harvest', views.harvest, name='harvest'),
    path('queries_agro', views.queries_agro, name='queries_agro'),
    path('prob', views.prob, name='prob')
]