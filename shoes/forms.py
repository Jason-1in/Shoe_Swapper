from django import forms 
from .models import Shoe, SwapRequest, Postcode
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class ShoeForm(forms.ModelForm):
    class Meta: 
        model = Shoe
        fields = ['brand', 'brand_other','model_name', 'size_us', 'condition', 'km_run','postcode','suburb','asking_price','notes','is_available' ]
        labels = {
            'model_name':'Model',
            'km_run':'Distance run(km)',
            'is_available': 'Available to swap',
            'asking_price':'Asking price ($)',
            'postcode': 'Postcode',
            'suburb': 'Suburb',
        }
    widgets = {'notes':forms.Textarea(attrs={'rows':3})}


    def clean_postcode(self):
        code = self.cleaned_data['postcode'].strip()
        if not Postcode.objects.filter(code=code).exists():
            raise ValidationError("We don't recognise that postcode")
        return code

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

class BrowseFilterForm(forms.Form):
    brand = forms.ChoiceField(required=False)
    model_name = forms.CharField(label='Shoe model', required=False, max_length=100)
    size_min = forms.DecimalField(
        label='Size from (US)', required=False, min_value=3, max_value=18,
        decimal_places=1, widget=forms.NumberInput(attrs={'step': '0.5'}),
    )
    size_max = forms.DecimalField(
        label='Size to (US)', required=False, min_value=3, max_value=18,
        decimal_places=1, widget=forms.NumberInput(attrs={'step': '0.5'}),
    )
    postcode = forms.CharField(
        label='Your postcode', required=False, max_length=4,
        validators=[RegexValidator(r'^\d{4}$', 'Enter a 4-digit postcode.')],
    )
    radius = forms.ChoiceField(
        label='Distance', required=False,
        choices=[('', 'Any distance'), ('10', 'Within 10 km'),
                 ('25', 'Within 25 km'), ('50', 'Within 50 km')],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brand_choices = Shoe._meta.get_field('brand').choices
        self.fields['brand'].choices = [('', 'Any brand')] + list(brand_choices)

    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get('size_min'), cleaned.get('size_max')
        if low is not None and high is not None and low > high:
            raise ValidationError('"Size from" can\'t be bigger than "Size to".')
        if cleaned.get('radius') and not cleaned.get('postcode'):
            self.add_error('postcode', 'Enter your postcode to filter by distance.')
        return cleaned