from django.db import models

class TrashBin(models.Model):
    sensor_id = models.CharField(max_length=50, unique=True)
    mahalla = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=[('FILLED', 'To‘ldi'), ('EMPTY', 'Bo‘sh')])
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sensor_id} - {self.status}"