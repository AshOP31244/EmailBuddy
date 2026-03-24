from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone 
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import Template, Customer, EmailLog, UserProfile, UserEmailSettings
from .forms import TemplateForm, CustomerForm, QuickEmailSendForm, SignUpForm, ProfileForm, EmailSettingsForm
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .utils import send_email_with_user_smtp, test_smtp_connection


@login_required
def dashboard(request):
    templates  = Template.objects.filter(user=request.user)
    customers  = Customer.objects.filter(user=request.user)
    email_logs = EmailLog.objects.filter(user=request.user)
    now        = timezone.now()
    context = {
        'template_count':   templates.count(),
        'customer_count':   customers.count(),
        'upcoming_count':   customers.filter(next_reminder__gt=now).count(),
        'overdue_count':    customers.filter(next_reminder__lt=now,
                                             next_reminder__isnull=False).count(),
        'recent_emails':    email_logs.order_by('-sent_at')[:5],
        'email_sent_count': email_logs.count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def api_templates(request):
    data = list(Template.objects.filter(user=request.user).values('id', 'title', 'body', 'template_type'))
    return JsonResponse({'templates': data})


# ── Templates ─────────────────────────────────────────────────

@login_required
def template_list(request):
    templates = Template.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'template_list.html', {'templates': templates})


@login_required
def template_create(request):
    form = TemplateForm(request.POST or None)
    if form.is_valid():
        t = form.save(commit=False)
        t.user = request.user
        t.save()
        messages.success(request, 'Template created successfully!')
        return redirect('template_list')
    return render(request, 'template_form.html', {'form': form, 'action': 'Create'})


@login_required
def template_edit(request, pk):
    template = get_object_or_404(Template, pk=pk, user=request.user)
    form = TemplateForm(request.POST or None, instance=template)
    if form.is_valid():
        form.save()
        messages.success(request, 'Template updated!')
        return redirect('template_list')
    return render(request, 'template_form.html', {'form': form, 'action': 'Edit'})


@login_required
def template_delete(request, pk):
    template = get_object_or_404(Template, pk=pk, user=request.user)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Template deleted.')
        return redirect('template_list')
    return render(request, 'template_confirm_delete.html', {'template': template})


# ── Customers ─────────────────────────────────────────────────

@login_required
def customer_list(request):
    qs = Customer.objects.filter(user=request.user)
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'customer_list.html', {
        'customers':      qs,
        'status_filter':  status_filter,
        'status_choices': Customer.STATUS_CHOICES,
    })


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        c = form.save(commit=False)
        c.user = request.user
        c.save()
        messages.success(request, 'Customer added!')
        return redirect('customer_list')
    return render(request, 'customer_form.html', {'form': form, 'action': 'Add'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, 'Customer updated!')
        return redirect('customer_list')
    return render(request, 'customer_form.html', {'form': form, 'action': 'Edit'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted.')
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': customer})


@login_required
def customer_detail(request, pk):
    customer   = get_object_or_404(Customer, pk=pk, user=request.user)
    email_logs = EmailLog.objects.filter(customer=customer).order_by('-sent_at')
    return render(request, 'customer_detail.html', {'customer': customer, 'email_logs': email_logs})


# ── Email Send with ACTUAL EMAIL SENDING ──────────────────────

@login_required
def email_send(request):
    form = QuickEmailSendForm(request.user, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data

        # Check if user has email settings
        if not hasattr(request.user, 'email_settings'):
            messages.error(request, 'Please configure your email settings first!')
            return redirect('email_settings')

        customer = None
        existing = Customer.objects.filter(user=request.user, email=cd['to_email']).first()

        if cd['save_as_customer']:
            if existing:
                customer = existing
                if cd['recipient_name']:
                    customer.name = cd['recipient_name']
                customer.status        = cd.get('customer_status') or customer.status
                customer.next_reminder = cd.get('next_reminder')
                customer.last_contact  = timezone.now()
                customer.save()
            else:
                customer = Customer.objects.create(
                    user          = request.user,
                    name          = cd.get('recipient_name') or cd['to_email'],
                    email         = cd['to_email'],
                    status        = cd.get('customer_status') or 'Interested',
                    next_reminder = cd.get('next_reminder'),
                    last_contact  = timezone.now(),
                )
        elif existing:
            existing.last_contact = timezone.now()
            existing.save()
            customer = existing

        body = cd['body']
        if customer:
            body = body.replace('{{name}}', customer.name).replace('{{email}}', customer.email)

        # ══════════════════════════════════════════════════════
        # SEND EMAIL USING USER'S SMTP
        # ══════════════════════════════════════════════════════
        email_status = 'Sent'
        
        success, error = send_email_with_user_smtp(
            user=request.user,
            subject=cd['subject'],
            body=body,
            to_emails=[cd['to_email']],
            cc_list=cd.get('cc_emails', []),
            bcc_list=cd.get('bcc_emails', []),
            is_html=cd.get('is_html', False)
        )
        
        if not success:
            email_status = 'Failed'
            messages.error(request, f'Email failed to send: {error}')

        # Log the email
        EmailLog.objects.create(
            user       = request.user,
            template   = cd.get('template'),
            customer   = customer,
            to_email   = cd['to_email'],
            cc_emails  = ', '.join(cd.get('cc_emails', [])),
            bcc_emails = ', '.join(cd.get('bcc_emails', [])),
            subject    = cd['subject'],
            body_sent  = body,
            is_html    = cd.get('is_html', False),
            status     = email_status,
        )

        if email_status == 'Sent':
            parts = ['Email sent successfully']
            if cd['save_as_customer']:
                parts.append('recipient saved as customer')
            if cd.get('next_reminder'):
                parts.append('follow-up reminder set')
            messages.success(request, ' · '.join(parts) + '!')
        
        return redirect('email_log_list')

    return render(request, 'email_send.html', {'form': form})


@login_required
def email_log_list(request):
    logs = EmailLog.objects.filter(user=request.user).order_by('-sent_at')
    return render(request, 'email_log_list.html', {'email_logs': logs})


@login_required
def reminders_view(request):
    now = timezone.now()
    upcoming = Customer.objects.filter(
        user=request.user, next_reminder__gt=now).order_by('next_reminder')
    overdue = Customer.objects.filter(
        user=request.user, next_reminder__lt=now,
        next_reminder__isnull=False).order_by('next_reminder')
    return render(request, 'reminders.html', {'upcoming': upcoming, 'overdue': overdue})




# ========== AUTHENTICATION VIEWS ==========

def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('email_settings')  # Redirect to setup email
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})


# ========== PROFILE VIEWS ==========

@login_required
def profile_view(request):
    """View user profile"""
    profile = request.user.profile
    has_email_settings = hasattr(request.user, 'email_settings')
    
    context = {
        'profile': profile,
        'has_email_settings': has_email_settings,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})


@login_required
def toggle_theme(request):
    """Toggle dark mode"""
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'dark_mode': profile.dark_mode})


# ========== EMAIL SETTINGS VIEWS ==========

@login_required
def email_settings_view(request):
    """Configure SMTP settings"""
    try:
        settings_obj = request.user.email_settings
    except UserEmailSettings.DoesNotExist:
        settings_obj = None
    
    if request.method == 'POST':
        form = EmailSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.user = request.user
            
            # Encrypt and save password if provided
            password = form.cleaned_data.get('smtp_password')
            if password:
                settings.set_password(password)
            
            settings.save()
            messages.success(request, 'Email settings saved! Test your connection below.')
            return redirect('email_settings')
    else:
        form = EmailSettingsForm(instance=settings_obj)
    
    return render(request, 'email_settings.html', {
        'form': form,
        'settings': settings_obj,
    })


@login_required
def test_smtp_view(request):
    """Test SMTP connection"""
    if request.method == 'POST':
        try:
            settings = request.user.email_settings
            password = settings.get_password()
            
            success, error = test_smtp_connection(
                settings.smtp_host,
                settings.smtp_port,
                settings.smtp_email,
                password,
                settings.smtp_use_tls
            )
            
            if success:
                settings.is_verified = True
                settings.last_verified = timezone.now()
                settings.save()
                return JsonResponse({'success': True, 'message': 'Connection successful!'})
            else:
                return JsonResponse({'success': False, 'message': f'Connection failed: {error}'})
                
        except UserEmailSettings.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Please configure email settings first'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# ========== PWA VIEW ==========

def install_pwa_view(request):
    """PWA installation guide"""
    return render(request, 'install_pwa.html')