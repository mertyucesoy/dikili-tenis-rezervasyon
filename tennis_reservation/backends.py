from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        UserModel = get_user_model()
        email = username.strip()  # baş/son boşlukları temizle

        try:
            # email'i büyük/küçük harfe duyarsız ara
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(email__iexact=email).order_by('id').first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
