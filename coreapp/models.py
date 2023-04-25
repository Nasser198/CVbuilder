from django.db import models

# Create your models here.
class UserInformation(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=4,null=True)
    
class WebsiteActions(models.Model):
    name = models.CharField(max_length=50,null=True)
    counter = models.IntegerField()
