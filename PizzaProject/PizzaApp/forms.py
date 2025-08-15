from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm,UsernameField,PasswordChangeForm
from django.contrib.auth.models import User

from .models import Customer

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model=Customer
        fields=['name','locality','city','mobile','pincode']
        widgets={
            'name':forms.TextInput(attrs={'class':'from-control'}),
            'locality':forms.TextInput(attrs={'class':'from-control'}),
            'city':forms.TextInput(attrs={'class':'from-control'}),
            'mobile':forms.NumberInput(attrs={'class':'from-control'}),
            'pincode':forms.NumberInput(attrs={'class':'from-control'}),
        }