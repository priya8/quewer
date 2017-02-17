#from __future__ import unicode_literals
from django import forms
from books.models import regis
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from random import randint
import warnings
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django import forms
from django.forms.util import flatatt
from django.template import loader
from django.shortcuts import render
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_bytes
from django.utils.html import format_html, format_html_join
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.template.loader import get_template
import re
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, identify_hasher
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.validators import RegexValidator
from functools import partial
#from django.forms import extras


UNMASKED_DIGITS_TO_SHOW = 6

mask_password = lambda p: "%s%s" % (p[:UNMASKED_DIGITS_TO_SHOW], "*" * max(len(p) - UNMASKED_DIGITS_TO_SHOW, 0))

#datepicker
DateInput = partial(forms.DateInput,{'class':'datepicker'},)




class MyRegistrationForm(forms.ModelForm):
    error_css_class = 'error'
    error_messages = {
        'duplicate_username': _("A user with that email id already exists."),
        'password_mismatch': _("The two password fields didn't match."),
        'length_wrong': _("Minimum length of password must be 6"),
        'phone_error': _("Phone number is not valid"),
        'in_error': _("Invalid institute name"),
        'edu_error': _("Invalid Educational qualification"),
        'usr_error':_("Invalid username"),
        'date_error':_("Follow The ")
       }



    dob = forms.DateField(label=_("dob"),
                          widget=DateInput())



    password1 = forms.CharField(label=_("Password"),
    widget=forms.PasswordInput(attrs={'placeholder':'Password','required': 'true'}))
    password2 = forms.CharField(label=_("Password confirmation"),
    widget=forms.PasswordInput(attrs={'placeholder':'Re-Type Password','required': 'true'}))



    def clean(self):
        '''Required custom validation for the form.'''
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and len(password1) <= 6:
            self._errors['password1'] = [u'Minimum length of password must be 6']

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                self._errors['password1'] = [u'Passwords must match.']
                self._errors['password2'] = [u'Passwords must match.']

        return self.cleaned_data




    class Meta:
        model = regis
        fields = ('username',
                  'dob',
                  'email',
                  'password1',
                  'password2',
                  'mobile',
                  'education',
                  'institute')
        widgets = { 'username' :forms.TextInput(attrs={'placeholder': 'Name','required': 'true'}),
                   #'dob':forms.DateInput(attrs={'placeholder':'Date Of Birth','required':'true'}),
                   'email':forms.TextInput(attrs={'placeholder': 'Email ID','required': 'true'}),
                   'password1':forms.TextInput(attrs={'placeholder': 'Password','required': 'true'}),
                   'password2':forms.TextInput(attrs={'placeholder': 'Password','required': 'true'}),
                   'mobile':forms.TextInput(attrs={'placeholder': 'Mobile','required': 'true'}),
                   'education':forms.TextInput(attrs={'placeholder': 'Education','required': 'true'}),
                   'institute':forms.TextInput(attrs={'placeholder': 'Institute','required': 'true'})
        }


    def clean_email(self):
        email = self.cleaned_data['email']
        if regis.objects.filter(email=email).exists():
         raise forms.ValidationError("Email-Id already used")
        else:
         return email

    def clean_mobile(self):
        mobile=self.cleaned_data['mobile']
        try:
            if int(mobile) and len(mobile)!=10:
                raise forms.ValidationError(
                    self.error_messages['phone_error'],
                    code='phone_error',
                )
        except(ValueError,TypeError):
            raise forms.ValidationError(
                self.error_messages['phone_error'],
                code='phone_error',
            )
        return mobile

    def clean_institute(self):

        institute=self.cleaned_data['institute']
        if re.match('^[\.a-zA-Z]*$',institute)==None:
            raise forms.ValidationError(
                self.error_messages['in_error'],
                code='in_error',
            )
        return institute

    def clean_education(self):

        education=self.cleaned_data['education']
        if re.match('^[\.a-zA-Z]*$',education)==None:
            raise forms.ValidationError(
                self.error_messages['edu_error'],
                code='edu_error',
            )
        return education


    def clean_username(self):
        username = self.cleaned_data['username']
        if re.match('^[\.a-zA-Z ]*$', username) == None:

             raise forms.ValidationError(
                self.error_messages['usr_error'],
                 code='usr_error',
                 )
        return username


    def save(self, commit=True):

        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        rand_no=randint(000000000,999999999);
        user.uid=rand_no
        send_mail('Thank you for registering',get_template("email.html").render(
        Context({
            'username': user.username,
            'password': user.password1,
            'random_no': user.uid
        }) ),'lombada11@gmail.com',[user.email], fail_silently=False)


        if commit:
              user.save()

        return user
