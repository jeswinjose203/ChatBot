# Create your models here.
from django.db import models

class Jeswin(models.Model):
    employee_name = models.CharField(max_length=255)

    def __str__(self):
        return self.employee_name
