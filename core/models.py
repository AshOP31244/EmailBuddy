from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from django.conf import settings
import base64


def get_cipher():
    """Get Fernet cipher for encryption/decryption"""
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not key:
        raise ValueError("FIELD_ENCRYPTION_KEY not set in settings")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


class UserProfile(models.Model):
    """Extended user profile with avatar and dark mode preference"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    dark_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/icons/icon-192.png'  # Default avatar


class UserEmailSettings(models.Model):
    """Per-user SMTP configuration with encrypted password"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_settings')
    
    smtp_email = models.EmailField(help_text="Your email address")
    smtp_password_encrypted = models.TextField(help_text="Encrypted app password")
    smtp_host = models.CharField(max_length=255, default='smtp.gmail.com')
    smtp_port = models.IntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)
    
    is_verified = models.BooleanField(default=False)
    last_verified = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Email Settings"
        verbose_name_plural = "User Email Settings"

    def __str__(self):
        return f"{self.user.username} - {self.smtp_email}"

    def set_password(self, raw_password):
        """Encrypt and store SMTP password"""
        cipher = get_cipher()
        encrypted = cipher.encrypt(raw_password.encode())
        self.smtp_password_encrypted = base64.b64encode(encrypted).decode()

    def get_password(self):
        """Decrypt and return SMTP password"""
        try:
            cipher = get_cipher()
            encrypted_bytes = base64.b64decode(self.smtp_password_encrypted)
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValidationError(f"Failed to decrypt password: {str(e)}")


class Template(models.Model):
    TYPE_CHOICES = [
        ('text', 'Plain Text'),
        ('html', 'HTML'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    template_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Customer(models.Model):
    STATUS_CHOICES = [
        ('Interested', 'Interested'),
        ('Not Interested', 'Not Interested'),
        ('Busy', 'Busy'),
        ('Follow-up Later', 'Follow-up Later'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Interested')
    last_contact = models.DateTimeField(null=True, blank=True)
    next_reminder = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}>"


class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)

    to_email = models.EmailField()
    cc_emails = models.CharField(max_length=500, blank=True, null=True)
    bcc_emails = models.CharField(max_length=500, blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    body_sent = models.TextField(blank=True, null=True)
    is_html = models.BooleanField(default=False)

    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Sent')

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.to_email} — {self.sent_at.strftime('%d %b %Y %H:%M')}"

