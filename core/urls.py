from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # API (used by JS on email_send page)
    path('api/templates/', views.api_templates, name='api_templates'),

    # Templates
    path('templates/',                    views.template_list,   name='template_list'),
    path('templates/create/',             views.template_create, name='template_create'),
    path('templates/edit/<int:pk>/',      views.template_edit,   name='template_edit'),
    path('templates/delete/<int:pk>/',    views.template_delete, name='template_delete'),

    # Customers
    path('customers/',                    views.customer_list,   name='customer_list'),
    path('customers/create/',             views.customer_create, name='customer_create'),
    path('customers/edit/<int:pk>/',      views.customer_edit,   name='customer_edit'),
    path('customers/delete/<int:pk>/',    views.customer_delete, name='customer_delete'),
    path('customers/detail/<int:pk>/',    views.customer_detail, name='customer_detail'),

    # Email
    path('email/send/',  views.email_send,      name='email_send'),
    path('email/logs/',  views.email_log_list,   name='email_log_list'),

    # Reminders
    path('reminders/',   views.reminders_view,   name='reminders'),
    
    # ========== ADD THESE NEW URLS (MISSING!) ==========
    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Email Settings
    path('email-settings/', views.email_settings_view, name='email_settings'),
    path('email-settings/test/', views.test_smtp_view, name='test_smtp'),
    
    # PWA
    path('install/', views.install_pwa_view, name='install_pwa'),
    
    # Theme toggle
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
]