from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Reservation
from django.db.models import Count
from datetime import datetime


# 👤 Özel kullanıcı yönetimi
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'full_name', 'age', 'phone', 'is_staff']
    ordering = ['email']
    search_fields = ['email', 'full_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('full_name', 'age', 'phone')}),
        ('Yetkiler', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'age', 'phone', 'password1', 'password2',
                       'is_staff', 'is_superuser', 'groups', 'user_permissions')}
         ),
    )


# 📅 Rezervasyon yönetimi ve istatistik görünümü
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time_slot')
    list_filter = ('date', 'time_slot')
    search_fields = ('user__email', 'date', 'time_slot')
    change_list_template = "admin/reservation_changelist.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Toplam rezervasyon sayısı
        total_reservations = Reservation.objects.count()

        # En çok rezervasyon yapan ilk 5 kullanıcı
        top_users = (
            Reservation.objects.values('user__full_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # En yoğun saat aralıkları
        popular_slots = (
            Reservation.objects.values('time_slot')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        extra_context.update({
            'total_reservations': total_reservations,
            'top_users': top_users,
            'popular_slots': popular_slots,
        })

        return super().changelist_view(request, extra_context=extra_context)


# Kayıtlar
admin.site.register(CustomUser, CustomUserAdmin)
