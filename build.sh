#!/usr/bin/env bash

# Gerekli Python paketlerini yükle
pip install -r requirements.txt

# Veritabanı tablolarını oluştur/güncelle
python manage.py migrate

# Statik dosyaları topla
python manage.py collectstatic --noinput
