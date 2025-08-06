from django.urls import path
from court import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 🏠 Ana sayfa ve temel işlemler
    path('', views.home, name='home'),
    path('reserve/', views.reserve, name='reserve'),
    path('admin-view/', views.admin_view, name='admin_view'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),

    # 👤 Kullanıcı işlemleri
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_email, name='verify_email'),

    # ⏳ Geçmiş rezervasyonlar
    path('past-reservations/', views.past_24h_reservations, name='past_24h_reservations'),

    # 🔐 Şifre sıfırlama adımları (Django built-in)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='court/password_reset.html'),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='court/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='court/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='court/password_reset_complete.html'),
         name='password_reset_complete'),
]
