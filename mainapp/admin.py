from django.contrib import admin
from .models import UserProfile, Transaction

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_limit', 'weekly_limit', 'balance')
    search_fields = ('user__username',)
    list_filter = ('daily_limit', 'weekly_limit')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'category', 'timestamp')
    search_fields = ('user__username', 'category')
    list_filter = ('category', 'timestamp')
    date_hierarchy = 'timestamp'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
