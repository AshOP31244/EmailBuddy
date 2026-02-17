from django import forms
from .models import Template, Customer


INPUT_CLS = 'form-input'


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'e.g. Welcome Email',
            }),
            'body': forms.Textarea(attrs={
                'rows': 9,
                'class': INPUT_CLS,
                'placeholder': 'Use {{name}}, {{email}} as placeholders…',
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
    """Send email to any address; optionally save recipient as Customer."""

    # Recipient
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

    # Content
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
        widget=forms.Textarea(attrs={'rows': 9, 'class': INPUT_CLS, 'id': 'id_body',
                                     'placeholder': 'Your email body…'}),
    )

    # Save-as-customer section
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