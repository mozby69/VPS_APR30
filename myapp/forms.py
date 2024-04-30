# myapp/forms.py
from django import forms
from datetime import date
from .models import DailyRecord

class DateSelectionForm(forms.Form):
    selected_date = forms.DateField(widget=forms.SelectDateWidget(), initial=date.today())


class ImportForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    

    class Meta:
        model = DailyRecord
        fields = ['date']


class SingleImport(forms.ModelForm):
    file = forms.FileField()