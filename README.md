# Dikili Tenis Rezervasyon

Dikili'deki tenis kortu için geliştirilmiş, gerçek kullanıcılara hizmet veren online rezervasyon sistemi.

**Canlı:** https://dikili-tenis-rezervasyon.onrender.com

## Özellikler

- E-posta ile kayıt ve 6 haneli doğrulama kodu
- Saat dilimi bazlı kort rezervasyonu ve iptal
- Şifre sıfırlama akışı
- Son 24 saatin rezervasyonlarını gösteren sayfa
- Rezervasyonları yönetmek için admin paneli

## Teknolojiler

- Python, Django 5.2
- Özel kullanıcı modeli (e-posta ile giriş)
- Gunicorn ve WhiteNoise
- Render üzerinde deploy

## Yerelde çalıştırma

```bash
git clone https://github.com/mertyucesoy/dikili-tenis-rezervasyon.git
cd dikili-tenis-rezervasyon
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export DEBUG=True
python manage.py migrate
python manage.py runserver
```

## Ortam değişkenleri

| Değişken | Açıklama |
|---|---|
| `SECRET_KEY` | Django gizli anahtarı (production'da zorunlu) |
| `DEBUG` | Geliştirme için `True` |
| `EMAIL_HOST_PASSWORD` | Doğrulama e-postaları için SMTP şifresi |
