from django import forms
from . models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class ItemForm(forms.ModelForm):
    class Meta:
        model=Item
        fields='__all__'

class ItemUploadFileForm(forms.Form):
    file = forms.FileField()

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()

class ItemEditForm(forms.Form):
    finalized_quantity = forms.IntegerField(required=False)  # Finalized quantity field for each item
    row_selected = forms.BooleanField(required=False)  # Checkbox to select the ro

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['finalized_quantity']  # Only include the field you want to edit

class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['finalized_quantity']  # Only include the finalized_quantity field

    
class AccountCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['email', 'username', 'fname', 'lname']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("pass1")
        password2 = self.cleaned_data.get("pass2")
        
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2
    



class UserPermissionsForm(forms.Form):
    #users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple, label="Select Users")
    
    # Permissions for each user (can be checkboxes)
    read_only = forms.BooleanField(required=False, label="Read Only")
    edit = forms.BooleanField(required=False, label="Edit")
    view_page = forms.BooleanField(required=False, label="View Page")