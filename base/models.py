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

class HabitCompletion(models.Model):
    """
    Model representing a habit completion entry
    
    Attributes:
    - id: Unique identifier for the habit completion (UUID primary key)
    - habit: Foreign key relationship to the Habit model
    - date: Date of habit completion
    - status: Boolean indicating whether the habit was completed
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    habit = models.ForeignKey(
        Habit, 
        on_delete=models.CASCADE, 
        related_name='completions'
    )
    
    date = models.DateField()
    
    status = models.BooleanField(
        default=False, 
        help_text="Indicates whether the habit was completed on this date"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """
        Custom validation to ensure:
        1. Date is within habit's start and end dates
        2. No duplicate entries for the same habit and date
        """
        # Check if date is within habit's tracking period
        if self.habit.start_date and self.date < self.habit.start_date:
            raise ValidationError("Completion date cannot be before habit start date")
        
        if self.habit.end_date and self.date > self.habit.end_date:
            raise ValidationError("Completion date cannot be after habit end date")
        
        # Check for duplicate entries
        existing_completion = HabitCompletion.objects.filter(
            habit=self.habit, 
            date=self.date
        ).exclude(pk=self.pk).exists()
        
        if existing_completion:
            raise ValidationError("A completion entry for this habit on this date already exists")
    
    def save(self, *args, **kwargs):
        """
        Override save method to run full clean validation
        """
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        """
        String representation of the HabitCompletion
        """
        return f"{self.habit.name} - {self.date} ({'Completed' if self.status else 'Not Completed'})"
    
    class Meta:
        """
        Metadata for the HabitCompletion model
        """
        unique_together = [['habit', 'date']]  # Ensure unique habit-date combination
        ordering = ['-date']
        verbose_name_plural = 'Habit Completions'
        indexes = [
            models.Index(fields=['habit', 'date', 'status']),
        ]

