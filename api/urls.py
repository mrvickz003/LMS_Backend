# urls.py
from django.urls import path
from api.views import custom_forms

urlpatterns = [
    path('forms/', custom_forms.FormView.as_view(), name='form-list-create'),
]
