from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from court import views  # ✅ past_24h_reservations için gerekli

urlpatterns = [
    path('admin/', admin.site.urls),

    # Uygulama içi tüm view'ları `court/urls.py` üzerinden yönlendir
    path('', include('court.urls')),

    # Eğer court.urls içinde login/logout tanımlı değilse buradan tanımlanır:
    path('login/', auth_views.LoginView.as_view(template_name='court/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Son 24 saatin geçmiş rezervasyonları
    path('past-reservations/', views.past_24h_reservations, name='past_24h_reservations'),
]
