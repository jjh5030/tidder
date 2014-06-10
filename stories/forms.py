from django.forms import ModelForm
from django import forms

from stories.models import Story, UserProfile, Comment
from django.contrib.auth.models import User


class StoryForm(ModelForm):
	title = forms.CharField(max_length=200, help_text="Please Enter The Title Of The Page.")
	url = forms.URLField(max_length=200, help_text="Please Enter The URL Of The Page.", required=False)
	description = forms.Textarea()

	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')
		
		# If url is not empty and doesn't start with 'http://' add 'http://' to the beginning
		if url and not url.startswith('http://'):
			url = 'http://' + url
			
			cleaned_data['url'] = url
		return cleaned_data

	class Meta:
		model = Story
		exclude = ('points', 'moderator','voters')

class UserForm(forms.ModelForm):
	username = forms.CharField(help_text="Please enter a username.")
	email = forms.CharField(help_text="Please enter your email address.")
	password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password")

	class Meta:
		model = User
		fields = ['username','email','password']

class UserProfileForm(forms.ModelForm):
	first_name = forms.CharField(help_text="Please enter your first name.", required=False)
	last_name = forms.CharField(help_text="Please enter your last name.", required=False)
	website = forms.URLField(help_text="Please enter your website.", required=False)
	picture = forms.ImageField(help_text="Select a profile image to upload.", required=False)

	class Meta:
		model = UserProfile
		fields = ['first_name', 'last_name', 'website', 'picture']

class CommentForm(forms.ModelForm):
	#Hidden value to get a child's parent
	parent = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'parent'}), required=False)
	
	class Meta:
		model = Comment
		fields = ('content',)

class ContactForm(forms.Form):
	name = forms.CharField(required=True)
	sender_email = forms.EmailField(required=True)
	subject = forms.CharField(required=True)
	message = forms.CharField(required=True)
	cc_myself = forms.BooleanField(required=False)