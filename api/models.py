from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as GL
from django.utils.timezone import now
from datetime import timedelta

def default_expiry():
    return now() + timedelta(minutes=5)

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mobile_number} - {self.otp}"
    
class Company(models.Model):
    company_name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    owner = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="ownerOfCompany")
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_company")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_company")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.company_name

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
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(height_field=None, width_field=None, max_length=None, blank=True, null=False)
    email = models.EmailField(unique=True,blank=False, null=False)
    mobile_number = models.IntegerField(blank=False, null=False,unique=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name="custom_user", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

class Form(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="forms", null=True, blank=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    layout = models.JSONField(blank=False, null=False)
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_forms")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_forms")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.name

class FormFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="form_files", null=True, blank=True)
    file = models.FileField()
    file_type = models.CharField(max_length=20)  # Store file type (image, audio, video)
    form_submission = models.ForeignKey("FormData", on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return f"{self.file_type} file for {self.form_submission.form.name}"

class FormData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="form_data", null=True, blank=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    submitted_data = models.JSONField()  # Store as a JSON field
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_data")
    create_date = models.DateTimeField()
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_data")
    update_date = models.DateTimeField()

    def __str__(self):
        return f"Submission for {self.form.name}"
    
class Calendar(models.Model):
    RECURRING_CHOICES = [
        ('NONE', 'None'),
        ('DALY', 'Daily'),
        ('WEEK', 'Weekly'),
        ('MONT', 'Monthly'),
        ('YEAR', 'Yearly'),
    ] 

    EVENT_TYPE = [
        ('NONE', 'None'),
        ('CUSM', 'Customer Meeting'),
        ('SCAL', 'Sales Call'),
        ('FLUP', 'Follow-Up'),
        ('PDEM', 'Product Demo'),
        ('PDIS', 'Proposal Discussion'),
        ('CSNG', 'Contract Signing'),
        ('FSES', 'Feedback Session'),
        ('TSES', 'Training Session'),
        ('NEVT', 'Networking Event'),
        ('LQCL', 'Lead Qualification Call'),
        ('OSES', 'Onboarding Session'),
        ('CLCH', 'Campaign Launch'),
        ('SUCL', 'Support Call'),
        ('CARY', 'Customer Anniversary'),
        ('RREM', 'Renewal Reminder'),
        ('CSSY', 'Customer Satisfaction Survey'),
        ('TMTG', 'Team Meeting'),
        ('GLRW', 'Goal Review'),
        ('PERW', 'Performance Review'),
        ('PPDN', 'Partnership Discussion'),
        ('BDAY', 'Birthday'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="event", null=True, blank=True)
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=28, choices=EVENT_TYPE, default='none')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    location = models.URLField(blank=True, null=True)
    meeting_url =  models.URLField(blank=True, null=True)
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')
    users = models.ManyToManyField('CustomUser', related_name='attending_events')
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_event")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_event")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.name

