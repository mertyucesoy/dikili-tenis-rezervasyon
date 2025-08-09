from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core import serializers
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

from .models import Reservation, CustomUser
from .forms import CustomUserCreationForm

from datetime import datetime, timedelta, date
from django.contrib.admin.views.decorators import staff_member_required


from django.http import HttpResponse
from django.contrib.auth import get_user_model


@login_required
def home(request):
    today = timezone.localdate()
    reservations = Reservation.objects.filter(date__gte=today).order_by('date', 'time_slot')
    return render(request, 'court/home.html', {'reservations': reservations})


@login_required
def reserve(request):
    today = timezone.localdate()
    selected_date_str = request.GET.get('date', today.isoformat())

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Geçersiz tarih formatı.")
        return redirect('reserve')

    if selected_date < today:
        messages.error(request, "Geçmiş bir tarih için rezervasyon yapılamaz.")
        return redirect('reserve')

    if selected_date > today + timedelta(days=2):
        messages.error(request, "En fazla 48 saat sonrasına rezervasyon yapılabilir.")
        return redirect('home')

    # 06:00-24:00 arası saat dilimleri
    all_slots = [f"{h:02d}:00 - {((h + 1) % 24):02d}:00" for h in range(6, 24)]

    now_local = timezone.localtime()
    if selected_date == now_local.date():
        # sadece ilerideki saatleri göster
        all_slots = [slot for slot in all_slots if int(slot[:2]) > now_local.hour]

    reserved_slots = set(
        Reservation.objects.filter(date=selected_date).values_list('time_slot', flat=True)
    )
    user_has_reservation = Reservation.objects.filter(
        user=request.user, date__gte=today
    ).exists()

    if request.method == 'POST':
        if user_has_reservation:
            messages.error(request, "Zaten bir rezervasyonunuz var.")
        else:
            time_slot = request.POST.get('time_slot')
            if not time_slot:
                messages.error(request, "Saat aralığı seçin.")
            elif time_slot in reserved_slots:
                messages.error(request, "Seçtiğiniz saat dolu.")
            else:
                Reservation.objects.create(
                    user=request.user, date=selected_date, time_slot=time_slot
                )
                messages.success(request, "Rezervasyon oluşturuldu.")
                return redirect('home')

    return render(request, 'court/reserve.html', {
        'all_slots': all_slots,
        'reserved_slots': reserved_slots,
        'selected_date': selected_date_str,
        'today': today.isoformat(),
        'max_date': (today + timedelta(days=2)).isoformat(),
        'user_locked': user_has_reservation,
    })


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if reservation.user == request.user or request.user.is_superuser:
        reservation.delete()
        messages.success(request, "Rezervasyon iptal edildi.")
    else:
        messages.error(request, "Bu rezervasyonu iptal etme yetkiniz yok.")
    return redirect('home')


def past_24h_reservations(request):
    now = timezone.localtime()
    yesterday = now - timedelta(days=1)
    results = []

    for res in Reservation.objects.all():
        try:
            _, end_str = res.time_slot.split(" - ")
            end_hour, end_minute = map(int, end_str.split(":"))
            end_time = datetime.combine(res.date, datetime.min.time()).replace(
                hour=end_hour, minute=end_minute
            )
            if end_hour == 0 and end_minute == 0:
                end_time += timedelta(days=1)
            aware_end = timezone.make_aware(end_time)
            if yesterday <= aware_end <= now:
                results.append(res)
        except Exception:
            continue

    return render(request, 'court/past_24h_reservations.html', {'reservations': results})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'Bu e-posta adresi zaten kullanılıyor.')
                return render(request, 'court/register.html', {'form': form})

            user = form.save(commit=False)
            user.is_active = False
            user.is_verified = False
            user.verification_code = get_random_string(6, allowed_chars='0123456789')
            user.code_expiry = timezone.now() + timedelta(minutes=10)
            raw_password = form.cleaned_data.get("password1")

            user.save()

            # Session'a şifre ve kullanıcıyı koy
            request.session['pending_user'] = serializers.serialize('json', [user])
            request.session['plain_password'] = raw_password

            # Mail gönderimini güvene al
            try:
                send_mail(
                    subject='Email Doğrulama Kodu',
                    message=f'Doğrulama kodunuz: {user.verification_code}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f"E-posta gönderilemedi: {e}")
                return render(request, 'court/register.html', {'form': form})

            return redirect('verify_email')
    else:
        form = CustomUserCreationForm()

    return render(request, 'court/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # email bekleniyor
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

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
            messages.error(request, "Kayıt bilgisi bulunamadı.")
            return redirect("register")

        user_data = list(serializers.deserialize('json', user_json))[0]
        user = user_data.object

        if timezone.now() > user.code_expiry:
            messages.error(request, "Kodun süresi doldu.")
            request.session.flush()
            return redirect("register")

        if user.verification_code == code:
            user.set_password(raw_password)
            user.is_active = True
            user.is_verified = True
            user.save()

            login(request, user, backend='tennis_reservation.backends.EmailBackend')

            # ❌ request.session.flush() kullanma
            # ✅ Sadece bu iki anahtarı temizle
            for k in ('pending_user', 'plain_password'):
                request.session.pop(k, None)

            return redirect("home")
        else:
            messages.error(request, "Kod yanlış.")

    return render(request, "court/verify_email.html")


@staff_member_required
def admin_view(request):
    reservations = Reservation.objects.all().order_by('-date', 'time_slot')
    return render(request, "court/admin.html", {"reservations": reservations})