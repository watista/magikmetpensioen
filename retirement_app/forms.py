# retirement_app/forms.py
from django import forms

class BirthDateForm(forms.Form):
    birth_date = forms.CharField(
        label="Geboortedatum (dd-mm-yyyy)",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "dd-mm-yyyy",
            "inputmode": "numeric",
            "maxlength": "10",
            "id": "birthDateInput",
            "autocomplete": "off",
        })
    )
