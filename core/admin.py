from django.contrib import admin
from .models import Template, Customer, EmailLog


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'body')
    date_hierarchy = 'created_at'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'user', 'last_contact', 'next_reminder')
    list_filter = ('status', 'user', 'last_contact')
    search_fields = ('name', 'email')
    date_hierarchy = 'last_contact'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'template', 'user', 'sent_at', 'status')
    list_filter = ('status', 'user', 'sent_at')
    search_fields = ('customer__email', 'customer__name')
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at',)