from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from easybid.models import Profile, AuctionItem

MAX_UPLOAD_SIZE = 2500000

class AuctionItemPicForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ('product_image',)
        widgets = {'product_image':forms.FileInput(
        attrs={'class':'form-control', 'required': False, 'accept':"image/*" } 
         )}

    def clean_product_image(self):
        product_image = self.cleaned_data['product_image']
        if product_image:
            if not product_image or not hasattr(product_image, 'content_type'):
                raise forms.ValidationError('No image was uploaded')
            if not product_image.content_type or not product_image.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if product_image.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return product_image

class AuctionItemEditForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ('product_image', 'update_time')
        widgets = {'update_time': forms.HiddenInput(),
        'product_image':forms.FileInput(
        attrs={'class':'form-control', 'required': False, 'accept':"image/*" } 
         )}

    def clean_product_image(self):
        product_image = self.cleaned_data['product_image']
        print(product_image)
        print(product_image)
        if product_image:
            if not product_image or not hasattr(product_image, 'content_type'):
                raise forms.ValidationError('No image was uploaded')
            if not product_image.content_type or not product_image.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if product_image.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return product_image

class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_picture', 'update_time')
        widgets = {'update_time': forms.HiddenInput(),
        'profile_picture':forms.FileInput(
        attrs={'class':'form-control', 'required': False, 'accept':"image/*" } 
         )}

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data['profile_picture']
        if not profile_picture or not hasattr(profile_picture, 'content_type'):
            raise forms.ValidationError('No profile image was uploaded')
        if not profile_picture.content_type or not profile_picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if profile_picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return profile_picture

class RegisterForm(forms.Form):
    username              = forms.CharField(max_length=20)
    password              = forms.CharField(max_length = 200, label='Password', widget = forms.PasswordInput())
    confirm_password      = forms.CharField(max_length = 200, label='Confirm', widget = forms.PasswordInput())
    email                 = forms.CharField(max_length = 50, label='E-mail', widget = forms.EmailInput())
    first_name            = forms.CharField(max_length=20)
    last_name             = forms.CharField(max_length=20)
    
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class LoginForm(forms.Form):
    username     = forms.CharField(max_length=20)
    password     = forms.CharField(max_length = 200, label='Password', widget = forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
