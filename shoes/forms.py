from django import forms 

from .models import Shoe, SwapRequest

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


class SwapRequestForm(forms.ModelForm):
    class Meta: 
        model = SwapRequest
        fields = ['message', 'contact_details']
        labels = {
            'message':'Message to the owner',
            'contact_details': 'Contact details to share (optional)'
        }
        help_texts ={
            'contact_details': 'Email, phone or Instagram. Only the shoe owner will see this.'
        }
        widgets = {'message':forms.Textarea(attrs={'rows':3})}

class RespondForm(forms.ModelForm):
    class Meta:
        model = SwapRequest
        fields = ['owner_contact_details']
        labels = {'owner_contact_details': 'Your contact details (optional)'}
        help_texts = {
            'owner_contact_details': 'Only shared with the requester if you accept.',
        }