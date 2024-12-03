# urls.py
from django.urls import path
from api.views import custom_forms, auth, custom_datas, calender
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("getToken", auth.GetToken.as_view(), name="getToken"),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    # path('login/', auth.Login.as_view(), name='login'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('register', auth.Register.as_view(), name='register'),

    path('userdetails', auth.UserDetails, name='user-details'),
    
    path('forms', custom_forms.FormView.as_view(), name='form_list_create'),
    path('datas', custom_datas.submit_form_data, name='dynamic_formdata'),
    path('datas/<int:form_data_id>', custom_datas.get_form_data, name='get_form_data'),

    path('events', calender.get_events, name='events'),

]
