import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import EmailValidator
from django.forms import ValidationError

# MANAGER FOR USER
class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)
# CUSTOM USER MODEL
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the Habit Tracker application
    
    Attributes:
    - id: Unique identifier for the user (UUID primary key)
    - email: User's email address (used as the primary login identifier)
    - password: Hashed password
    - avatar: Profile picture URL
    - is_active: User account status
    - is_staff: Determines admin access
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    email = models.EmailField(
        unique=True, 
        validators=[EmailValidator()],
        max_length=255
    )
    
    avatar = models.URLField(
        max_length=500, 
        null=True, 
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Specify the field used for login
    USERNAME_FIELD = 'email'
    
    # Additional required fields when creating a user
    REQUIRED_FIELDS = []
    
    # Custom manager
    objects = CustomUserManager()
    
    # Add unique related_name to resolve conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )
    
    def __str__(self):
        """
        String representation of the user
        """
        return self.email
    
    class Meta:
        """
        Metadata for the CustomUser model
        """
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

class FrequencyChoices(models.TextChoices):
    DAILY = 'DAILY', 'Daily'
    WEEKLY = 'WEEKLY', 'Weekly'
    MONTHLY = 'MONTHLY', 'Monthly'

# HABIT MODEL
class Habit(models.Model):
    """
    Model representing a habit in the Habit Tracker application.
    
    Attributes:
    - id: Unique identifier for the habit (UUID primary key)
    - user: Foreign key relationship to the CustomUser model
    - name: Name of the habit
    - description: Detailed description of the habit
    - frequency: Frequency of the habit (Daily/Weekly/Monthly)
    - start_date: Date when the habit tracking begins
    - end_date: Date when the habit tracking ends
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='habits'
    )
    
    name = models.CharField(
        max_length=255, 
        null=False, 
        blank=False
    )
    
    description = models.TextField(
        null=True, 
        blank=True
    )
    
    frequency = models.CharField(
        max_length=10, 
        choices=FrequencyChoices.choices, 
        default=FrequencyChoices.DAILY
    )
    
    start_date = models.DateField()
    
    end_date = models.DateField(
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """
        Custom validation to ensure end_date is after start_date if provided
        """
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")
    
    def save(self, *args, **kwargs):
        """
        Override save method to run full clean validation
        """
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        """
        String representation of the Habit
        """
        return f"{self.name} - {self.frequency}"
    
    class Meta:
        """
        Metadata for the Habit model
        """
        ordering = ['-created_at']
        verbose_name_plural = 'Habits'
        indexes = [
            models.Index(fields=['user', 'frequency', 'start_date']),
        ]
