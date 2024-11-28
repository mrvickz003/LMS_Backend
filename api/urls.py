# urls.py
from django.urls import path
from api.views import custom_forms, auth
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('login/', auth.Login.as_view(), name='token_obtain_pair'),
    path('register/', auth.Register.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forms/', custom_forms.FormView.as_view(), name='form-list-create'),
]
