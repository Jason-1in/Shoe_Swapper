from django import forms 

from .models import Shoe

class ShoeForm(forms.ModelForm):
    class Meta: 
        model = Shoe
        fields = ['brand', 'brand_other','model_name', 'size_us', 'condition', 'km_run','asking_price','notes','is_available']
        labels = {
            'model_name':'Model',
            'km_run':'Distance run(km)',
            'is_available': 'Available to swap',
            'asking_price':'Asking price ($)',

        }
    widgets = {'notes':forms.Textarea(attrs={'rows':3})}