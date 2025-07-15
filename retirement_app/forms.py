# retirement_app/forms.py
from django import forms

class BirthDateForm(forms.Form):
    birth_date = forms.CharField(
        required=True,
        label="Geboortedatum (dd-mm-jjjj)",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "01-01-1990",
            "inputmode": "numeric",
            "maxlength": "10",
            "id": "birthDateInput",
            "autocomplete": "off",
        })
    )
