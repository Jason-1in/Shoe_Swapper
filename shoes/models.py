from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError


# Create your models here.
class Shoe(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Like new'),
        ('good', 'Good'),
        ('worn', 'Well worn'),
    ]
    
    BRAND_CHOICES = [
    ('nike', 'Nike'),
    ('adidas', 'Adidas'),
    ('asics', 'ASICS'),
    ('brooks', 'Brooks'),
    ('hoka', 'HOKA'),
    ('mizuno', 'Mizuno'),
    ('new_balance', 'New Balance'),
    ('on', 'On'),
    ('puma', 'Puma'),
    ('saucony', 'Saucony'),
    ('other', 'Other'),
    ]

    #later add brand choices dropdown, with hint to type brand if selecting other 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoes')
    brand = models.CharField(max_length=20, choices=BRAND_CHOICES)
    brand_other = models.CharField(
        "Other brand",
        max_length=100,
        blank=True,
        default='',
        help_text="Only needed if you chose Other",
        )
    model_name = models.CharField(max_length=100)
    # size = models.CharField(max_length=10)
    size_us = models.DecimalField(
        "Size (US)",
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(3), MaxValueValidator(18)],
        help_text="e.g. 9 or 9.5", #help text helps give clues re. input
    )
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    km_run = models.PositiveIntegerField(default=0)
    suburb = models.CharField(max_length=100, help_text="Suburb for pick up, don't include your actual address!")
    postcode = models.CharField(
        max_length =4, validators =[RegexValidator(r'^\d{4}$')] #ensure the postcode is 4 numerical characters
    )
    asking_price = models.DecimalField(
        "Asking price ($)",
        max_digits = 6,
        decimal_places = 2,
        null=True,
        blank=True,
        validators =[MinValueValidator(0)],
        help_text = "Leave blank for swap only",
    )
    photo = models.ImageField(upload_to='shoes/',blank =True)
    notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def clean(self):
        #to ensure brand is either selected from drop down or other
        if self.brand == 'other' and not self.brand_other.strip():
            raise ValidationError({'brand_other': 'Please enter the brand name.'})
        if self.brand != 'other':
            self.brand_other = ''
    @property
    def brand_name(self):
        """The brand to show people: the typed one if Other, else the dropdown label."""
        if self.brand == 'other':
            return self.brand_other
        return self.get_brand_display()

    def __str__(self):
        return f'{self.brand_name} {self.model_name} (US {self.size_us})'


class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='swap_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests')
    message = models.TextField(blank=True)
    contact_details = models.CharField("Contact details", max_length=200, blank=True)
    owner_contact_details = models.CharField("Owner's contact details", max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requester} -> {self.shoe} ({self.status})'

class Postcode(models.Model):
    """One row per Australian postcode with central point for distance calculation"""
    code = models.CharField(max_length=4, unique = True)
    state = models.CharField(max_length=3, blank =True)
    latitude=models.FloatField() 
    longitude=models.FloatField() 
    suburbs = models.CharField(max_length =200,blank = True)


    def __str__(self):
        return f'{self.code} {self.suburbs}'