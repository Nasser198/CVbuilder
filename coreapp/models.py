from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# class UserInformation(models.Model):
#     email = models.EmailField()
#     otp = models.CharField(max_length=4,null=True)
    
# class WebsiteActions(models.Model):
#     name = models.CharField(max_length=50,null=True)
#     counter = models.IntegerField()

class UserInformation(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=4,null=True)
    request_count = models.PositiveIntegerField(default=0)  # new field
    request_sum = models.PositiveIntegerField(default=0)  # new field
    country = models.CharField(max_length=100, null=True)  # new field to store country of login/IP
    def add_request(self):
        self.request_count += 1
        self.save()
    
    @classmethod
    def update_request_sums(cls):
        """Update request_sum field for all users"""
        today = datetime.date.today()
        users = cls.objects.all()
        for user in users:
            request_count_today = user.websiteactions_set.filter(timestamp__date=today).count()
            user.request_sum = request_count_today
            user.save()

class WebsiteActions(models.Model):
    name = models.CharField(max_length=50,null=True)
    counter = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)  # new field to store the date and time of each request

class UserIP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    time = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)


