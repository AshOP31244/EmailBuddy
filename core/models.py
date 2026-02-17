from django.contrib.auth.models import User
from django.db import models


class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
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

    # Direct send fields (for quick-send without saved customer)
    to_email = models.EmailField()
    cc_emails = models.CharField(max_length=500, blank=True, null=True,
                                 help_text="Comma-separated CC emails")
    bcc_emails = models.CharField(max_length=500, blank=True, null=True,
                                  help_text="Comma-separated BCC emails")
    subject = models.CharField(max_length=300, blank=True, null=True)
    body_sent = models.TextField(blank=True, null=True, help_text="Actual body that was sent")

    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Sent')

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.to_email} — {self.sent_at.strftime('%d %b %Y %H:%M')}"