from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    weekly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=5000)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Еда'),
        ('Transport', 'Транспорт'),
        ('Entertainment', 'Развлечения'),
        ('Utilities', 'Коммунальные услуги'),
        ('Other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} — {self.amount} {self.currency} [{self.category}]"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        indexes = [
            models.Index(fields=['timestamp'], name='idx_transaction_timestamp'),
            models.Index(fields=['category'], name='idx_transaction_category'),
            models.Index(fields=['user', 'timestamp'], name='idx_transaction_user_timestamp'),
        ]