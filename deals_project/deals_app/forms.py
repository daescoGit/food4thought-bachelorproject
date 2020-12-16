from django import forms
from .models import Category

categories = Category.objects.filter()
categoriesExists = categories.exists()
categoryChoices = []

<<<<<<< HEAD
if categoriesExists:
    for category in categories:
        categoryChoices.append((category.pk, category.name))
=======
# for category in categories:
#     categoryChoices.append((category.pk, category.name))
>>>>>>> main


class DateInput(forms.DateInput):
    input_type = 'date'

class PostForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    new_price = forms.IntegerField()
    old_price = forms.IntegerField()
    category = forms.ChoiceField(choices=categoryChoices)
    address_line_1 = forms.CharField(max_length=200)
    address_line_2 = forms.CharField(max_length=200)
    postcode_code = forms.IntegerField()
    postcode_text = forms.CharField(max_length=200)
    expiration_date = forms.DateField(widget=DateInput)
    lng = forms.FloatField()
    lat = forms.FloatField()    

