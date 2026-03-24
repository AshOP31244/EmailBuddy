from django import forms
from .models import Template, Customer ,UserProfile, UserEmailSettings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


INPUT_CLS = 'form-input'


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'template_type', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'e.g. Welcome Email',
            }),
            'template_type': forms.RadioSelect(),
            'body': forms.Textarea(attrs={
                'rows': 12,
                'class': INPUT_CLS,
                'id': 'id_body_field',
                'placeholder': 'Enter template content…',
            }),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'company', 'status', 'next_reminder', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLS, 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': '+1 234 567 890'}),
            'company': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Company name'}),
            'status': forms.Select(attrs={'class': INPUT_CLS}),
            'next_reminder': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': INPUT_CLS, 'type': 'datetime-local'},
            ),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': INPUT_CLS,
                'placeholder': 'Internal notes…',
            }),
        }


class QuickEmailSendForm(forms.Form):
    """Send email with preview before sending."""

    to_email = forms.EmailField(
        label='To *',
        widget=forms.EmailInput(attrs={'class': INPUT_CLS, 'placeholder': 'recipient@example.com'}),
    )
    cc_emails = forms.CharField(
        label='CC', required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'cc1@example.com, cc2@example.com'}),
    )
    bcc_emails = forms.CharField(
        label='BCC', required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'bcc@example.com'}),
    )

    template = forms.ModelChoiceField(
        queryset=Template.objects.none(),
        required=False,
        empty_label='— Pick a template (optional) —',
        widget=forms.Select(attrs={'class': INPUT_CLS, 'id': 'id_template_select'}),
    )
    subject = forms.CharField(
        label='Subject *',
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Email subject'}),
    )
    body = forms.CharField(
        label='Body *',
        widget=forms.Textarea(attrs={'rows': 10, 'class': INPUT_CLS, 'id': 'id_body',
                                     'placeholder': 'Your email body…'}),
    )
    is_html = forms.BooleanField(
        label='HTML Email',
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'id_is_html', 'class': 'save-toggle'}),
    )

    save_as_customer = forms.BooleanField(
        label='Save recipient as Customer',
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'id_save_as_customer', 'class': 'save-toggle'}),
    )
    recipient_name = forms.CharField(
        label='Recipient Name', required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Full name'}),
    )
    customer_status = forms.ChoiceField(
        label='Customer Status',
        choices=Customer.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': INPUT_CLS}),
    )
    next_reminder = forms.DateTimeField(
        label='Follow-up Reminder', required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'class': INPUT_CLS, 'type': 'datetime-local'},
        ),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = Template.objects.filter(user=user)

    def clean_cc_emails(self):
        raw = self.cleaned_data.get('cc_emails', '')
        return [e.strip() for e in raw.split(',') if e.strip()] if raw else []

    def clean_bcc_emails(self):
        raw = self.cleaned_data.get('bcc_emails', '')
        return [e.strip() for e in raw.split(',') if e.strip()] if raw else []
    


class SignUpForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': INPUT_CLS, 'placeholder': 'your@email.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Last name'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLS, 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLS, 'placeholder': 'Confirm password'})


class ProfileForm(forms.ModelForm):
    """User profile editing form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT_CLS}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLS}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLS}))
    
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': INPUT_CLS, 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.save()
        if commit:
            profile.save()
        return profile


class EmailSettingsForm(forms.ModelForm):
    """SMTP settings form with password field"""
    smtp_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLS, 'placeholder': 'App Password'}),
        help_text='Your Gmail App Password (16 characters)',
        label='SMTP Password'
    )
    
    class Meta:
        model = UserEmailSettings
        fields = ['smtp_email', 'smtp_host', 'smtp_port', 'smtp_use_tls']
        widgets = {
            'smtp_email': forms.EmailInput(attrs={'class': INPUT_CLS, 'placeholder': 'your-email@gmail.com'}),
            'smtp_host': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'smtp.gmail.com'}),
            'smtp_port': forms.NumberInput(attrs={'class': INPUT_CLS, 'placeholder': '587'}),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'save-toggle'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't require password if editing existing settings
        if self.instance and self.instance.pk:
            self.fields['smtp_password'].required = False
            self.fields['smtp_password'].help_text = 'Leave blank to keep current password'