from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
        path('',views.Home_view,name='home'),
        path('log/', views.login_view, name='login'),
        path('upload_excel/', views.upload_excel, name='upload_excel'),
        path('items/', views.item_list, name='item_list'),
        path('create_user/', views.create_user, name='create_user'),
        path('save_user/', views.save_finalized_quantities_user, name='save_user'),
        path('signout/', views.signout, name='signout'),
        path('assign_permissions/', views.assign_permissions, name='assign_permissions'),
        path('logout/', views.user_logout, name='logout'),
        

]