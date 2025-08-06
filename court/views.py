from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation, CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_backends
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from datetime import date, datetime, timedelta
from django.core import serializers
from django.utils.timezone import make_aware, is_naive




@login_required
def home(request):
    today = timezone.localdate()
    upcoming_reservations = Reservation.objects.filter(
        date__gte=today
    ).order_by('date', 'time_slot')

    return render(request, 'court/home.html', {
        'reservations': upcoming_reservations
    })


@login_required
def reserve(request):
    today = date.today()
    today_str = today.isoformat()
    selected_date_str = request.GET.get('date', today_str)
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    max_date = today + timedelta(days=2)
    if selected_date > max_date:
        messages.error(request, "En fazla 48 saat sonrasına rezervasyon yapılabilir.")
        return redirect('home')

    reserved_slots = Reservation.objects.filter(date=selected_date).values_list('time_slot', flat=True)
    user_has_reservation = Reservation.objects.filter(user=request.user, date__gte=timezone.localdate()).exists()

    all_slots = [(f"{h:02d}:00 - {((h + 1) % 24):02d}:00") for h in range(6, 24)]

    now = datetime.now()
    if selected_date == now.date():
        current_hour = now.hour
        if now.minute > 0:
            current_hour += 1
        all_slots = [slot for slot in all_slots if int(slot.split(":")[0]) >= current_hour]

    if request.method == 'POST':
        if user_has_reservation:
            messages.error(request, "Bu tarih için zaten bir rezervasyonunuz var.")
        else:
            date_input = request.POST['date']
            time_slot = request.POST['time_slot']
            Reservation.objects.create(user=request.user, date=date_input, time_slot=time_slot)
            messages.success(request, "Rezervasyon başarıyla oluşturuldu.")
            return redirect('home')

    return render(request, 'court/reserve.html', {
        'all_slots': all_slots,
        'reserved_slots': reserved_slots,
        'today': today_str,
        'selected_date': selected_date_str,
        'user_locked': user_has_reservation,
        'max_date': max_date.isoformat()
    })


def admin_view(request):
    reservations = Reservation.objects.all().order_by('date', 'time_slot')
    return render(request, 'court/admin.html', {'reservations': reservations})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.user == request.user or request.user.is_superuser:
        reservation.delete()
    return redirect('home')


# ✅ DÜZENLİ: Geçmiş rezervasyonları gösteren view
def past_24h_reservations(request):
    now = timezone.localtime()
    yesterday = now - timedelta(days=1)

    past_reservations = []

    for res in Reservation.objects.all():
        try:
            start_str, end_str = res.time_slot.split(" - ")
            end_hour, end_minute = map(int, end_str.split(":"))

            # Eğer bitiş saati gece 00:00 ise → tarihi 1 gün artır
            reservation_date = res.date
            if end_hour == 0 and end_minute == 0:
                reservation_date += timedelta(days=1)

            # Bitiş zamanını oluştur ve aware yap
            naive_end = datetime.combine(reservation_date, datetime.min.time()).replace(hour=end_hour, minute=end_minute)
            aware_end = timezone.make_aware(naive_end)

            if yesterday <= aware_end <= now:
                past_reservations.append(res)
        except Exception:
            continue

    return render(request, 'court/past_24h_reservations.html', {
        'reservations': past_reservations
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 1. Kullanıcıyı geçici olarak oluştur
            user = form.save(commit=False)

            # 2. Doğrulama ve pasiflik ayarları
            user.is_active = False
            user.is_verified = False
            user.verification_code = get_random_string(6, allowed_chars='0123456789')
            user.code_expiry = timezone.now() + timezone.timedelta(minutes=10)

            # 3. Şifreyi al (ileride session’a koyacağız)
            raw_password = form.cleaned_data.get("password1")

            # 4. Veritabanına kaydet → artık ID var
            user.save()

            # 5. Serializasyona geç → artık hata vermez
            user_json = serializers.serialize('json', [user])
            request.session['pending_user'] = user_json
            request.session['plain_password'] = raw_password

            # 6. Mail gönder
            send_mail(
                subject='Email Doğrulama Kodu',
                message=f'Doğrulama kodunuz: {user.verification_code}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return redirect('verify_email')
    else:
        form = CustomUserCreationForm()

    return render(request, 'court/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_verified or user.is_superuser:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'E-posta doğrulaması yapılmamış.')
        else:
            messages.error(request, 'Geçersiz e-posta veya şifre.')

    return render(request, 'court/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')


def verify_email(request):
    if request.method == "POST":
        code = request.POST.get("code")
        user_json = request.session.get("pending_user")
        raw_password = request.session.get("plain_password")

        if not user_json:
            messages.error(request, "Kayıt bilgisi bulunamadı. Lütfen yeniden kayıt olun.")
            return redirect("register")

        user_data = list(serializers.deserialize('json', user_json))[0]
        user = user_data.object

        if timezone.now() > user.code_expiry:
            messages.error(request, "Kodun süresi doldu. Lütfen tekrar kayıt olun.")
            request.session.flush()
            return redirect("register")

        if user.verification_code == code:
            user.set_password(raw_password)
            user.is_active = True
            user.is_verified = True
            user.save()

            backend = get_backends()[0]
            login(request, user, backend='tennis_reservation.backends.EmailBackend')

            request.session.flush()
            messages.success(request, "E-posta doğrulandı.")
            return redirect("home")
        else:
            messages.error(request, "Kod yanlış.")

    return render(request, "court/verify_email.html")
