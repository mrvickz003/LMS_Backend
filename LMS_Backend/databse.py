from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zilltech_database',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST':'localhost',
        'PORT':'3306',
    }
}
