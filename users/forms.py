from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    # Extra field for password (write-only, not returned)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    # Field-level validation example
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    # Object-level validation (cross-field)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")
        return cleaned_data

    # Save method to handle password hashing (like create_user)
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # hash the password
        if commit:
            user.save()
        return user
