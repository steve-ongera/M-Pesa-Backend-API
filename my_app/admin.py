# my_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import locale
from django.db.models import Sum
from .models import User, Transaction

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass

class UserAdmin(BaseUserAdmin):
    # Display options for list view
    list_display = ('phone_number', 'full_name', 'formatted_balance', 'is_active', 
                    'is_staff', 'created_at', 'recent_transactions')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('phone_number', 'full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'user_stats')
    list_per_page = 25
    filter_horizontal = ('groups', 'user_permissions')
    
    # Fieldsets for detail view
    fieldsets = (
        ('Authentication', {
            'fields': ('phone_number', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name',)
        }),
        ('Account Information', {
            'fields': ('balance', 'user_stats', 'is_active')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add user form fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password1', 'password2'),
        }),
    )
    
    # Custom methods
    def formatted_balance(self, obj):
        """Format balance with currency symbol"""
        try:
            return locale.currency(float(obj.balance), grouping=True)
        except:
            return f"KSh {obj.balance:,.2f}"
    formatted_balance.short_description = 'Balance'
    formatted_balance.admin_order_field = 'balance'
    
    def recent_transactions(self, obj):
        """Show recent transaction count"""
        count = obj.sent_transactions.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        url = reverse('admin:my_app_transaction_changelist') + f'?sender__id__exact={obj.id}'
        return format_html('<a href="{}">{} transactions</a>', url, count)
    recent_transactions.short_description = 'Last 30 Days'
    
    def user_stats(self, obj):
        """Display user statistics"""
        total_sent = obj.sent_transactions.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_received = obj.received_transactions.filter(status='COMPLETED').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_transactions = obj.sent_transactions.count() + obj.received_transactions.count()
        
        try:
            sent_formatted = locale.currency(float(total_sent), grouping=True)
            received_formatted = locale.currency(float(total_received), grouping=True)
        except:
            sent_formatted = f"KSh {total_sent:,.2f}"
            received_formatted = f"KSh {total_received:,.2f}"
        
        html = f"""
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            <h4 style="margin-top: 0; color: #333;">User Statistics</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                <div style="background: white; padding: 10px; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Total Sent</div>
                    <div style="font-size: 16px; font-weight: bold; color: #dc3545;">
                        {sent_formatted}
                    </div>
                </div>
                <div style="background: white; padding: 10px; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Total Received</div>
                    <div style="font-size: 16px; font-weight: bold; color: #28a745;">
                        {received_formatted}
                    </div>
                </div>
            </div>
            <div style="margin-top: 10px; background: white; padding: 10px; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 12px; color: #666;">Total Transactions</div>
                <div style="font-size: 16px; font-weight: bold; color: #007bff;">{total_transactions}</div>
            </div>
        </div>
        """
        return format_html(html)
    user_stats.short_description = 'Statistics'


class TransactionAdmin(admin.ModelAdmin):
    # Display options
    list_display = ('transaction_code', 'formatted_amount', 'transaction_type', 
                    'status_badge', 'sender_link', 'receiver_link', 'created_at')
    list_filter = ('status', 'transaction_type', 'created_at')
    search_fields = ('transaction_code', 'sender__phone_number', 
                    'receiver__phone_number', 'description')
    readonly_fields = ('transaction_code', 'created_at', 'updated_at', 
                      'transaction_details')
    list_select_related = ('sender', 'receiver')
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    # Fieldsets for detail view
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_code', 'transaction_type', 'status', 'amount')
        }),
        ('Parties', {
            'fields': ('sender', 'receiver')
        }),
        ('Details', {
            'fields': ('description', 'transaction_details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods
    def formatted_amount(self, obj):
        """Format amount with currency symbol"""
        try:
            amount = locale.currency(float(obj.amount), grouping=True)
        except:
            amount = f"KSh {obj.amount:,.2f}"
        
        color = '#28a745' if obj.transaction_type in ['DEPOSIT'] else '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, amount)
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'PENDING': 'warning',
            'COMPLETED': 'success',
            'FAILED': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        badge_styles = {
            'warning': 'background: #ffc107; color: #000;',
            'success': 'background: #28a745; color: #fff;',
            'danger': 'background: #dc3545; color: #fff;',
            'secondary': 'background: #6c757d; color: #fff;'
        }
        style = badge_styles.get(color, '')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; {}">{}</span>', 
            style, obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def sender_link(self, obj):
        """Create clickable link to sender"""
        if obj.sender:
            url = reverse('admin:my_app_user_change', args=[obj.sender.id])
            return format_html('<a href="{}">{}</a>', url, obj.sender.phone_number)
        return '-'
    sender_link.short_description = 'Sender'
    
    def receiver_link(self, obj):
        """Create clickable link to receiver"""
        if obj.receiver:
            url = reverse('admin:my_app_user_change', args=[obj.receiver.id])
            return format_html('<a href="{}">{}</a>', url, obj.receiver.phone_number)
        return '-'
    receiver_link.short_description = 'Receiver'
    
    def transaction_details(self, obj):
        """Display transaction details"""
        html = f"""
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px; margin-top: 10px;">
            <h4 style="margin-top: 0; color: #333;">Transaction Timeline</h4>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 100px; font-size: 12px; color: #666;">Created:</div>
                <div>{obj.created_at.strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 100px; font-size: 12px; color: #666;">Last Updated:</div>
                <div>{obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
        </div>
        """
        return format_html(html)
    transaction_details.short_description = 'Details'
    
    # Custom actions
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected transactions as completed"""
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} transaction(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected transactions as COMPLETED"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected transactions as failed"""
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} transaction(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected transactions as FAILED"


# Register models
admin.site.register(User, UserAdmin)
admin.site.register(Transaction, TransactionAdmin)

# Customize admin site
admin.site.site_header = 'M-Pesa Mobile Money Administration'
admin.site.site_title = 'M-Pesa Admin'
admin.site.index_title = 'Welcome to M-Pesa Admin Dashboard'