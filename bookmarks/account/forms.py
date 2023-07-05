from django import forms
# from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat your password')

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'email', 'password', 'password2', 'date_of_birth', 'photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)'})
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise forms.ValidationError('User with that email already exists')

        return email


# form to edit user info
class UserEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (DOB)'}),
            'photo': forms.ClearableFileInput()
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Profile.objects.exclude(id=self.instance.id).filter(email=email)

        if qs.exists():
            raise forms.ValidationError('User with that email already exists')

        return email
