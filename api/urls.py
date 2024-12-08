# urls.py
from django.urls import path
from api.views import custom_forms, auth, custom_datas, calender
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("getToken", auth.GetToken.as_view(), name="getToken"),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('login', auth.user_login, name='login'),
    path('register', auth.Register.as_view(), name='register'),
    path('verify_otp', auth.VerifyOtp.as_view(), name='verify_otp'),

    path('userdetails', auth.UserDetails, name='user-details'),
    
    path('forms', custom_forms.FormView.as_view(), name='form_list_create'),
    path('datas', custom_datas.submit_form_data, name='dynamic_formdata'),

    path('events', calender.get_events, name='events'),
    path('event_form', calender.event_form, name='event_form'),
    path('create_event', calender.create_event, name='create_event'),
    path('update_event', calender.update_event, name='update_event'),
    path('delete_event', calender.delete_event, name='delete_event'),
]
