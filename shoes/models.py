from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Shoe(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Like new'),
        ('good', 'Good'),
        ('worn', 'Well worn'),
    ]

    #later add brand choices dropdown, with hint to type brand if selecting other 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoes')
    brand = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    km_run = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.brand} {self.model_name} (size {self.size})'


class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='swap_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requester} -> {self.shoe} ({self.status})'