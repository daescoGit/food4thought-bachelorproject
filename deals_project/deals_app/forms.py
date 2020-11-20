from django import forms
from .models import Category

categories = Category.objects.all()

choices = []

for category in categories:
    choices.append((category.pk, category.name))

class DateInput(forms.DateInput):
    input_type = 'date'

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    new_price = forms.IntegerField()
    old_price = forms.IntegerField()
    category = forms.ChoiceField(choices=choices)
    expiration_date = forms.DateField(widget=DateInput)