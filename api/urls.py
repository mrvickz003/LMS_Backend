# urls.py
from django.urls import path
from api.views import custom_forms, auth, custom_datas, calender, common, testing
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("getToken", common.GetToken.as_view(), name="getToken"),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('login', auth.user_login, name='login'),
    path('register', auth.register, name='register'),
    path('test_register', testing.test_register, name='test_register'), 
    path('account_verify', auth.account_verify, name='account_verify'),
    path('forget_password_otp', auth.forget_password_otp, name='forget_password_otp'),
    path('forget_password_otp_verify', auth.forget_password_otp_verify, name='forget_password_otp_verify'),
    path('change_forget_password', auth.change_forget_password, name='change_forget_password'),
    path('change_password', auth.change_password, name='change_password'),
    
    path('forms', custom_forms.FormView.as_view(), name='form_list_create'),
    path('datas', custom_datas.submit_form_data, name='dynamic_formdata'),

    path('events', calender.get_events, name='events'),
    path('event_form', calender.event_form, name='event_form'),
    path('create_event', calender.create_event, name='create_event'),
    path('update_event', calender.update_event, name='update_event'),
    path('delete_event', calender.delete_event, name='delete_event'),
]
