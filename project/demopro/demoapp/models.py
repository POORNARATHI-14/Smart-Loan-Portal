from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    age = models.CharField(max_length=15, blank=True, null=True)
    per_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

class LoanApplication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    applicant_income = models.FloatField()
    coapplicant_income = models.FloatField()
    loan_amount = models.FloatField()
    loan_amount_term = models.FloatField(default=360)   
    credit_history = models.FloatField()

    property_area = models.CharField(max_length=50)
    education = models.CharField(max_length=50)
    employment = models.CharField(max_length=50)

    prediction = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.prediction}"
