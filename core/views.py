from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Template, Customer, EmailLog
from .forms import TemplateForm, CustomerForm, QuickEmailSendForm


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
    data = list(Template.objects.filter(user=request.user).values('id', 'title', 'body'))
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


# ── Email Send ────────────────────────────────────────────────

@login_required
def email_send(request):
    form = QuickEmailSendForm(request.user, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data

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

        EmailLog.objects.create(
            user       = request.user,
            template   = cd.get('template'),
            customer   = customer,
            to_email   = cd['to_email'],
            cc_emails  = ', '.join(cd['cc_emails']),
            bcc_emails = ', '.join(cd['bcc_emails']),
            subject    = cd['subject'],
            body_sent  = body,
            status     = 'Sent',
        )

        parts = ['Email logged']
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