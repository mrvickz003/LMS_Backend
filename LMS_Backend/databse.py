from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zilltech_database',
        'USER': 'Zilltech',
        'PASSWORD': '6369706554@#!',
        'HOST':'Zilltech.mysql.pythonanywhere-services.com',
        'PORT':'3306',
    }
}
