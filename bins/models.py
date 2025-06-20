from django.db import models
from django.contrib.auth.models import User
import secrets

class Dispatcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_token = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class TrashBin(models.Model):
    dispatcher = models.ForeignKey(Dispatcher, on_delete=models.CASCADE, related_name='bins')
    sensor_id = models.CharField(max_length=50, unique=True)
    mahalla = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=[('FILLED', 'To‘ldi'), ('EMPTY', 'Bo‘sh')])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sensor_id} - {self.status}"


class BinStatusHistory(models.Model):
    trash_bin = models.ForeignKey(TrashBin, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trash_bin.sensor_id} - {self.status} at {self.timestamp}"
