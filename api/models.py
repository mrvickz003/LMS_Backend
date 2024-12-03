from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as GL

class Company(models.Model):
    company_name = models.CharField(max_length=30, blank=False, null=False)
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
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(height_field=None, width_field=None, max_length=None, blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile_number = models.IntegerField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="custom_user", null=True, blank=True)
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
    file = models.FileField(upload_to='uploads/')
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
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ] 

    EVENT_TYPE = [
        ('none', 'None'),
        ('customer_meeting', 'Customer Meeting'),
        ('sales_call', 'Sales Call'),
        ('follow_up', 'Follow-Up'),
        ('product_demo', 'Product Demo'),
        ('proposal_discussion', 'Proposal Discussion'),
        ('contract_signing', 'Contract Signing'),
        ('feedback_session', 'Feedback Session'),
        ('training_session', 'Training Session'),
        ('networking_event', 'Networking Event'),
        ('lead_qualification_call', 'Lead Qualification Call'),
        ('onboarding_session', 'Onboarding Session'),
        ('campaign_launch', 'Campaign Launch'),
        ('support_call', 'Support Call'),
        ('customer_anniversary', 'Customer Anniversary'),
        ('renewal_reminder', 'Renewal Reminder'),
        ('customer_satisfaction_survey', 'Customer Satisfaction Survey'),
        ('team_meeting', 'Team Meeting'),
        ('goal_review', 'Goal Review'),
        ('performance_review', 'Performance Review'),
        ('partnership_discussion', 'Partnership Discussion'),
        ('birthday', 'Birthday'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="event", null=True, blank=True)
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=28, choices=EVENT_TYPE, default='none')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')
    users = models.ManyToManyField('CustomUser', related_name='attending_events')
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_event")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_event")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.name

