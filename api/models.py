from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as GL

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(GL('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(GL('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(GL('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    def createFolder(self, filename):
        return f"{self.email}/profile/{filename}"

    photo = models.ImageField(upload_to=createFolder, height_field=None, width_field=None, max_length=None, blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile_number = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} to {self.last_login}"

class Form(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    layout = models.JSONField(blank=False, null=False)  # JSON layout for form fields
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_forms")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_forms")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.name

class FormFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=20)  # Store file type (image, audio, video)
    form_submission = models.ForeignKey("FormData", on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return f"{self.file_type} file for {self.form_submission.form.name}"

class FormData(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    submitted_data = models.JSONField()  # Store as a JSON field
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_data")
    create_date = models.DateTimeField()
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_data")
    update_date = models.DateTimeField()

    def __str__(self):
        return f"Submission for {self.form.name}"
    
class Calendar(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    RECURRING_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"

class Attendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name