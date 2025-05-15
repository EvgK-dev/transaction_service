from django.urls import path
from .views import user_login, register, purchases_view, user_logout

urlpatterns = [
    path('', user_login, name='login'),
    path('register/', register, name='register'),
    path('purchases/', purchases_view, name='purchases'),
    path('logout/', user_logout, name='logout'),
]